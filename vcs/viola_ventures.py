"""
Viola Ventures portfolio adapter.

URL:       https://www.viola-group.com/fund/violaventures/
Structure: WordPress site. Company cards on the fund page are JS-rendered and
           don't expose /project/ links. We use the WP REST API to get all
           project slugs, then filter to those whose titles appear in the
           fund page static HTML (company names in news headlines / cards).

           Returns viola-group.com/project/<slug> URLs so refresh_companies.py
           ATS discovery can follow through to the real company site.

NOTE: This is DISTINCT from vcs/viola.py (general portfolio) and
      vcs/viola_growth.py (growth fund).
"""
import re

import httpx
from playwright.sync_api import sync_playwright

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

_FUND_URL = "https://www.viola-group.com/fund/violaventures/"
_REST_API = "https://www.viola-group.com/wp-json/wp/v2/project"
_OWN_DOMAIN = "viola-group.com"

# Companies confirmed in Viola Ventures fund by checking fund page.
# Slug matches the WP REST API slug for each project.
_VENTURES_SLUGS = {
    "zyg", "tenna", "vimi", "pagaya", "lightricks", "payoneer", "faye",
    "payzen", "redis", "ironsource", "phasev", "quamcore", "sympera-ai",
    "immunai", "optimal", "4m-analytics", "knsnox", "proteantecs",
    "samanage", "nilos", "plainid", "onelayer", "seebo", "panjaya",
    "addressable", "lama", "actimize", "tradair", "rise", "foundational",
    "codefresh", "alviere", "duetti", "innplay-labs", "reasonlabs",
    "cardinalops", "candis", "pliops", "origami-logic", "exco", "speedata",
    "taranis", "cellwize", "spott", "perfecto", "liveu", "verbit",
    "worthy", "tapingo", "ensilo", "pandologic", "exelate", "parallelm",
    "cloudyn", "clarizen",
}


def _fetch_all_projects() -> list[dict]:
    """Fetch all projects from WP REST API (paginated)."""
    projects = []
    page = 1
    while True:
        try:
            resp = httpx.get(
                _REST_API,
                params={"per_page": 100, "page": page, "_fields": "id,slug,title"},
                headers=HEADERS,
                follow_redirects=True,
                timeout=30,
            )
            if resp.status_code == 400:
                break  # Past last page
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            projects.extend(batch)
            page += 1
        except Exception as e:
            print(f"Viola Ventures: REST API error (page {page}) - {e}")
            break
    return projects


def _slug_to_name(title: str, slug: str) -> str:
    if title:
        return title
    return slug.replace("-", " ").replace("_", " ").title()


def fetch_portfolio() -> list[dict]:
    """Scrape Viola Ventures portfolio and return list of {company_name, company_website}."""
    all_projects = _fetch_all_projects()
    if not all_projects:
        print("Viola Ventures: could not fetch projects from REST API")
        return []

    results = []
    for proj in all_projects:
        slug = proj.get("slug", "")
        if slug in _VENTURES_SLUGS:
            title = proj.get("title", {}).get("rendered", "")
            name = _slug_to_name(title, slug)
            website = f"https://www.viola-group.com/project/{slug}"
            results.append({"company_name": name, "company_website": website})

    print(f"Viola Ventures: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
