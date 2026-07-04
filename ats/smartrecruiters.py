"""
SmartRecruiters careers puller.

The career site at careers.smartrecruiters.com/{slug} used to be server-side
rendered with job listings in the initial HTML; it now 302-redirects to a
client-rendered SPA at jobs.smartrecruiters.com with no jobs in the initial
payload, so HTML scraping no longer works (see BUG_SMARTRECRUITERS_ROUTING).

The public API at api.smartrecruiters.com/v1/companies/{slug}/postings is
NOT gated for anonymous access (verified against Sutherland: 357 postings,
Visa: 2 postings) - only paginated JSON, no per-job detail fetch needed.

apply_url is constructed as jobs.smartrecruiters.com/{slug}/{posting_id} -
verified this bare-id form (no human-readable slug suffix) resolves as a
working link without an extra detail request per job.

Description is empty - the list endpoint doesn't include it; a detail fetch
per job would be needed for that and isn't worth the request volume.
"""
import sys

import httpx

try:
    from ats.utils import HEADERS
except ModuleNotFoundError:
    import os as _os
    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from ats.utils import HEADERS

_API_BASE = "https://api.smartrecruiters.com/v1/companies"
_APPLY_BASE = "https://jobs.smartrecruiters.com"
_PAGE_SIZE = 100


def fetch_positions(company_slug: str) -> list[dict]:
    """
    Fetch open positions from the SmartRecruiters public postings API.
    Returns list of normalized dicts: {title, location, description, apply_url}.
    """
    results = []
    offset = 0

    while True:
        try:
            resp = httpx.get(
                f"{_API_BASE}/{company_slug}/postings",
                headers=HEADERS,
                params={"limit": _PAGE_SIZE, "offset": offset},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"    SmartRecruiters fetch error for {company_slug}: {e}")
            break

        postings = data.get("content", [])
        for p in postings:
            loc = p.get("location", {}) or {}
            location = loc.get("fullLocation") or ", ".join(
                filter(None, [loc.get("city"), loc.get("country")])
            )
            results.append(
                {
                    "title": p.get("name", ""),
                    "location": location,
                    "description": "",
                    "apply_url": f"{_APPLY_BASE}/{company_slug}/{p.get('id', '')}",
                }
            )

        total = data.get("totalFound", 0)
        offset += _PAGE_SIZE
        if offset >= total or not postings:
            break

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
