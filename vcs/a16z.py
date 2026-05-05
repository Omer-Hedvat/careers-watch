"""
Andreessen Horowitz (a16z) portfolio adapter.

Company data is embedded in the page as window.a16z_portfolio_companies,
a JSON array of 800+ portfolio companies. We read it via Playwright's
page.evaluate() and return {company_name, company_website}.
"""
import json as _json
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://a16z.com/portfolio/"

SKIP_DOMAINS = {
    "a16z.com", "andreessen.com",
    "linkedin.com", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "youtube.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def fetch_portfolio() -> list[dict]:
    """Scrape a16z portfolio via window.a16z_portfolio_companies. Returns {company_name, company_website}."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            raw = page.evaluate("() => JSON.stringify(window.a16z_portfolio_companies || [])")
        finally:
            browser.close()

    try:
        companies_data = _json.loads(raw)
    except Exception as e:
        print(f"a16z: failed to parse portfolio data - {e}")
        return []

    if not companies_data:
        print("a16z: window.a16z_portfolio_companies is empty or missing")
        return []

    results = []
    seen = set()
    for entry in companies_data:
        name = (entry.get("title") or "").strip()
        web = (entry.get("web") or "").strip()

        if not name or not web or name == "[untitled]":
            continue

        parsed = urlparse(web)
        if not parsed.netloc or _is_filtered(parsed.netloc):
            continue

        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in seen:
            seen.add(base)
            results.append({"company_name": name, "company_website": base})

    print(f"a16z: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
