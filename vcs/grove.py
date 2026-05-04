import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PORTFOLIO_INDEX_URL = "https://www.grovevc.com/grove-portfolio-companies/"
PORTFOLIO_BASE_URL = "https://www.grovevc.com/portfolio/"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "venturebeat",
    "calcalistech", "prnewswire", "axios", "medium", "crunchbase", "globenewswire",
    "businesswire", "nocamels",
}
SKIP_DOMAINS = {"grovevc.com", "gmpg.org", "fonts.gstatic.com", "careers.grovevc.com",
                "sharethis.com", "pxcel"}


def _is_social(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SOCIAL_DOMAINS)


def _is_press(netloc: str, href: str) -> bool:
    return any(p in netloc.lower() or p in href.lower() for p in PRESS_DOMAINS)


def _is_skip(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def _get_company_slugs(html: str) -> list[tuple[str, str]]:
    """Extract (company_name, slug) from portfolio index HTML."""
    # Pattern: <div class="portfolio-box COMPANY_NAME " data-category="...">
    # followed by <a href="/portfolio/slug/">
    block_pattern = re.compile(
        r'<div class="portfolio-box ([^"]+) "[^>]*>.*?href="https://www\.grovevc\.com/portfolio/([^/"]+)/"',
        re.DOTALL,
    )
    seen: set[str] = set()
    results = []
    for m in block_pattern.finditer(html):
        name = m.group(1).strip()
        slug = m.group(2).strip()
        if slug and slug not in seen:
            seen.add(slug)
            results.append((name, slug))
    return results


def _get_company_website(browser, slug: str) -> str | None:
    """Fetch Grove company page and extract the external website via web-link class."""
    url = f"{PORTFOLIO_BASE_URL}{slug}/"
    page = browser.new_page()
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        html = page.content()
    except Exception as e:
        print(f"  grove/{slug}: load error: {e}")
        return None
    finally:
        page.close()

    # Pattern: <a class="web-link for-desktop" href="COMPANY_URL">
    links = re.findall(r'class="web-link[^"]*"[^>]*href="(https?://[^"]+)"', html)
    for href in links:
        parsed = urlparse(href)
        netloc = parsed.netloc
        if _is_social(netloc) or _is_press(netloc, href) or _is_skip(netloc):
            continue
        return f"{parsed.scheme}://{parsed.netloc}"

    return None


def fetch_portfolio() -> list[dict]:
    """
    Scrape Grove Ventures portfolio.

    - Index page: lists company names (as div class) and slugs (internal links)
    - Per-company page: has <a class="web-link for-desktop"> with external website
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            index_page = browser.new_page()
            index_page.goto(PORTFOLIO_INDEX_URL, wait_until="networkidle", timeout=45000)
            for _ in range(5):
                index_page.keyboard.press("End")
                index_page.wait_for_timeout(300)
            index_html = index_page.content()
            index_page.close()

            company_pairs = _get_company_slugs(index_html)
            results = []

            for name, slug in company_pairs:
                website = _get_company_website(browser, slug)
                if website:
                    results.append({"company_name": name, "company_website": website})
                else:
                    print(f"  grove/{slug}: no website found, skipping")
        finally:
            browser.close()

    print(f"Grove: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
