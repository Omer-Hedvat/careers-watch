"""
Insight Partners - Israel portfolio adapter.

URL: https://www.insightpartners.com/portfolio/
Structure: WordPress site with a REST API at /wp-json/insight/v1/get-companies.
           The API requires browser cookies (403 via plain httpx), so Playwright
           is used to establish the session, paginate through all ~845 companies,
           filter to Israel, and then fetch each company's page to get the
           external website URL from the "Learn More About ..." link.
"""
import json
import re
import time
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

INSIGHT_PORTFOLIO_URL = "https://www.insightpartners.com/portfolio/"
INSIGHT_COMPANY_URL = "https://www.insightpartners.com/portfolio/{slug}/"
INSIGHT_DOMAIN = "insightpartners.com"

SKIP_DOMAINS = {
    "insightpartners.com", "go-scale.com", "onetrust.com", "altareturn.com",
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com", "glassdoor.com",
    "bizible.com", "bizibly.com", "google.com", "gstatic.com",
    "googleapis.com", "doubleclick.net", "marketo.com", "mktoresp.com",
    "6sc.co", "segment.io", "ads.linkedin.com",
}


def _is_filtered(url: str) -> bool:
    return any(s in url for s in SKIP_DOMAINS)


def _name_from_domain(netloc: str) -> str:
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def fetch_portfolio() -> list[dict]:
    """
    Scrape Insight Partners Israel portfolio and return list of {company_name, company_website}.
    Uses Playwright to handle cookie-gated API calls.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Establish session with cookies
                page.goto(INSIGHT_PORTFOLIO_URL, wait_until="networkidle", timeout=60000)

                # Paginate through all companies via in-page fetch (uses session cookies)
                all_rows: list[dict] = []
                page_num = 1

                while True:
                    raw = page.evaluate(f"""
                        async () => {{
                            const resp = await fetch(
                                '/wp-json/insight/v1/get-companies?page={page_num}&search=&per_page=50',
                                {{credentials: 'same-origin'}}
                            );
                            return await resp.text();
                        }}
                    """)
                    data = json.loads(json.loads(raw))
                    rows = data.get("rows", [])
                    if not rows:
                        break
                    all_rows.extend(rows)
                    page_num += 1

                # Filter to Israel companies
                israel_rows = [
                    r for r in all_rows
                    if "israel" in r.get("location", "").lower()
                ]

                results = []
                for company in israel_rows:
                    slug = company.get("slug", "")
                    company_name = company.get("name", "")
                    if not slug:
                        continue

                    website = _get_company_website(page, slug)
                    if website:
                        name = company_name or _name_from_domain(urlparse(website).netloc)
                        results.append({"company_name": name, "company_website": website})
                    else:
                        print(f"  insight/{slug}: no website found, skipping")
                    time.sleep(0.15)

            finally:
                page.close()
                browser.close()

        print(f"Insight Partners: found {len(results)} Israel portfolio companies")
        return results

    except Exception as e:
        print(f"Insight Partners: error fetching portfolio - {e}")
        return []


def _get_company_website(page, slug: str) -> str | None:
    """Navigate to a company page and extract the external website URL."""
    try:
        url = INSIGHT_COMPANY_URL.format(slug=slug)
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        html = page.content()

        # Primary pattern: href="..." title="Learn More About COMPANY"
        learn_more = re.search(
            r'href="(https?://[^"]+)"[^>]*title="Learn More About', html
        )
        if learn_more:
            href = learn_more.group(1)
            parsed = urlparse(href)
            return f"{parsed.scheme}://{parsed.netloc}"

        # Fallback: first external non-skip link with short path
        for m in re.finditer(r'href="(https?://[^"]+)"', html):
            href = m.group(1)
            if _is_filtered(href):
                continue
            parsed = urlparse(href)
            netloc = parsed.netloc
            if not netloc:
                continue
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc}"

        return None
    except Exception as e:
        print(f"  insight/{slug}: page error - {e}")
        return None


if __name__ == "__main__":
    import json as _json
    companies = fetch_portfolio()
    print(_json.dumps(companies, ensure_ascii=False, indent=2))
