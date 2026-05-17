"""
State of Mind Ventures (SOMV) portfolio adapter.

URL: https://www.somv.com/companies
Structure: server-side rendered Webflow CMS page; each company card has a
           "social-btn" anchor pointing directly to the company website.
           Company names are derived from domain (no reliable alt text).
"""
import re
from urllib.parse import urlparse

import httpx

SOMV_URL = "https://www.somv.com/companies"
SOMV_DOMAIN = "somv.com"

SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com",
}
SKIP_DOMAINS = {
    # SOMV own infrastructure
    "somv.com", "cdn.prod.website-files.com", "webflow.io",
    "fonts.googleapis.com", "fonts.gstatic.com",
    # Third-party tools linked from the page
    "getproven.com", "orcainc.com", "app.servc.co.il",
    "medium.com", "somv-beta.webflow.io",
    # Press / acquirers
    "tenable.com", "fortinet.com", "silverfort.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _name_from_domain(netloc: str) -> str:
    """Derive a readable company name from the netloc."""
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    for s in SOCIAL_DOMAINS | SKIP_DOMAINS | {SOMV_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def fetch_portfolio() -> list[dict]:
    """Scrape SOMV portfolio page and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(SOMV_URL, follow_redirects=True, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        html = resp.text

        # Each company has a "social-btn" link pointing to its external website
        # Pattern: <a href="URL" ... class="social-btn ...">
        social_btn_re = re.compile(
            r'<a\s+href="(https?://[^"]+)"[^>]*class="[^"]*social-btn[^"]*"',
            re.IGNORECASE,
        )

        seen = set()
        results = []

        for m in social_btn_re.finditer(html):
            href = m.group(1)
            parsed = urlparse(href)
            netloc = parsed.netloc

            if not netloc:
                continue
            if _is_filtered(netloc):
                continue

            # Skip long paths (article / product pages)
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue

            base = f"{parsed.scheme}://{parsed.netloc}"
            if base in seen:
                continue
            seen.add(base)

            name = _name_from_domain(netloc)
            results.append({"company_name": name, "company_website": base})

        print(f"State of Mind Ventures: found {len(results)} portfolio companies")
        return results

    except Exception as e:
        print(f"State of Mind Ventures: error fetching portfolio - {e}")
        return []


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
