"""
Merlin Ventures portfolio adapter.

URL: https://merlin.vc/portfolio/
Structure: server-side rendered WordPress site; portfolio page lists companies with links to
           /companies/[slug]/ detail pages using single-quote attributes (href='...').
           Each detail page exposes the external website URL.
"""
import re
from urllib.parse import urlparse

import httpx

BASE_URL = "https://merlin.vc"
PORTFOLIO_URL = f"{BASE_URL}/portfolio/"
MERLIN_DOMAIN = "merlin.vc"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}
PRESS_DOMAINS = {
    "calcalistech.com", "techcrunch.com", "wired.com", "bloomberg.com",
    "reuters.com", "wsj.com", "forbes.com", "e-channelnews.com",
    "securityweek.com", "darkreading.com", "helpnetsecurity.com",
    "businesswire.com", "prnewswire.com", "globenewswire.com",
}
# Link-tracking / infrastructure domains embedded in the page HTML
INFRA_DOMAINS = {
    "lltrck.com", "fontawesome.com", "kit.fontawesome.com",
    "gmpg.org", "schema.org",
    "cloudfront.net", "amazonaws.com",
}
# Acquirer domains - these appear on acquired-company detail pages
ACQUIRER_DOMAINS = {
    "paloaltonetworks.com", "microsoft.com", "cisco.com", "google.com",
    "amazon.com", "aws.amazon.com", "ibm.com", "crowdstrike.com",
    "zscaler.com", "sentinelone.com", "xmcyber.com",
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
    for s in SOCIAL_DOMAINS | PRESS_DOMAINS | INFRA_DOMAINS | ACQUIRER_DOMAINS | {MERLIN_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def _fetch_company_site(client: httpx.Client, slug: str) -> str | None:
    """Fetch the company detail page and extract the external website URL."""
    try:
        url = f"{BASE_URL}/companies/{slug}/"
        resp = client.get(url, follow_redirects=True, timeout=20)
        if resp.status_code != 200:
            return None
        html = resp.text
        # merlin.vc detail pages use single-quote attributes too
        for m in re.finditer(r"""href=['\"](https?://[^'\"]+)['\"]""", html):
            href = m.group(1)
            parsed = urlparse(href)
            netloc = parsed.netloc
            if not netloc or _is_filtered(netloc):
                continue
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        pass
    return None


def fetch_portfolio() -> list[dict]:
    """Scrape Merlin Ventures portfolio and return list of {company_name, company_website}."""
    try:
        with httpx.Client(headers=HEADERS) as client:
            resp = client.get(PORTFOLIO_URL, follow_redirects=True, timeout=30)
            resp.raise_for_status()
            html = resp.text

            # NOTE: merlin.vc WordPress uses single-quote href attributes (href='...' not href="...")
            # Pattern: href='https://merlin.vc/companies/torq/' title='Torq'
            slug_re = re.compile(
                r"href=['\"](?:https?://merlin\.vc)?/companies/([^'\"/?]+)/?['\"]",
                re.IGNORECASE,
            )
            slugs_seen: set[str] = set()
            slug_name_pairs: list[tuple[str, str]] = []

            for m in slug_re.finditer(html):
                slug = m.group(1)
                if slug not in slugs_seen:
                    slugs_seen.add(slug)
                    # Derive name from slug as default
                    name = slug.replace("-", " ").title()
                    slug_name_pairs.append((slug, name))

            # Improve names from title attributes on the same tag
            # Pattern: href='...companies/slug/?' ... title='CompanyName'
            title_after_re = re.compile(
                r"href=['\"](?:https?://merlin\.vc)?/companies/([^'\"/?]+)/?['\"][^>]*title=['\"]([^'\"]+)['\"]",
                re.IGNORECASE,
            )
            name_overrides: dict[str, str] = {}
            for m in title_after_re.finditer(html):
                slug = m.group(1)
                if slug not in name_overrides:
                    name_overrides[slug] = m.group(2).strip()

            # Also look for title before href on the same tag
            title_before_re = re.compile(
                r"title=['\"]([^'\"]+)['\"][^>]*href=['\"](?:https?://merlin\.vc)?/companies/([^'\"/?]+)/?['\"]",
                re.IGNORECASE,
            )
            for m in title_before_re.finditer(html):
                slug = m.group(2)
                if slug not in name_overrides:
                    name_overrides[slug] = m.group(1).strip()

            results = []
            for slug, default_name in slug_name_pairs:
                name = name_overrides.get(slug, default_name)
                website = _fetch_company_site(client, slug) or ""
                results.append({"company_name": name, "company_website": website})

        print(f"Merlin Ventures: found {len(results)} portfolio companies")
        return results

    except Exception as e:
        print(f"Merlin Ventures: error fetching portfolio - {e}")
        return []


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
