"""
Greenfield Partners portfolio adapter.

URL:       https://www.greenfield-growth.com/portfolio
Structure: Static HTML. Company cards contain external anchor tags.
           Strong cyber/AI infra focus (Silverfort, Torq, Coralogix).
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

_INDEX_URL = "https://www.greenfield-growth.com/portfolio"
_OWN_DOMAIN = "greenfield-growth.com"

_SKIP_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com",
    "google.com", "googleapis.com", "gstatic.com", "googletagmanager.com",
    "cloudflare.com", "cdnjs.cloudflare.com",
    "fonts.googleapis.com", "fonts.gstatic.com",
    "doubleclick.net", "typekit.net", "w3.org",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    blocked = _SKIP_DOMAINS | {_OWN_DOMAIN}
    return any(clean == s or clean.endswith("." + s) for s in blocked)


def fetch_portfolio() -> list[dict]:
    """Scrape Greenfield Partners portfolio and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(_INDEX_URL, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Greenfield: error fetching portfolio - {e}")
        return []

    seen: set[str] = set()
    results: list[dict] = []

    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        href = m.group(1).split("?")[0]
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

        host = netloc.lower().lstrip("www.")
        name = host.split(".")[0].replace("-", " ").title()
        results.append({"company_name": name, "company_website": base})

    print(f"Greenfield: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
