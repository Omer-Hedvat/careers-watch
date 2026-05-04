import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "siliconangle", "venturebeat",
    "calcalistech", "prnewswire", "axios", "msspalert", "securityboulevard", "hackread",
    "ynetnews", "medium", "crunchbase", "devops.com", "scworld", "esecurityplanet",
    "cioinfluence", "nocamels", "globenewswire", "crn.com", "thenextweb", "451research",
    "vator.tv", "tenable.com", "gigaom", "go.hunters", "securityweek", "darkreading",
    "helpnetsecurity", "zdnet", "wired", "businesswire", "investors.",
}


def _is_press(netloc: str, href: str) -> bool:
    netloc = netloc.lower()
    return any(p in netloc or p in href.lower() for p in PRESS_DOMAINS)


def _is_social(netloc: str) -> bool:
    return any(s in netloc.lower() for s in SOCIAL_DOMAINS)


def fetch_portfolio() -> list[dict]:
    """Scrape YL Ventures portfolio page and return list of {company_name, company_website}."""
    url = "https://www.ylventures.com/portfolio/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_selector(".modal-portfolio-trigger", timeout=15000)
        html = page.content()
        browser.close()

    # Extract company names from card logo alt text
    card_re = re.compile(
        r'data-company="([^#][^"]+)"[^>]*>.*?alt="([^"]+?)\s*(?:logo)?"\s*class="card__logo',
        re.DOTALL,
    )
    cards = {}
    for m in card_re.finditer(html):
        slug, name = m.group(1).strip(), m.group(2).strip()
        if slug not in ("+ companySlug +", "${companySlug}"):
            cards[slug] = name

    # Extract carousel blocks — each contains one company's modal content
    starts = [
        (m.start(), m.group(1).lstrip("#"))
        for m in re.finditer(
            r'<div class="carousel-item company-block[^"]*" data-company="([^"]+)"', html
        )
    ]

    results = []
    for i, (start, slug) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else start + 10000
        block = html[start:end]

        website = None
        for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL):
            href = m.group(1)
            text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            parsed = urlparse(href)
            netloc = parsed.netloc

            if _is_social(netloc) or _is_press(netloc, href):
                continue
            # Skip internal YL pages
            if "ylventures.com" in netloc:
                continue
            # Skip long article paths — company homepages have at most 1-2 path segments
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue

            candidate = f"{parsed.scheme}://{parsed.netloc}"
            # Prefer empty-text links (logo/icon → company site)
            if not text:
                website = candidate
                break
            elif website is None:
                website = candidate

        name = cards.get(slug, slug)
        if website:
            results.append({"company_name": name, "company_website": website})

    print(f"YL Ventures: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
