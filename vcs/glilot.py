"""
Glilot Capital Partners portfolio adapter.

URL: https://glilotcapital.com/companies/
Structure: server-side rendered; each company is an <a href="https://company.com">
           wrapping a logo image. No alt text on images - name is derived from domain.
"""
import re
from urllib.parse import urlparse

import httpx

GLILOT_URL = "https://glilotcapital.com/companies/"
GLILOT_DOMAIN = "glilotcapital.com"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}

# Acquirer / press domains to skip
SKIP_DOMAINS = {
    "paloaltonetworks.com", "adobe.com", "rapid7.com", "varonis.com",
    "ibm.com", "intuit.com", "checkpoint.com", "anaplan.com",
    "microsoft.com", "ginvestclub.com", "mimecast.com",
    # press
    "forbes.com", "techcrunch.com", "wsj.com", "reuters.com", "bloomberg.com",
    "calcalistech.com", "prnewswire.com", "businesswire.com",
    # hosting / infrastructure (not portfolio companies)
    "fiscloudservices.com",
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
    for s in SOCIAL_DOMAINS | SKIP_DOMAINS | {GLILOT_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def _name_from_domain(netloc: str) -> str:
    """Derive a readable company name from the netloc."""
    # Strip www. prefix, take the first label, title-case it
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def fetch_portfolio() -> list[dict]:
    """Scrape Glilot Capital portfolio page and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(GLILOT_URL, follow_redirects=True, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        html = resp.text

        # Each company is an <a href="https://...">...</a> wrapping a logo image
        href_re = re.compile(r'<a\s+[^>]*href="(https?://[^"]+)"[^>]*>', re.IGNORECASE)

        seen = set()
        results = []

        for m in href_re.finditer(html):
            href = m.group(1)
            parsed = urlparse(href)
            netloc = parsed.netloc

            if not netloc:
                continue
            if _is_filtered(netloc):
                continue
            # Skip long paths (article / product pages), allow up to 2 path parts
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue

            base = f"{parsed.scheme}://{parsed.netloc}"
            if base in seen:
                continue
            seen.add(base)

            name = _name_from_domain(netloc)
            results.append({"company_name": name, "company_website": base})

        print(f"Glilot Capital: found {len(results)} portfolio companies")
        return results

    except Exception as e:
        print(f"Glilot Capital: error fetching portfolio - {e}")
        return []


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
