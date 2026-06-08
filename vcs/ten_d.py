"""
10D portfolio adapter.

URL:       https://www.10d.vc/portfolio/
Structure: JS-rendered WordPress site. Company cards are rendered client-side;
           the raw HTML only has navigation links. Playwright needed.
           49 companies across cyber, defense, fintech, enterprise, deep tech.
"""
import re
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

_INDEX_URL = "https://www.10d.vc/portfolio/"
_OWN_DOMAIN = "10d.vc"

_SKIP_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com",
    "google.com", "googleapis.com", "gstatic.com", "googletagmanager.com",
    "cloudflare.com", "w3.org", "wordpress.com", "wp.com",
    "servc.co.il", "gmpg.org", "apple.com", "microsoft.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    blocked = _SKIP_DOMAINS | {_OWN_DOMAIN}
    return any(clean == s or clean.endswith("." + s) for s in blocked)


def fetch_portfolio() -> list[dict]:
    """Scrape 10D portfolio and return list of {company_name, company_website}."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(_INDEX_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            html = page.content()
            browser.close()
    except Exception as e:
        print(f"10D: error fetching portfolio - {e}")
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

    print(f"10D: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
