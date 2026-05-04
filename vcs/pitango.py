import re
from urllib.parse import urlparse
import httpx
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.pitango.com/portfolio/"
AJAX_URL = "https://www.pitango.com/wp-admin/admin-ajax.php"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "venturebeat",
    "calcalistech", "prnewswire", "axios", "medium", "crunchbase", "globenewswire",
    "businesswire", "nocamels", "globes.co.il", "geektime", "calcalist",
    "techtime", "zdnet", "wired",
}
SKIP_DOMAINS = {"pitango.com", "gmpg.org", "fonts.gstatic.com", "cookiebot.com",
                "accessibe.com", "icx.efrontcloud.com", "business.safety.google"}


def _is_social(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SOCIAL_DOMAINS)


def _is_press(netloc: str, href: str) -> bool:
    return any(p in netloc.lower() or p in href.lower() for p in PRESS_DOMAINS)


def _is_skip(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def _get_company_slugs_and_names(html: str) -> list[tuple[str, str]]:
    """Extract (slug, name) pairs from the portfolio page HTML."""
    # Pattern: data-slug="slug" ... alt="Company Name"
    pairs = re.findall(
        r'data-slug="([^"]+)"[^>]*>.*?<img[^>]*alt="([^"]+)"',
        html,
        re.DOTALL,
    )
    seen: set[str] = set()
    results = []
    for slug, name in pairs:
        if slug and name and slug not in seen:
            seen.add(slug)
            results.append((slug, name))
    return results


def _get_company_website(slug: str) -> str | None:
    """Fetch modal HTML via AJAX and extract the company website."""
    try:
        resp = httpx.post(
            AJAX_URL,
            data={"action": "get_popup", "slug": slug, "paging": "show"},
            headers={"Referer": PORTFOLIO_URL},
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        html = resp.text
    except Exception as e:
        print(f"  pitango/{slug}: AJAX error: {e}")
        return None

    # Find company website (not social/press)
    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        href = m.group(1)
        parsed = urlparse(href)
        netloc = parsed.netloc

        if _is_social(netloc) or _is_press(netloc, href) or _is_skip(netloc):
            continue

        # Skip long paths
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(path_parts) > 2:
            continue

        return f"{parsed.scheme}://{parsed.netloc}"

    return None


def fetch_portfolio() -> list[dict]:
    """
    Scrape Pitango portfolio page.

    Companies are rendered as clickable cards that open a modal via AJAX POST.
    We extract slugs and names from the portfolio page HTML, then call the
    AJAX endpoint per company to get the external website URL.
    """
    # Get portfolio page HTML
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=45000)
            for _ in range(5):
                page.keyboard.press("End")
                page.wait_for_timeout(300)
            html = page.content()
        finally:
            page.close()
            browser.close()

    company_pairs = _get_company_slugs_and_names(html)
    results = []

    for slug, name in company_pairs:
        website = _get_company_website(slug)
        if website:
            results.append({"company_name": name, "company_website": website})
        else:
            print(f"  pitango/{slug}: no website found, skipping")

    print(f"Pitango: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
