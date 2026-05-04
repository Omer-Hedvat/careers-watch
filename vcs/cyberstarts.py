"""
Cyberstarts VC portfolio adapter.

URL: https://www.cyberstarts.com/portfolio
Structure: server-side rendered; portfolio page lists companies with internal links
           to /companies/[slug]. Each company detail page exposes an external website link.
"""
import re
from urllib.parse import urlparse

import httpx

BASE_URL = "https://www.cyberstarts.com"
PORTFOLIO_URL = f"{BASE_URL}/portfolio"
CYBERSTARTS_DOMAIN = "cyberstarts.com"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}

# CDN / hosting / infrastructure domains that appear in page HTML but are not company websites
CDN_DOMAINS = {
    "website-files.com", "webflow.com", "webflow.io",
    "cloudfront.net", "amazonaws.com", "cloudflare.com",
    "googleapis.com", "gstatic.com", "google.com",
    "youtube.com", "vimeo.com",
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
    for s in SOCIAL_DOMAINS | CDN_DOMAINS | {CYBERSTARTS_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def _fetch_company_site(client: httpx.Client, slug: str) -> str | None:
    """Fetch the company detail page and extract the external website URL."""
    try:
        url = f"{BASE_URL}/companies/{slug}"
        resp = client.get(url, follow_redirects=True, timeout=20)
        if resp.status_code != 200:
            return None
        html = resp.text
        # Look for external links (not cyberstarts.com, not social)
        for m in re.finditer(r'href="(https?://[^"]+)"', html):
            href = m.group(1)
            parsed = urlparse(href)
            netloc = parsed.netloc
            if not netloc or _is_filtered(netloc):
                continue
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc.lower()}"
    except Exception:
        pass
    return None


def fetch_portfolio() -> list[dict]:
    """Scrape Cyberstarts portfolio and return list of {company_name, company_website}."""
    try:
        with httpx.Client(headers=HEADERS) as client:
            resp = client.get(PORTFOLIO_URL, follow_redirects=True, timeout=30)
            resp.raise_for_status()
            html = resp.text

            # Extract internal company slugs: href="/companies/[slug]" or href contains company name
            # Pattern: <a href="/companies/[slug]"> or links with h3 text nearby
            slug_re = re.compile(r'href="/companies/([^"/?]+)"')
            slugs_seen = set()
            slugs = []
            for m in slug_re.finditer(html):
                slug = m.group(1)
                if slug not in slugs_seen:
                    slugs_seen.add(slug)
                    slugs.append(slug)

            # Also try to extract company names from h3 tags alongside the slugs
            # Pattern: find h3 content near each slug occurrence
            name_map: dict[str, str] = {}
            # Try to find <h3>CompanyName</h3> patterns
            h3_re = re.compile(r'<h3[^>]*>\s*([^<]+?)\s*</h3>', re.IGNORECASE)
            h3_names = [m.group(1).strip() for m in h3_re.finditer(html)]

            # Match names to slugs by order of appearance (they're usually co-located)
            for i, slug in enumerate(slugs):
                # Derive name from slug as fallback
                name = slug.replace("-", " ").title()
                # Try to find a matching h3 name
                slug_lower = slug.lower().replace("-", "")
                for h3 in h3_names:
                    h3_lower = h3.lower().replace(" ", "").replace("-", "")
                    if h3_lower == slug_lower or slug_lower.startswith(h3_lower[:4]):
                        name = h3
                        break
                name_map[slug] = name

            results = []
            for slug in slugs:
                website = _fetch_company_site(client, slug)
                if website:
                    results.append({
                        "company_name": name_map.get(slug, slug.replace("-", " ").title()),
                        "company_website": website,
                    })

        print(f"Cyberstarts: found {len(results)} portfolio companies")
        return results

    except Exception as e:
        print(f"Cyberstarts: error fetching portfolio - {e}")
        return []


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
