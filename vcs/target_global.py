"""
Target Global portfolio adapter.

URL:       https://www.targetglobal.vc/portfolio/
Structure: Static HTML (Webflow site). Company website links are embedded
           directly in the HTML as <a href="..."> tags. No JS rendering needed.
           ~98 portfolio companies globally; includes Israel-based companies.
           No region filtering is applied here - collect_jobs.py handles
           location filtering via location_filter in each company entry.
"""
import re
from urllib.parse import urlparse

import httpx

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

_PORTFOLIO_URL = "https://www.targetglobal.vc/portfolio/"
_OWN_DOMAIN = "targetglobal.vc"

_SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
}
_SKIP_DOMAINS = {
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com", "prnewswire.com",
    "businesswire.com", "globenewswire.com", "wired.com",
    # CDN and infrastructure
    "cdn.prod.website-files.com", "fonts.googleapis.com", "fonts.gstatic.com",
    # Target Global own domains
    "portal.targetglobal.vc", "targetglobal.medium.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    blocked = _SOCIAL_DOMAINS | _SKIP_DOMAINS | {_OWN_DOMAIN}
    return any(clean == s or clean.endswith("." + s) for s in blocked)


def _name_from_domain(netloc: str) -> str:
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def fetch_portfolio() -> list[dict]:
    """Scrape Target Global portfolio and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(_PORTFOLIO_URL, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Target Global: error fetching portfolio - {e}")
        return []

    seen: set[str] = set()
    results: list[dict] = []

    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        href = m.group(1)
        parsed = urlparse(href)
        netloc = parsed.netloc
        if not netloc or _is_filtered(netloc):
            continue
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(path_parts) > 2:
            continue

        base = f"{parsed.scheme}://{parsed.netloc}"
        if base in seen:
            continue
        seen.add(base)

        name = _name_from_domain(netloc)
        results.append({"company_name": name, "company_website": base})

    print(f"Target Global: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
