import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.firstime.vc/companies/"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "venturebeat",
    "calcalistech", "prnewswire", "axios", "medium", "crunchbase", "globenewswire",
    "businesswire", "nocamels",
}
SKIP_DOMAINS = {"firstime.vc", "firstime.vcmdataroom.com", "gmpg.org", "fonts.gstatic.com"}


def _is_social(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SOCIAL_DOMAINS)


def _is_press(netloc: str, href: str) -> bool:
    return any(p in netloc.lower() or p in href.lower() for p in PRESS_DOMAINS)


def _is_skip(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def fetch_portfolio() -> list[dict]:
    """
    Scrape Firstime VC portfolio from /companies/.

    Each company is displayed as a flip card:
    - Front face: image with alt=company_name
    - Back face: <a href="company_website"> (the entire back div is the link)

    We use DOM evaluation to pair front names with back URLs.
    Note: Some entries have /tag/ internal links instead of external URLs,
    and a few have mismatched names. We filter out internal firstime.vc links.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(2000)

            # Use DOM evaluation to pair front img alt with back href
            raw = page.evaluate("""() => {
                const widgets = document.querySelectorAll('.elementor-widget-flip-box');
                return Array.from(widgets).map(widget => {
                    const front = widget.querySelector('.elementor-flip-box__front');
                    const back = widget.querySelector('.elementor-flip-box__back');
                    const img = front ? front.querySelector('img') : null;
                    const name = img ? img.getAttribute('alt') : null;
                    const url = back ? back.getAttribute('href') : null;
                    return { name, url };
                });
            }""")
        finally:
            page.close()
            browser.close()

    results = []
    seen_urls: set[str] = set()

    for entry in raw:
        name = (entry.get("name") or "").strip()
        href = (entry.get("url") or "").strip()

        if not name or not href:
            continue

        # Filter internal links (relative paths or firstime.vc domains)
        if not href.startswith("http"):
            continue

        parsed = urlparse(href)
        netloc = parsed.netloc

        if _is_social(netloc) or _is_press(netloc, href) or _is_skip(netloc):
            continue

        website = f"{parsed.scheme}://{parsed.netloc}"
        if website in seen_urls:
            continue
        seen_urls.add(website)

        results.append({"company_name": name, "company_website": website})

    print(f"Firstime: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
