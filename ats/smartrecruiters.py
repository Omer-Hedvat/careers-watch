"""
SmartRecruiters careers puller.

The public API at api.smartrecruiters.com/v1/companies/{slug}/postings is
effectively gated for anonymous access (always returns 0).  The career site
at careers.smartrecruiters.com/{slug} is server-side rendered — job groups
(by location) and individual job links are in the initial HTML.

Pagination: the first page is the SSR render; additional pages are fetched
from /{slug}/api/groups?page=N which also returns HTML fragments.

apply_url is the jobs.smartrecruiters.com URL embedded in every anchor.
Description is empty — the listing HTML has none; titles are descriptive
enough for scoring and description can be added later via a detail fetch.
"""
import re
import sys

import httpx

try:
    from ats.utils import HEADERS
except ModuleNotFoundError:
    import os as _os
    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from ats.utils import HEADERS

_CAREER_BASE = "https://careers.smartrecruiters.com"

# Matches: aria-label="Job Title - REF1234" on the job anchor
_JOB_ANCHOR_RE = re.compile(
    r'<a[^>]+href=["\']([^"\']+/\d+-[^"\']+)["\'][^>]+aria-label=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
# Location heading for each opening group
_LOCATION_RE = re.compile(
    r'<h3[^>]+class=["\'][^"\']*opening-title[^"\']*["\'][^>]*>([^<]+)</h3>',
    re.IGNORECASE,
)
_DATA_PAGES_RE = re.compile(r'data-groups-pages=["\'](\d+)["\']')


def _parse_jobs_from_html(html: str) -> list[dict]:
    """
    Extract jobs from a SmartRecruiters career-site HTML page or fragment.

    Groups jobs by location: the `.opening-title` heading before each group
    of `.js-job-ad-link` anchors provides the city/country for those jobs.
    """
    results = []

    # Split on opening-section boundaries to pair each location with its jobs
    # Sections are <section ... class="...opening...js-group">...</section>
    section_blocks = re.split(
        r'<section[^>]+class=["\'][^"\']*(?:opening|js-group)[^"\']*["\']',
        html,
        flags=re.IGNORECASE,
    )

    for block in section_blocks[1:]:  # skip preamble before first section
        # Extract the location from the first opening-title in this block
        loc_m = _LOCATION_RE.search(block)
        location = loc_m.group(1).strip() if loc_m else ""

        # Extract all job anchors within this block
        for url, label in _JOB_ANCHOR_RE.findall(block):
            # aria-label format: "Job Title - REF12345X" — strip REF suffix
            title = re.sub(r"\s*-\s*REF[A-Z0-9]+\s*$", "", label).strip()
            results.append(
                {
                    "title": title,
                    "location": location,
                    "description": "",
                    "apply_url": url,
                }
            )

    return results


def fetch_positions(company_slug: str) -> list[dict]:
    """
    Fetch open positions from a SmartRecruiters career site.
    Returns list of normalized dicts: {title, location, description, apply_url}.
    """
    base_url = f"{_CAREER_BASE}/{company_slug}"
    try:
        resp = httpx.get(base_url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"    SmartRecruiters fetch error for {company_slug}: {e}")
        return []

    results = _parse_jobs_from_html(html)

    # Determine total page count from data-groups-pages attribute
    m = _DATA_PAGES_RE.search(html)
    total_pages = int(m.group(1)) if m else 1

    # Fetch remaining pages
    for page in range(1, total_pages):
        page_url = f"{base_url}/api/groups?page={page}"
        try:
            pr = httpx.get(page_url, headers=HEADERS, timeout=15, follow_redirects=True)
            pr.raise_for_status()
            results.extend(_parse_jobs_from_html(pr.text))
        except Exception as e:
            print(f"    SmartRecruiters page {page} error for {company_slug}: {e}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ats/smartrecruiters.py <company_slug>")
        print("  e.g. uv run ats/smartrecruiters.py Sutherland")
        sys.exit(1)

    slug = sys.argv[1]
    print(f"Fetching SmartRecruiters postings for: {slug}")
    jobs = fetch_positions(slug)
    print(f"Found {len(jobs)} job(s)")
    for i, job in enumerate(jobs[:8]):
        print(f"  [{i + 1}] {job['title'][:60]} - {job['location']}")
        print(f"       {job['apply_url'][:80]}")
    if len(jobs) > 8:
        print(f"  ... and {len(jobs) - 8} more")
