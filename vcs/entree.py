"""
Entrée Capital portfolio adapter.

URL:       https://entreecap.com/companies
Structure: WordPress site. Most company website links are present in the
           static HTML (~180+ companies). A "Load More" button loads additional
           companies dynamically. We try httpx first; if a Load More button is
           detected we switch to Playwright to click through all pages.

           Heavy Israel focus: monday.com, Riskified, HiBob are in portfolio.
"""
import re
from urllib.parse import urlparse

import httpx
from playwright.sync_api import sync_playwright

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

_PORTFOLIO_URL = "https://entreecap.com/companies"
_OWN_DOMAIN = "entreecap.com"

_SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
}
_SKIP_DOMAINS = {
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com", "prnewswire.com",
    "businesswire.com", "globenewswire.com", "wired.com",
    # CDN and infrastructure
    "cdn.jsdelivr.net", "fonts.googleapis.com", "fonts.gstatic.com",
    "js.hsforms.net", "api.w.org",
    # Well-known non-portfolio domains that appear in press/news
    "deliveroo.co.uk", "seatgeek.com", "postmates.com", "gusto.com",
    "stripe.com", "solana.com", "snapchat.com", "zynga.com",
    "pillpack.com", "houseparty.com", "agero.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    blocked = _SOCIAL_DOMAINS | _SKIP_DOMAINS | {_OWN_DOMAIN}
    return any(clean == s or clean.endswith("." + s) for s in blocked)


def _name_from_text_or_domain(text: str, netloc: str) -> str:
    text = text.strip()
    # Strip HTML tags from text
    text = re.sub(r"<[^>]+>", "", text).strip()
    if text and len(text) < 60:
        return text
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def _extract_companies(html: str) -> list[dict]:
    """Extract portfolio company links from HTML."""
    seen: set[str] = set()
    results: list[dict] = []

    for m in re.finditer(r'<a\s+[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE):
        href = m.group(1)
        raw_text = m.group(2)

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

    return results


def _fetch_with_playwright() -> str:
    """Use Playwright to load the page and click all Load More buttons."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(_PORTFOLIO_URL, wait_until="load", timeout=60000)
            page.wait_for_timeout(3000)

            # Click "Load More" until it disappears or 20 iterations max
            clicks = 0
            while clicks < 20:
                # Look for a Load More button
                btn = page.query_selector("button:has-text('Load More'), a:has-text('Load More'), [class*='load-more']")
                if not btn or not btn.is_visible():
                    break
                try:
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    page.wait_for_timeout(2000)
                    clicks += 1
                except Exception:
                    break

            if clicks > 0:
                print(f"Entree: clicked Load More {clicks} times")

            # Also scroll to bottom to catch any lazy-loaded content
            for _ in range(5):
                page.keyboard.press("End")
                page.wait_for_timeout(500)

            html = page.content()
        except Exception as e:
            print(f"Entree: Playwright error - {e}")
            html = ""
        finally:
            browser.close()
    return html


def fetch_portfolio() -> list[dict]:
    """Scrape Entree Capital portfolio and return list of {company_name, company_website}."""
    # Try httpx first - most companies are in static HTML
    try:
        resp = httpx.get(_PORTFOLIO_URL, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Entree: error fetching portfolio with httpx - {e}")
        html = ""

    # Check if there's a Load More button - if so, use Playwright for full load
    has_load_more = bool(re.search(r"load.?more", html, re.IGNORECASE))
    if has_load_more:
        print("Entree: Load More detected - using Playwright for full load")
        playwright_html = _fetch_with_playwright()
        if playwright_html:
            html = playwright_html

    results = _extract_companies(html)
    print(f"Entree: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
