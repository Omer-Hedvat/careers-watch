"""
Boldstart Ventures portfolio adapter.

Two-step scraper (same pattern as Cyberstarts):
  Step 1: Playwright renders /companies/ (JS-heavy) to extract company slugs.
  Step 2: httpx fetches each company detail page; extracts the external website link
          (an icon/globe anchor with empty text pointing to the company domain).
"""
import re
from urllib.parse import urlparse

import httpx
from playwright.sync_api import sync_playwright

BASE_URL = "https://boldstart.vc"
COMPANIES_URL = f"{BASE_URL}/companies/"

SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "youtube.com",
}
CDN_DOMAINS = {
    "fonts.gstatic.com", "fonts.googleapis.com",
    "googleapis.com", "gstatic.com",
    "cloudfront.net", "amazonaws.com",
    "cloudflare.com", "cdn.jsdelivr.net",
    "unpkg.com", "cdnjs.cloudflare.com",
    "stripe.com", "intercom.io", "hubspot.com",
    "google-analytics.com", "googletagmanager.com",
    "segment.com", "amplitude.com",
}
SKIP_DOMAINS = {"boldstart.vc", "fastforward.boldstart.vc"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    all_skip = SOCIAL_DOMAINS | CDN_DOMAINS | SKIP_DOMAINS
    return any(clean == s or clean.endswith("." + s) for s in all_skip)


def _fetch_company_site(client: httpx.Client, slug: str) -> tuple[str, str | None]:
    """Fetch company detail page. Returns (name, website_url | None)."""
    url = f"{BASE_URL}/companies/{slug}/"
    try:
        resp = client.get(url, follow_redirects=True, timeout=15)
        if resp.status_code != 200:
            return slug.replace("-", " ").title(), None
        html = resp.text

        # Company name: prefer <h1>, fall back to <title>
        h1 = re.search(r"<h1[^>]*>\s*([^<]+?)\s*</h1>", html, re.IGNORECASE)
        if h1:
            name = h1.group(1).strip()
        else:
            title = re.search(r"<title[^>]*>([^|<–-]+)", html)
            name = title.group(1).strip() if title else slug.replace("-", " ").title()

        # External website: first external link that isn't social/boldstart
        for m in re.finditer(r'href="(https?://[^"]+)"', html):
            href = m.group(1)
            parsed = urlparse(href)
            netloc = parsed.netloc
            if not netloc or _is_filtered(netloc):
                continue
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return name, f"{parsed.scheme}://{parsed.netloc.lower()}"
    except Exception:
        pass
    return slug.replace("-", " ").title(), None


def fetch_portfolio() -> list[dict]:
    """Scrape Boldstart portfolio. Returns list of {company_name, company_website}."""
    # Step 1: Render the JS-heavy companies listing page with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(COMPANIES_URL, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(2000)
            html = page.content()
        finally:
            browser.close()

    # Extract unique company slugs from internal /companies/slug/ links
    slug_re = re.compile(
        r'href="(?:https://boldstart\.vc)?/companies/([^/"]+)/"?'
    )
    slugs = list(dict.fromkeys(m.group(1) for m in slug_re.finditer(html)))

    if not slugs:
        print("Boldstart: no company slugs found on listing page")
        return []

    # Step 2: Fetch each company detail page to get external website URL
    results = []
    with httpx.Client(headers=HEADERS) as client:
        for slug in slugs:
            name, website = _fetch_company_site(client, slug)
            if website:
                results.append({"company_name": name, "company_website": website})

    print(f"Boldstart: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
