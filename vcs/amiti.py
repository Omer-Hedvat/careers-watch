"""
Amiti Ventures portfolio adapter.

URL:       https://www.amiti.vc/portfolio
Structure: Static HTML. Active portfolio companies appear as external anchor tags
           within the page body. Company name is derived from link text or domain.
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

_INDEX_URL = "https://www.amiti.vc/portfolio"
_OWN_DOMAIN = "amiti.vc"

_SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
}
_SKIP_DOMAINS = {
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com", "prnewswire.com",
    "businesswire.com",
    # Acquirer domains - these appear when a company is listed as acquired
    "crowdstrike.com", "microsoft.com", "paloaltonetworks.com",
    "salesforce.com", "jfrog.com", "samsung.com", "apple.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    blocked = _SOCIAL_DOMAINS | _SKIP_DOMAINS | {_OWN_DOMAIN}
    return any(clean == s or clean.endswith("." + s) for s in blocked)


def _name_from_text_or_domain(text: str, netloc: str) -> str:
    text = text.strip()
    if text and len(text) < 50:
        return text
    host = netloc.lower().lstrip("www.")
    return host.split(".")[0].replace("-", " ").title()


def fetch_portfolio() -> list[dict]:
    """Scrape Amiti Ventures portfolio and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(_INDEX_URL, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Amiti: error fetching portfolio - {e}")
        return []

    seen: set[str] = set()
    results: list[dict] = []

    for m in re.finditer(r'<a\s+[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE):
        href = m.group(1)
        raw_text = re.sub(r"<[^>]+>", "", m.group(2)).strip()

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

        name = _name_from_text_or_domain(raw_text, netloc)
        results.append({"company_name": name, "company_website": base})

    print(f"Amiti: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
