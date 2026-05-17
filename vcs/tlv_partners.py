"""
TLV Partners portfolio adapter.

Source-of-truth: jobs.tlv.partners/companies (the active-hiring board).
We parse the Next.js __NEXT_DATA__ blob server-side; this avoids the WAF-blocked
public API and gives us a clean (name, domain) for every actively-hiring company.

The marketing portfolio at www.tlv.partners/portfolio is intentionally NOT used:
it includes acquired/exited companies and serves logos as CSS background-image
strings, which produced garbage names like 'Next.Svg")' in earlier versions.
"""

import json
import re

import httpx

COMPANIES_URL = "https://jobs.tlv.partners/companies"
NEXT_DATA_RE = re.compile(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL)
CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_portfolio() -> list[dict]:
    """
    Return TLV Partners' actively-hiring portfolio as list[{company_name, company_website}].
    Deduplicated by website. Returns [] on any error.
    """
    try:
        resp = httpx.get(
            COMPANIES_URL,
            headers={"User-Agent": CHROME_UA},
            follow_redirects=True,
            timeout=20,
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"TLV Partners: fetch error: {e}")
        return []

    m = NEXT_DATA_RE.search(resp.text)
    if not m:
        print("TLV Partners: no __NEXT_DATA__ in response")
        return []

    try:
        data = json.loads(m.group(1))
        companies = data["props"]["pageProps"]["initialState"]["companies"]["found"]
    except (KeyError, ValueError, TypeError) as e:
        print(f"TLV Partners: unexpected data shape: {e}")
        return []

    if not isinstance(companies, list):
        return []

    results: list[dict] = []
    seen_websites: set[str] = set()

    for c in companies:
        name = (c.get("name") or "").strip()
        domain = (c.get("domain") or "").strip().lstrip("www.").rstrip("/")
        if not name or not domain:
            continue
        website = f"https://{domain}"
        if website in seen_websites:
            continue
        seen_websites.add(website)
        results.append({"company_name": name, "company_website": website})

    print(f"TLV Partners: found {len(results)} actively-hiring portfolio companies")
    return results


if __name__ == "__main__":
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
