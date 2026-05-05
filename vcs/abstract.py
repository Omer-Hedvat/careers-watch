"""
Abstract Ventures portfolio adapter.

Portfolio is at https://www.abstract.com/companies-list/ - a JS-rendered
page with 470+ company cards. Each card has:
  - .all-companies-modal__item-logo-text: company name
  - <a>Visit Website</a>: external website URL

All companies load in one scroll pass (no pagination).
"""
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

COMPANIES_URL = "https://www.abstract.com/companies-list/"

SKIP_DOMAINS = {
    "abstract.com", "abstractvc.com",
    "linkedin.com", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "youtube.com",
    "jobs.abstractvc.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def fetch_portfolio() -> list[dict]:
    """Scrape Abstract Ventures portfolio. Returns list of {company_name, company_website}."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(COMPANIES_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)
            # Scroll progressively to trigger lazy-loading of all cards
            for _ in range(8):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            raw = page.evaluate("""() => {
                const entries = [];
                const seen = new Set();

                document.querySelectorAll('div.all-companies-modal__item').forEach(card => {
                    // Name: prefer logo-text div; fall back to logo img alt attribute
                    const nameEl = card.querySelector('.all-companies-modal__item-logo-text');
                    let name = nameEl ? nameEl.textContent.trim() : '';
                    if (!name) {
                        const logoImg = card.querySelector('.all-companies-modal__item-logo img');
                        name = logoImg ? (logoImg.alt || '').trim() : '';
                    }
                    if (!name) return;

                    // "Visit Website" link is the external company URL
                    const visitLink = [...card.querySelectorAll('a')].find(
                        a => a.textContent.trim() === 'Visit Website'
                    );
                    if (!visitLink) return;

                    const href = visitLink.href;
                    if (!href || !href.startsWith('http')) return;

                    try {
                        const url = new URL(href);
                        const base = url.origin;
                        if (!seen.has(base)) {
                            seen.add(base);
                            entries.push({ name, website: base });
                        }
                    } catch (_) {}
                });

                return entries;
            }""")
        finally:
            browser.close()

    results = []
    for entry in raw:
        parsed = urlparse(entry["website"])
        if parsed.netloc and not _is_filtered(parsed.netloc):
            results.append({
                "company_name": entry["name"],
                "company_website": entry["website"],
            })

    print(f"Abstract Ventures: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
