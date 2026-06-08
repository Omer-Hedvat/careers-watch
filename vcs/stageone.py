"""
StageOne Ventures portfolio adapter.

Index URL:  https://www.stageonevc.com/portfolio/
Structure:  Static HTML. Company slugs live at /our-succeses/<slug>/ links on the index.
            Each individual page has an external company website link.
            Two-step fetch: index → slug pages (similar to Aleph adapter).
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

_INDEX_URL = "https://www.stageonevc.com/portfolio/"
_COMPANY_URL = "https://www.stageonevc.com/our-succeses/{slug}/"
_OWN_DOMAIN = "stageonevc.com"

_SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "crunchbase.com",
}
_SKIP_DOMAINS = {
    "medium.com", "techcrunch.com", "forbes.com", "bloomberg.com",
    "wsj.com", "reuters.com", "calcalistech.com", "prnewswire.com",
    "businesswire.com", "globenewswire.com", "wired.com",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    blocked = _SOCIAL_DOMAINS | _SKIP_DOMAINS | {_OWN_DOMAIN}
    return any(clean == s or clean.endswith("." + s) for s in blocked)


def _name_from_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def _get_company_website(slug: str) -> str | None:
    try:
        resp = httpx.get(
            _COMPANY_URL.format(slug=slug),
            headers=HEADERS,
            follow_redirects=True,
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        html = resp.text
        for m in re.finditer(r'href="(https?://[^"]+)"', html):
            href = m.group(1)
            parsed = urlparse(href)
            if not parsed.netloc or _is_filtered(parsed.netloc):
                continue
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception as e:
        print(f"  stageone/{slug}: error - {e}")
    return None


def fetch_portfolio() -> list[dict]:
    """Scrape StageOne Ventures portfolio and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(_INDEX_URL, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"StageOne: error fetching index - {e}")
        return []

    slugs = list(dict.fromkeys(re.findall(r'href="[^"]*our-succeses/([^/"]+)/', html)))

    results = []
    for slug in slugs:
        website = _get_company_website(slug)
        if website:
            name = _name_from_slug(slug)
            results.append({"company_name": name, "company_website": website})
        else:
            print(f"  stageone/{slug}: no website found, skipping")
        time.sleep(0.15)

    print(f"StageOne: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
