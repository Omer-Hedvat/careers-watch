import re
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.viola-group.com/portfolio/"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "venturebeat",
    "calcalistech", "prnewswire", "axios", "medium", "crunchbase", "globenewswire",
    "businesswire", "nocamels",
}
SKIP_DOMAINS = {"viola-group.com", "viola.vc", "gmpg.org", "fonts.gstatic.com", "addthis.com"}


def _is_social(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SOCIAL_DOMAINS)


def _is_press(netloc: str) -> bool:
    return any(p in netloc.lower() for p in PRESS_DOMAINS)


def _slug_to_name(slug: str) -> str:
    """Convert URL slug to a company name (best-effort)."""
    return slug.replace("-", " ").title()


def fetch_portfolio() -> list[dict]:
    """
    Scrape Viola Group portfolio page.

    The portfolio page lists companies as internal links to /portfolio/slug/.
    External company websites are not shown on the portfolio index - only slugs
    are available. We return (name, viola-group company page URL) so that
    refresh_companies.py can run discovery against the correct domain.
    Since the company page itself doesn't expose the external URL, we return
    the best-guess canonical website derived from the slug for discovery.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=45000)
            # Scroll to trigger lazy loading
            for _ in range(10):
                page.keyboard.press("End")
                page.wait_for_timeout(300)
            html = page.content()
        finally:
            page.close()
            browser.close()

    # Extract slugs from internal /portfolio/slug links
    slugs = re.findall(r'href="/portfolio/([^/"]+)"', html)
    unique_slugs = list(dict.fromkeys(slugs))  # preserve order, deduplicate

    results = []
    for slug in unique_slugs:
        name = _slug_to_name(slug)
        # Use viola-group internal page as the website - discovery will find the real one
        website = f"https://www.viola-group.com/portfolio/{slug}"
        results.append({"company_name": name, "company_website": website})

    print(f"Viola: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
