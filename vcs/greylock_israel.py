"""
Greylock portfolio adapter.

URL: https://greylock.com/portfolio
Structure: server-side rendered WordPress site.  Companies are in
           <div class="portfolio-modal-box ..."> blocks, each containing
           a logo image (alt="COMPANY NAME Logo") and a website link
           distinguished by an "icon link" img alt attribute.
           No Israel filter - returns the full portfolio; the ATS-detect
           step filters irrelevant companies downstream.
"""
import re
from urllib.parse import urlparse

import httpx

GREYLOCK_URL = "https://greylock.com/portfolio"
GREYLOCK_DOMAIN = "greylock.com"

SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com",
}
SKIP_DOMAINS = {
    "greylock.com", "greylock.altareturn.com",
    "fonts.googleapis.com", "fonts.gstatic.com",
    "gravatar.com", "wordpress.com", "wp.com",
    "feedburner.com", "gmpg.org",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    for s in SOCIAL_DOMAINS | SKIP_DOMAINS | {GREYLOCK_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def fetch_portfolio() -> list[dict]:
    """Scrape Greylock portfolio page and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(GREYLOCK_URL, follow_redirects=True, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Greylock: error fetching portfolio - {e}")
        return []

    # Split on card boundaries: <div class="portfolio-modal-box..." ...>
    card_blocks = re.split(r'<div class="portfolio-modal-box[^"]*"', html)[1:]

    results = []
    seen = set()

    for block in card_blocks:
        # Company name from logo alt: alt="COMPANY NAME Logo"
        name_m = re.search(r'alt="([^"]+?) Logo"', block)
        # External website from icon-link img: alt="icon link"
        url_m = re.search(
            r'href="(https?://(?!greylock)[^"]+)"[^>]*><img[^>]+alt="icon link"',
            block,
        )

        if not (name_m and url_m):
            continue

        name = name_m.group(1).strip()
        href = url_m.group(1)
        parsed = urlparse(href)
        netloc = parsed.netloc

        if not netloc or _is_filtered(netloc):
            continue

        # Skip long paths
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(path_parts) > 2:
            continue

        base = f"{parsed.scheme}://{parsed.netloc}"
        if base in seen:
            continue
        seen.add(base)

        results.append({"company_name": name, "company_website": base})

    print(f"Greylock: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
