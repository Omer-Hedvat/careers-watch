import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "forbes", "techcrunch", "wsj", "reuters", "bloomberg", "siliconangle", "venturebeat",
    "calcalistech", "prnewswire", "axios", "msspalert", "securityboulevard", "hackread",
    "ynetnews", "medium", "crunchbase", "devops.com", "scworld", "esecurityplanet",
    "cioinfluence", "nocamels", "globenewswire", "crn.com", "thenextweb", "securityweek",
    "darkreading", "helpnetsecurity", "zdnet", "wired", "businesswire",
}

PORTFOLIO_URL = "https://team8.vc/portfolio/"


def _is_press(netloc: str, href: str) -> bool:
    netloc = netloc.lower()
    return any(p in netloc or p in href.lower() for p in PRESS_DOMAINS)


def _is_social(netloc: str) -> bool:
    clean = netloc.lower().split("@")[-1]
    return any(clean == s or clean.endswith("." + s) for s in SOCIAL_DOMAINS)


def _get_company_slugs(browser) -> list[str]:
    """Fetch the portfolio index page and extract company slugs."""
    page = browser.new_page()
    try:
        page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=30000)
        html = page.content()
    finally:
        page.close()

    # Links like https://team8.vc/portfolio/fig-security/
    slugs = re.findall(r'href="https://team8\.vc/portfolio/([^/]+)/"', html)
    # Deduplicate, exclude the portfolio index itself
    seen = set()
    result = []
    for s in slugs:
        if s and s not in seen:
            seen.add(s)
            result.append(s)
    return result


def _get_company_website(browser, slug: str) -> tuple[str, str] | None:
    """Fetch individual company page and return (name, website) or None."""
    url = f"https://team8.vc/portfolio/{slug}/"
    page = browser.new_page()
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        html = page.content()
    except Exception as e:
        print(f"  team8/{slug}: load error: {e}")
        return None
    finally:
        page.close()

    # Company name from <h1> or <title>
    name_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    if name_m:
        name = re.sub(r"<[^>]+>", "", name_m.group(1)).strip()
    else:
        # Fallback: prettify slug
        name = slug.replace("-", " ").title()

    # Find external company website - first non-team8, non-social, non-press link
    website = None
    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        href = m.group(1)
        parsed = urlparse(href)
        netloc = parsed.netloc

        if "team8.vc" in netloc:
            continue
        if _is_social(netloc) or _is_press(netloc, href):
            continue
        if "gmpg.org" in netloc:
            continue

        # Skip long paths (article/blog links)
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(path_parts) > 2:
            continue

        website = f"{parsed.scheme}://{parsed.netloc}"
        break

    if not name or not website:
        return None
    return name, website


def fetch_portfolio() -> list[dict]:
    """Scrape Team8 portfolio page and return list of {company_name, company_website}."""
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            slugs = _get_company_slugs(browser)
            for slug in slugs:
                entry = _get_company_website(browser, slug)
                if entry:
                    name, website = entry
                    results.append({"company_name": name, "company_website": website})
        finally:
            browser.close()

    print(f"Team8: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
