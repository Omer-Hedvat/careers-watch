"""
Sequoia Capital portfolio adapter (global, no Israel-specific filter).

URL: https://sequoiacap.com/our-companies/
Structure: WordPress + FacetWP site.  The "All" tab in the company listing
           table pre-renders up to ~52 companies with name and post_id.
           Each company's external website is loaded via an AJAX call to
           wp-admin/admin-ajax.php with action=load_company_content.
           No Israel-specific filter is available; all listed companies are
           returned and the ATS-detect step handles irrelevance downstream.
"""
import re
import time
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

SEQUOIA_URL = "https://sequoiacap.com/our-companies/"
SEQUOIA_DOMAIN = "sequoiacap.com"

SOCIAL_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com",
    "instagram.com", "youtube.com",
}
SKIP_DOMAINS = {
    "sequoiacap.com", "wp-content", "wp-includes", "wp-admin",
    "fonts.googleapis.com", "fonts.gstatic.com", "gmpg.org",
    "pixel.wp.com", "stats.wp.com", "cdn.segment.com",
    "parsely.com", "analytics",
}


def _is_filtered(url: str, netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    if any(s in clean for s in SOCIAL_DOMAINS):
        return True
    if any(s in url for s in SKIP_DOMAINS):
        return True
    if SEQUOIA_DOMAIN in clean:
        return True
    return False


def _name_from_domain(netloc: str) -> str:
    host = netloc.lower().lstrip("www.")
    label = host.split(".")[0]
    return label.replace("-", " ").title()


def fetch_portfolio() -> list[dict]:
    """
    Scrape Sequoia Capital portfolio and return list of {company_name, company_website}.
    Uses Playwright to handle session-authenticated AJAX calls.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(SEQUOIA_URL, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)

                # Extract nonce from page
                html = page.content()
                nonce_m = re.search(r'"nonce":"([^"]+)"', html)
                nonce = nonce_m.group(1) if nonce_m else ""

                # Click All tab to render the company table
                try:
                    page.click('[href="#all-panel"]')
                    page.wait_for_timeout(2000)
                except Exception:
                    pass

                html = page.content()

                # Extract (post_id, company_name) pairs from table rows
                # Rows: <tr ... data-target="#company_listing-ID"> ... <th>COMPANY NAME</th>
                row_pairs: list[tuple[str, str]] = []
                seen_ids: set[str] = set()

                for block in re.split(r"<tr\s+", html)[1:]:
                    target_m = re.search(r'data-target="#company_listing-(\d+)"', block)
                    name_m = re.search(
                        r'<th\s+scope="row"[^>]*>([^<]+)</th>', block
                    )
                    if target_m and name_m:
                        post_id = target_m.group(1)
                        name = name_m.group(1).strip()
                        if post_id not in seen_ids:
                            seen_ids.add(post_id)
                            row_pairs.append((post_id, name))

                results = []
                for post_id, company_name in row_pairs:
                    website = _fetch_company_website(page, post_id, nonce)
                    if website:
                        results.append(
                            {"company_name": company_name, "company_website": website}
                        )
                    else:
                        print(f"  sequoia/{company_name}: no website found, skipping")
                    time.sleep(0.1)

            finally:
                page.close()
                browser.close()

        print(f"Sequoia: found {len(results)} portfolio companies")
        return results

    except Exception as e:
        print(f"Sequoia: error fetching portfolio - {e}")
        return []


def _fetch_company_website(page, post_id: str, nonce: str) -> str | None:
    """Load company detail via AJAX and extract the external website URL."""
    try:
        raw = page.evaluate(f"""
            async () => {{
                const resp = await fetch('/wp-admin/admin-ajax.php', {{
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                    body: 'action=load_company_content&post_id={post_id}&nonce={nonce}'
                }});
                return await resp.text();
            }}
        """)

        for m in re.finditer(r'href="(https?://[^"]+)"', raw):
            href = m.group(1)
            parsed = urlparse(href)
            netloc = parsed.netloc
            if not netloc:
                continue
            if _is_filtered(href, netloc):
                continue
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) > 2:
                continue
            return f"{parsed.scheme}://{parsed.netloc}"
        return None
    except Exception as e:
        print(f"  sequoia/{post_id}: AJAX error - {e}")
        return None


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
