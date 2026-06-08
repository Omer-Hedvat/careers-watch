"""
Qumra Capital portfolio adapter.

URL:       https://qumracapital.com/portfolio/
Structure: WordPress. The portfolio page links to internal /company/<slug>/
           pages; each company page has the external website link.
           Two-step fetch: index -> company pages.
"""
import re
import time
from urllib.parse import urlparse

import httpx

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

_INDEX_URL = "https://qumracapital.com/portfolio/"
_OWN_DOMAIN = "qumracapital.com"

_SKIP_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com",
    "google.com", "googleapis.com", "gstatic.com", "googletagmanager.com",
    "cloudflare.com", "w3.org", "wordpress.com", "wp.com",
    "apple.com", "microsoft.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    blocked = _SKIP_DOMAINS | {_OWN_DOMAIN}
    return any(clean == s or clean.endswith("." + s) for s in blocked)


def _get_company_website(slug: str) -> str | None:
    url = f"https://qumracapital.com/company/{slug}/"
    try:
        resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
        if resp.status_code != 200:
            return None
        for m in re.finditer(r'href="(https?://[^"]+)"', resp.text):
            href = m.group(1).split("?")[0]
            parsed = urlparse(href)
            netloc = parsed.netloc
            if not netloc or _is_filtered(netloc):
                continue
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception as e:
        print(f"  qumra/{slug}: error - {e}")
    return None


def fetch_portfolio() -> list[dict]:
    """Scrape Qumra Capital portfolio and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(_INDEX_URL, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Qumra: error fetching index - {e}")
        return []

    slugs = list(dict.fromkeys(
        re.findall(r'href="https://qumracapital\.com/company/([^/"]+)/"', html)
    ))

    results = []
    for slug in slugs:
        website = _get_company_website(slug)
        if website:
            name = slug.replace("-", " ").title()
            results.append({"company_name": name, "company_website": website})
        else:
            print(f"  qumra/{slug}: no website found, skipping")
        time.sleep(0.15)

    print(f"Qumra: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
