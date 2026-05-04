import re
import json as json_module
import httpx
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.nfx.com/portfolio"
NEXT_DATA_PATH = "/_next/data/{build_id}/companies.json"


def _get_build_id() -> str | None:
    """Fetch the portfolio page and extract the Next.js build ID."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            html = page.content()
        finally:
            page.close()
            browser.close()

    m = re.search(r'"buildId"\s*:\s*"([^"]+)"', html)
    if m:
        return m.group(1)
    return None


SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "venturebeat",
    "calcalistech", "prnewswire", "axios", "medium", "crunchbase", "globenewswire",
    "businesswire", "nocamels",
}


def _is_social(url: str) -> bool:
    return any(s in url.lower() for s in SOCIAL_DOMAINS)


def _is_press(url: str) -> bool:
    return any(p in url.lower() for p in PRESS_DOMAINS)


def fetch_portfolio() -> list[dict]:
    """
    Scrape NFX portfolio via the Next.js data API.

    NFX serves company data at /_next/data/{buildId}/companies.json.
    Each company has acf.link (website URL) and title.rendered (company name).
    We filter to Active companies only.
    """
    build_id = _get_build_id()
    if not build_id:
        print("NFX: could not determine build ID - returning []")
        return []

    api_url = f"https://www.nfx.com/_next/data/{build_id}/companies.json"
    try:
        resp = httpx.get(api_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"NFX: API fetch error: {e}")
        return []

    companies = data.get("pageProps", {}).get("companies", [])
    results = []

    for company in companies:
        acf = company.get("acf", {})
        status = acf.get("status", "")
        if status.lower() not in ("active", ""):
            continue  # skip acquired/merged

        name = re.sub(r"<[^>]+>", "", company.get("title", {}).get("rendered", "")).strip()
        website = acf.get("link", "").strip()

        if not name or not website:
            continue

        # Filter social/press URLs
        if _is_social(website) or _is_press(website):
            continue

        # Normalize to just scheme + netloc
        from urllib.parse import urlparse
        parsed = urlparse(website)
        if not parsed.netloc:
            continue
        website_norm = f"{parsed.scheme}://{parsed.netloc}"

        results.append({"company_name": name, "company_website": website_norm})

    print(f"NFX: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
