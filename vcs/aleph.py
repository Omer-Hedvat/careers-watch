"""
Aleph VC portfolio adapter.

Index URL: https://aleph.vc/companies
Structure: server-side rendered Webflow site.
           Company slugs are extracted from the index; each slug page
           at /companies/<slug> contains the external company website link.
"""
import re
import time
from urllib.parse import urlparse

import httpx

ALEPH_INDEX_URL = "https://aleph.vc/companies"
ALEPH_COMPANY_URL = "https://aleph.vc/companies/{slug}"
ALEPH_DOMAIN = "aleph.vc"

SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com",
}
SKIP_DOMAINS = {
    "medium.com", "aleph.vc", "cdn.prod.website-files.com",
    "fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net",
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
    for s in SOCIAL_DOMAINS | SKIP_DOMAINS | {ALEPH_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def _name_from_domain(netloc: str) -> str:
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def _get_company_website(slug: str) -> str | None:
    """Fetch the individual company page and extract the external website URL."""
    try:
        url = ALEPH_COMPANY_URL.format(slug=slug)
        resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
        if resp.status_code != 200:
            return None
        html = resp.text

        for m in re.finditer(r'href="(https?://[^"]+)"', html):
            href = m.group(1)
            parsed = urlparse(href)
            netloc = parsed.netloc
            if not netloc:
                continue
            if _is_filtered(netloc):
                continue
            # Skip long paths
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc}"
        return None
    except Exception as e:
        print(f"  aleph/{slug}: error - {e}")
        return None


def fetch_portfolio() -> list[dict]:
    """Scrape Aleph VC portfolio and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(ALEPH_INDEX_URL, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text

        slugs = re.findall(r'href="/companies/([^"]+)"', html)
        unique_slugs = list(dict.fromkeys(slugs))
    except Exception as e:
        print(f"Aleph: error fetching index - {e}")
        return []

    results = []
    for slug in unique_slugs:
        website = _get_company_website(slug)
        if website:
            name = _name_from_domain(urlparse(website).netloc)
            results.append({"company_name": name, "company_website": website})
        else:
            print(f"  aleph/{slug}: no website found, skipping")
        time.sleep(0.15)

    print(f"Aleph: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
