"""
Bessemer Venture Partners portfolio adapter.

BVP has a built-in Israel filter on their portfolio page.
We use that to scrape only Israeli portfolio companies.
Each company entry has a "Visit Website" link with an absolute external URL.
"""
import re
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.bvp.com/portfolio?filter=portfolio-roadmap&value=israel"

SKIP_DOMAINS = {
    "bvp.com", "bessemer.com",
    "linkedin.com", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "youtube.com",
    "medium.com", "techcrunch.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    for s in SKIP_DOMAINS:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def fetch_portfolio() -> list[dict]:
    """Scrape BVP Israel portfolio page. Returns list of {company_name, company_website}."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            raw = page.evaluate("""() => {
                const entries = [];
                const seen = new Set();

                // BVP applies the Israel portfolio filter by removing the 'hidden' class
                // from matching article cards. We select only non-hidden investment cards.
                document.querySelectorAll('article.investment:not(.hidden)').forEach(article => {
                    const visitLink = [...article.querySelectorAll('a')].find(
                        a => /visit website/i.test(a.textContent.trim())
                    );
                    if (!visitLink) return;

                    const href = visitLink.href;
                    if (!href || !href.startsWith('http') || seen.has(href)) return;

                    const heading = article.querySelector('h1, h2, h3, h4');
                    const name = heading ? heading.textContent.trim() : '';
                    if (!name) return;

                    seen.add(href);
                    entries.push({ name, website: href });
                });

                return entries;
            }""")
        finally:
            browser.close()

    results = []
    for entry in raw:
        parsed = urlparse(entry["website"])
        if not parsed.netloc or _is_filtered(parsed.netloc):
            continue
        website = f"{parsed.scheme}://{parsed.netloc}"
        results.append({"company_name": entry["name"], "company_website": website})

    print(f"Bessemer: found {len(results)} Israeli portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
