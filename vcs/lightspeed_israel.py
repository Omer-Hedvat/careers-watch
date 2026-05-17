"""
Lightspeed Venture Partners - Israel portfolio adapter.

URL: https://lsvp.com/companies?location=israel
Structure: server-side rendered WordPress site.  The ?location=israel query
           parameter filters the company list to ~41 Israel-related companies.
           Company names are extracted from <h5> elements; external websites
           are fetched from individual company pages at /company/<slug>/.
"""
import re
import time
from urllib.parse import urlparse

import httpx

LSVP_ISRAEL_URL = "https://lsvp.com/companies?location=israel"
LSVP_COMPANY_URL = "https://lsvp.com/company/{slug}/"
LSVP_DOMAIN = "lsvp.com"

SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "tiktok.com",
}
SKIP_DOMAINS = {
    "lsvp.com", "wp-content", "fonts.googleapis.com", "fonts.gstatic.com",
    "cdn.", "fiscloudservices.com", "lighthouse.lsvp.com", "jobs.lsvp.com",
    "medium.com", "faction.vc", "gmpg.org", "feedburner.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _is_filtered(url: str, netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    if any(s in clean for s in SOCIAL_DOMAINS):
        return True
    if any(s in url for s in SKIP_DOMAINS):
        return True
    if LSVP_DOMAIN in clean:
        return True
    return False


def _name_from_domain(netloc: str) -> str:
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def _get_company_website(slug: str) -> str | None:
    """Fetch the company page and extract the external website URL."""
    try:
        url = LSVP_COMPANY_URL.format(slug=slug)
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
            if _is_filtered(href, netloc):
                continue
            # Skip long paths
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc}"
        return None
    except Exception as e:
        print(f"  lightspeed/{slug}: error - {e}")
        return None


def fetch_portfolio() -> list[dict]:
    """
    Scrape Lightspeed Israel portfolio and return list of {company_name, company_website}.
    """
    try:
        resp = httpx.get(
            LSVP_ISRAEL_URL, headers=HEADERS, follow_redirects=True, timeout=30
        )
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Lightspeed Israel: error fetching index - {e}")
        return []

    # Parse (company_id, name) pairs from list items
    # Each company: <li data-company-id="slug"...> ... <h5>Company Name</h5>
    li_blocks = re.split(r"<li\s+", html)

    seen_ids: set[str] = set()
    slug_name_pairs: list[tuple[str, str]] = []

    for block in li_blocks[1:]:
        id_m = re.search(r'data-company-id="([^"]+)"', block)
        name_m = re.search(r"<h5[^>]*>\s*([^<\n]+?)\s*</h5>", block)
        if id_m and name_m:
            company_id = id_m.group(1)
            name = name_m.group(1).strip()
            if company_id not in seen_ids:
                seen_ids.add(company_id)
                slug_name_pairs.append((company_id, name))

    results = []
    for slug, name in slug_name_pairs:
        website = _get_company_website(slug)
        if website:
            results.append({"company_name": name, "company_website": website})
        else:
            print(f"  lightspeed/{slug}: no website found, skipping")
        time.sleep(0.1)

    print(f"Lightspeed Israel: found {len(results)} portfolio companies")
    return results


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
