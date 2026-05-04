import re
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://fintlv.com/portfolio/"

# Known FinTLV portfolio companies with their websites
# The portfolio page shows company names but not external website links
# (company websites open via Jet Popup on click, not in static HTML)
# This hardcoded list was compiled from the portfolio page + public sources
KNOWN_COMPANIES = [
    ("Able", "https://able.finance"),
    ("Akinova", "https://www.akinova.com"),
    ("AKUR8", "https://akur8.com"),
    ("Assured Allies", "https://www.assuredallies.com"),
    ("BlackSwan Technologies", "https://www.blackswantechnologies.ai"),
    ("Bolttech", "https://bolt.tech"),
    ("Carbyne", "https://carbyne.com"),
    ("Corvus", "https://www.corvusinsurance.com"),
    ("Foretellix", "https://www.foretellix.com"),
    ("Health Bridge", "https://www.hbridge.com"),
    ("Hippo", "https://www.hippo.com"),
    ("ifeel", "https://ifeelonline.com"),
    ("Livez", "https://www.livez.health"),
    ("Lovys", "https://www.lovys.com"),
    ("mailo", "https://www.mailo-insurance.com"),
    ("Momentick", "https://momentick.com"),
    ("Next Insurance", "https://www.nextinsurance.com"),
    ("NorthOne", "https://www.northone.com"),
    ("Onit", "https://www.onit.com"),
    ("Sweetch", "https://www.sweetch.com"),
    ("Unqork", "https://www.unqork.com"),
    ("Venn", "https://www.venn.city"),
    ("wefox", "https://www.wefox.com"),
]


def fetch_portfolio() -> list[dict]:
    """
    Return FinTLV portfolio companies.

    The fintlv.com portfolio page embeds company names in Elementor headings
    but website links only load via Jet Popup (not in static HTML).
    We return the known hardcoded list rather than relying on the dynamic popup.
    """
    # Attempt to scrape for any new companies not in the hardcoded list
    scraped_names: set[str] = set()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)
                html = page.content()
            finally:
                page.close()
                browser.close()

        # Extract company names from headings
        names = re.findall(
            r'elementor-heading-title elementor-size-default">([^<]+)</div>',
            html,
        )
        scraped_names = {n.strip() for n in names if n.strip() and len(n.strip()) < 50}
    except Exception as e:
        print(f"  fintlv: scrape warning: {e}")

    known_names = {name for name, _ in KNOWN_COMPANIES}
    new_names = scraped_names - known_names
    if new_names:
        print(f"  fintlv: WARNING - found new company names not in hardcoded list: {new_names}")

    results = [{"company_name": name, "company_website": website} for name, website in KNOWN_COMPANIES]
    print(f"FinTLV: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
