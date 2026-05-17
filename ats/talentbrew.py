"""
TalentBrew (Radancy) careers platform puller.

TalentBrew is a hosted careers platform used by large enterprises (Intuit,
many Fortune 500s). It exposes a JSON-wrapped HTML search endpoint at
/search-jobs/results that supports facet-based filtering (FacetType=2 is
country) and pagination via CurrentPage.

The endpoint returns {"results": "<HTML>"} where the HTML embeds a
<section id="search-results"> with data-total-pages / data-current-page
attributes and a <ul class="search-list"> of job cards. Each card is an
<li data-intuit-jobid="..."> containing <a href="/job/..."> with an <h2>
title and a <span class="job-location"> location.

Usage: uv run ats/talentbrew.py <host> [facet]
  e.g. uv run ats/talentbrew.py jobs.intuit.com israel
"""

import re
import sys

import httpx

try:
    from ats.utils import HEADERS
except ModuleNotFoundError:
    # Allow running as a script from the repo root: uv run ats/talentbrew.py <host>
    import os as _os

    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from ats.utils import HEADERS

SEARCH_SECTION_RE = re.compile(
    r'<section\s+id="search-results"[^>]*'
    r'data-total-pages="(\d+)"[^>]*'
    r'data-current-page="(\d+)"',
    re.IGNORECASE | re.DOTALL,
)

JOB_CARD_RE = re.compile(
    r'<li\b[^>]*\bdata-[-a-z]*jobid="[^"]+"[^>]*>(.*?)</li>',
    re.IGNORECASE | re.DOTALL,
)

HREF_RE = re.compile(r'<a\s+[^>]*href="([^"]+)"', re.IGNORECASE)
TITLE_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)
LOCATION_RE = re.compile(
    r'<span[^>]*class="job-location"[^>]*>(.*?)</span>',
    re.IGNORECASE | re.DOTALL,
)


def _clean(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).strip()


def fetch_positions(host: str, facet: str = "israel") -> list[dict]:
    """
    Fetch open positions from a TalentBrew careers site.
    Returns list of normalized dicts: {title, location, description, apply_url}.
    Returns whatever was accumulated on partial failure.
    """
    base = f"https://{host}"
    url = f"{base}/search-jobs/results"
    results: list[dict] = []

    page = 1
    total_pages = 1
    while page <= total_pages:
        params = {
            "ActiveFacetID": 0,
            "CurrentPage": page,
            "RecordsPerPage": 100,
            "Distance": 50,
            "RadiusUnitType": 0,
            "Keywords": "",
            "Latitude": "",
            "Longitude": "",
            "ShowRadius": "False",
            "IsPagination": "False",
            "CustomFacetName": "",
            "FacetTerm": facet,
            "FacetType": 2,
            "SearchResultsModuleName": "Search Results",
        }
        try:
            resp = httpx.get(
                url,
                params=params,
                headers=HEADERS,
                follow_redirects=True,
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"    TalentBrew fetch error for {host} page {page}: {e}")
            return results

        html = data.get("results", "") if isinstance(data, dict) else ""
        if not html:
            break

        m = SEARCH_SECTION_RE.search(html)
        if m:
            total_pages = int(m.group(1))

        cards = JOB_CARD_RE.findall(html)
        if not cards:
            break

        for card in cards:
            href_m = HREF_RE.search(card)
            title_m = TITLE_RE.search(card)
            loc_m = LOCATION_RE.search(card)
            if not href_m or not title_m:
                continue
            href = href_m.group(1)
            apply_url = href if href.startswith("http") else base + href
            results.append(
                {
                    "title": _clean(title_m.group(1)),
                    "location": _clean(loc_m.group(1)) if loc_m else "",
                    "description": "",
                    "apply_url": apply_url,
                }
            )

        page += 1

    print(f"    TalentBrew {host} ({facet}): {len(results)} jobs across {total_pages} page(s)")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ats/talentbrew.py <host> [facet]")
        print("  e.g. uv run ats/talentbrew.py jobs.intuit.com israel")
        sys.exit(1)

    host = sys.argv[1]
    facet = sys.argv[2] if len(sys.argv) > 2 else "israel"
    positions = fetch_positions(host, facet)
    print(f"\n{len(positions)} positions from {host} ({facet}):")
    for p in positions:
        print(f"  {p['title']} - {p['location']}")
        print(f"    {p['apply_url']}")
