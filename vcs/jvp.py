import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://jvpvc.com/portfolio/"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
SKIP_DOMAINS = {"jvpvc.com", "elfsight.com", "gmpg.org", "fonts.gstatic.com",
                "cookiebot.com", "google.com", "jobs.jvpvc.com"}
SKIP_SCHEMES = {"mailto", "tel"}


def _is_social(netloc: str) -> bool:
    # Strip userinfo (e.g. "info@domain.com" -> "domain.com")
    clean = netloc.lower().split("@")[-1]
    # Use suffix/domain match, not substring, to avoid "x.com" matching "earnix.com"
    return any(clean == s or clean.endswith("." + s) for s in SOCIAL_DOMAINS)


def _is_skip(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def _url_to_name(url: str) -> str:
    """Derive a company name from its website URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lstrip("www.")
    # Handle subdomains like "chain-reaction.io" -> "Chain Reaction"
    name = domain.split(".")[0].replace("-", " ").title()
    return name


def fetch_portfolio() -> list[dict]:
    """
    Scrape JVP portfolio page.

    JVP embeds portfolio companies in .portfolioItems containers.
    Each item has a set of links; the company website is the first
    external http/https link (not jvpvc.com, not social, not email).
    Company names are derived from the website domain.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=45000)

            raw = page.evaluate("""() => {
                const items = document.querySelectorAll('.portfolioItems');
                return Array.from(items).map(item => {
                    const allLinks = [];
                    item.querySelectorAll('a[href]').forEach(a => {
                        const href = a.getAttribute('href');
                        if (href) allLinks.push(href);
                    });
                    return { links: allLinks };
                });
            }""")
        finally:
            page.close()
            browser.close()

    results = []
    seen_urls: set[str] = set()

    SKIP_URL_PATTERNS = {"http://empty", "#", ""}

    for entry in raw:
        company_url = None
        for href in entry.get("links", []):
            href = href.strip()
            if not href or href in SKIP_URL_PATTERNS:
                continue

            parsed = urlparse(href)

            if parsed.scheme in SKIP_SCHEMES:
                continue
            if not parsed.scheme.startswith("http"):
                continue

            netloc = parsed.netloc
            if _is_social(netloc) or _is_skip(netloc):
                continue

            company_url = f"{parsed.scheme}://{parsed.netloc}"
            break

        if not company_url or company_url in seen_urls:
            continue
        seen_urls.add(company_url)

        name = _url_to_name(company_url)
        results.append({"company_name": name, "company_website": company_url})

    print(f"JVP: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
