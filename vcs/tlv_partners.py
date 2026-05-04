import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.tlv.partners/portfolio"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "venturebeat",
    "calcalistech", "prnewswire", "axios", "medium", "crunchbase", "globenewswire",
    "businesswire", "nocamels",
}
SKIP_DOMAINS = {"tlv.partners", "gmpg.org", "fonts.gstatic.com", "jobs.tlv.partners"}


def _is_social(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SOCIAL_DOMAINS)


def _is_press(netloc: str, href: str) -> bool:
    return any(p in netloc.lower() or p in href.lower() for p in PRESS_DOMAINS)


def _is_skip(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SKIP_DOMAINS)


def _logo_filename_to_name(logo_url: str) -> str:
    """Derive a company name from a logo image filename."""
    filename = logo_url.rsplit("/", 1)[-1]
    base = re.sub(r"\.[a-z]{2,5}$", "", filename, flags=re.IGNORECASE)
    # Remove common suffixes/qualifiers
    base = re.sub(
        r"(?i)([-_](?:logo|white|color|black|horizontal|v\d+).*|[-_]aquired|-\d{4}$|-\d+x\d+.*)$",
        "",
        base,
    )
    base = re.sub(r"[-_]+", " ", base).strip().title()
    return base


def fetch_portfolio() -> list[dict]:
    """
    Scrape TLV Partners portfolio page.

    Each company card (.tlv_company) contains:
    - A "Visit" link: <a href="COMPANY_URL"> inside .visit
    - A colored logo div (.tlv_logo_color) with data-bg pointing to the logo image

    We use DOM evaluation to extract (url, logo_bg) pairs per company,
    then derive the company name from the logo filename.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=45000)
            for _ in range(10):
                page.keyboard.press("End")
                page.wait_for_timeout(300)

            raw = page.evaluate("""() => {
                const companies = document.querySelectorAll('.tlv_company');
                return Array.from(companies).map(c => {
                    const visitLink = c.querySelector('.visit a');
                    const logoDiv = c.querySelector('.tlv_logo_color');
                    const url = visitLink ? visitLink.getAttribute('href') : null;
                    const logoBg = logoDiv
                        ? (logoDiv.getAttribute('data-bg') || logoDiv.style.backgroundImage)
                        : null;
                    return { url, logoBg };
                });
            }""")
        finally:
            page.close()
            browser.close()

    results = []
    seen_urls: set[str] = set()

    for entry in raw:
        href = (entry.get("url") or "").strip()
        logo_bg = (entry.get("logoBg") or "").strip()

        if not href:
            continue

        parsed = urlparse(href)
        netloc = parsed.netloc

        if _is_social(netloc) or _is_press(netloc, href) or _is_skip(netloc):
            continue

        website = f"{parsed.scheme}://{parsed.netloc}"
        if website in seen_urls:
            continue
        seen_urls.add(website)

        # Derive company name from logo filename
        if logo_bg:
            name = _logo_filename_to_name(logo_bg)
        else:
            name = netloc.lstrip("www.").split(".")[0].title()

        if name and website:
            results.append({"company_name": name, "company_website": website})

    print(f"TLV Partners: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
