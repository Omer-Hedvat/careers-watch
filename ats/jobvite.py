import re
import sys

import httpx

try:
    from ats.utils import HEADERS, strip_html as _strip_html
except ModuleNotFoundError:
    import os as _os

    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from ats.utils import HEADERS, strip_html as _strip_html


# Jobvite public job-board pages embed each job as an <li class="row"> block. The
# documented /api/jobs?company=<slug> JSON endpoint redirects to a help page in
# practice, so we parse the HTML directly.
_LI_RE = re.compile(r'<li class="row">(.*?)</li>', re.DOTALL | re.IGNORECASE)
_HREF_RE = re.compile(r'href="(/[^"/]+/job/[^"]+)"', re.IGNORECASE)
_TITLE_RE = re.compile(r'<div class="jv-job-list-name">\s*(.+?)\s*</div>', re.DOTALL | re.IGNORECASE)
_LOC_BLOCK_RE = re.compile(
    r'<div class="ml-auto jv-job-list-location">(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)
_SPAN_RE = re.compile(r'<span>\s*(.+?)\s*</span>', re.DOTALL | re.IGNORECASE)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", _strip_html(text)).strip()


def fetch_positions(company_slug: str) -> list[dict]:
    """
    Fetch open positions from a Jobvite-hosted public job board.
    Returns list of normalized job dicts: {title, location, description, apply_url}.
    Returns [] on error.
    """
    url = f"https://jobs.jobvite.com/{company_slug}"
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15, headers=HEADERS)
        resp.raise_for_status()
    except Exception as e:
        print(f"    Jobvite error for {company_slug}: {e}")
        return []

    html = resp.text
    results = []
    seen_paths: set[str] = set()

    for li in _LI_RE.finditer(html):
        block = li.group(1)
        href_m = _HREF_RE.search(block)
        title_m = _TITLE_RE.search(block)
        if not href_m or not title_m:
            continue

        path = href_m.group(1).split("?", 1)[0]
        if path in seen_paths:
            continue
        seen_paths.add(path)

        title = _clean(title_m.group(1))

        # Jobvite renders <span>category</span><span>location</span> inside the
        # location block. The trailing span is the actual location; earlier spans
        # are department facets. Fall back to joining all spans if there's only one.
        location = ""
        loc_block = _LOC_BLOCK_RE.search(block)
        if loc_block:
            spans = [_clean(s.group(1)) for s in _SPAN_RE.finditer(loc_block.group(1))]
            spans = [s for s in spans if s]
            if len(spans) >= 2:
                location = spans[-1]
            elif spans:
                location = spans[0]

        results.append(
            {
                "title": title,
                "location": location,
                "description": "",
                "apply_url": f"https://jobs.jobvite.com{path}",
            }
        )

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ats/jobvite.py <company_slug>")
        sys.exit(1)

    slug = sys.argv[1]
    print(f"Fetching Jobvite postings for: {slug}")
    jobs = fetch_positions(slug)
    print(f"Found {len(jobs)} job(s)")
    for i, job in enumerate(jobs[:5]):
        print(f"  [{i + 1}] {job['title']} - {job['location']}")
        print(f"       {job['apply_url']}")
    if len(jobs) > 5:
        print(f"  ... and {len(jobs) - 5} more")
