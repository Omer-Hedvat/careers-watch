"""
Magenta VC portfolio adapter.

URL:       https://www.magentavc.com/portfolio
Structure: JS-rendered (site blocks plain HTTP); use Playwright.
           Company cards contain logo images and external website links.
           Name is derived from domain since alt text may be empty.

NOTE: Run `uv run vcs/magenta.py` to test and verify selectors.
      The site may require scroll-to-bottom before all cards appear.
"""
import re
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

_PORTFOLIO_URL = "https://www.magentavc.com/portfolio"
_OWN_DOMAIN = "magentavc.com"

_SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
}
_SKIP_DOMAINS = {
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com", "prnewswire.com",
    "businesswire.com",
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
    """Scrape Magenta VC portfolio and return list of {company_name, company_website}."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(_PORTFOLIO_URL, wait_until="networkidle", timeout=30000)
            # Scroll to bottom to trigger lazy-load
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            html = page.content()
        except Exception as e:
            print(f"Magenta: Playwright error - {e}")
            browser.close()
            return []
        browser.close()

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

    print(f"Magenta: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
