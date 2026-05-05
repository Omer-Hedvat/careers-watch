"""
Bain Capital Ventures portfolio adapter.

Playwright renders the JS-heavy portfolio page.
Company cards are wrapped in <a href="https://company.com/"> anchors
that contain a heading with the company name.
"""
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://baincapitalventures.com/portfolio/"

SKIP_DOMAINS = {
    "baincapitalventures.com", "bain.com",
    "linkedin.com", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "youtube.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def fetch_portfolio() -> list[dict]:
    """Scrape BCV portfolio. Returns list of {company_name, company_website}."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)

            # Click "Load more" until all companies are loaded
            for _ in range(20):
                btn = page.query_selector("button:has-text('Load more')")
                if not btn:
                    break
                btn.click()
                page.wait_for_timeout(1500)

            raw = page.evaluate("""() => {
                const entries = [];
                const seen = new Set();

                // Company links live in the #companies section.
                // Format: <a href="https://company.com/">Company Name - description</a>
                // We take the text before " - " as the company name.
                const section = document.getElementById('companies');
                if (!section) return entries;

                section.querySelectorAll('a[href]').forEach(link => {
                    const href = link.href;
                    if (!href || !href.startsWith('http')) return;
                    try {
                        const url = new URL(href);
                        if (url.hostname.includes('baincapital')) return;

                        // Skip partner/team/domain internal-looking content
                        if (/baincapital|team|domain/i.test(url.hostname)) return;

                        const rawText = link.textContent.trim();
                        if (!rawText || rawText.length < 2) return;

                        // Strip description after " - "
                        const name = rawText.split(' - ')[0].trim();
                        if (!name) return;

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

    print(f"Bain Capital Ventures: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
