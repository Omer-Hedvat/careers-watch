"""
Accel portfolio adapter.

Uses Accel's public Algolia search API (app J60GRWQY2U, index relationships-index).
Filters to the "Europe & Israel" region, active companies only, then keeps Israeli ones.
"""
import httpx

_ALGOLIA_URL = (
    "https://j60grwqy2u-dsn.algolia.net/1/indexes/relationships-index/query"
    "?x-algolia-agent=Algolia%20for%20JavaScript%20(4.22.1)%3B%20Browser%20(lite)"
    "&x-algolia-api-key=83fd461ed9ef96bf7d972a8029970435"
    "&x-algolia-application-id=J60GRWQY2U"
)
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Content-Type": "application/json",
}


def fetch_portfolio() -> list[dict]:
    """Return Accel Europe & Israel active portfolio companies as {company_name, company_website}."""
    try:
        resp = httpx.post(
            _ALGOLIA_URL,
            headers=_HEADERS,
            json={
                "query": "",
                "hitsPerPage": 500,
                "page": 0,
                "facetFilters": [["region:Europe & Israel"]],
                "filters": "current-status:true",
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        from urllib.parse import urlparse

        def _is_israel(hit: dict) -> bool:
            for field in ("location", "headquarters", "sfdc-headquarters"):
                val = (hit.get(field) or "").upper()
                if "ISRAEL" in val or "ISR" in val:
                    return True
            return False

        results = []
        for hit in data.get("hits", []):
            if not _is_israel(hit):
                continue
            name = hit.get("name", "").strip()
            website = (hit.get("website-url") or "").strip().rstrip("/")
            if not name or not website:
                continue
            parsed = urlparse(website)
            base = f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else website
            results.append({"company_name": name, "company_website": base})

        print(f"Accel: found {len(results)} Israeli portfolio companies")
        return results

    except Exception as e:
        print(f"Accel: error fetching portfolio - {e}")
        return []


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
