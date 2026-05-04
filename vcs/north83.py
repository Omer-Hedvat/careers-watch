import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.83north.com/companies/"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "venturebeat",
    "calcalistech", "prnewswire", "axios", "medium", "crunchbase", "globenewswire",
    "businesswire", "nocamels",
}
SKIP_DOMAINS = {
    "83north.com", "gmpg.org", "fonts.gstatic.com", "bunny-wp-pullzone",
    "accessibe.com", "dynamoeu.netagesolutions.com",
}


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
    Scrape 83North portfolio page (/companies/).

    Structure:
      <h2>Company Name</h2>
      <h3>Tagline</h3>
      <p class="website"><a href="https://company.com">...</a></p>
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=45000)
            for _ in range(10):
                page.keyboard.press("End")
                page.wait_for_timeout(300)
            html = page.content()
        finally:
            page.close()
            browser.close()

    results = []
    seen_urls: set[str] = set()

    # Pattern: <h2>Name</h2> ... <p class="website"><a href="URL">
    block_pattern = re.compile(
        r"<h2>([^<]+)</h2>.*?<p class=\"website\"><a href=\"(https?://[^\"]+)\"",
        re.DOTALL,
    )

    for m in block_pattern.finditer(html):
        name = m.group(1).strip()
        href = m.group(2).strip()
        parsed = urlparse(href)
        netloc = parsed.netloc

        if _is_social(netloc) or _is_press(netloc, href) or _is_skip(netloc):
            continue

        website = f"{parsed.scheme}://{parsed.netloc}"
        if website in seen_urls:
            continue
        seen_urls.add(website)

        if name and website:
            results.append({"company_name": name, "company_website": website})

    print(f"83North: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
