"""
One-off script: extract Comeet company_uid and token from self-hosted careers pages.

Run: uv run python3 scripts/extract_comeet_tokens.py
"""
import re
from playwright.sync_api import sync_playwright

# Use specific job listing pages - Comeet embed is guaranteed to be active there
TARGETS = {
    "Lusha":         "https://www.lusha.com/careers/co/tel-aviv/6F.26C/senior-bi-data-engineer/",
    "Kaltura":       "https://corp.kaltura.com/careers/account-manager/59.B68/",
    "AU10TIX":       "https://www.au10tix.com/position/8C.866/",
    "Duve":          "https://duve.com/career/co/ramat-gan-office/9C.869/ai-team-lead/all/",
    "Bright Data":   "https://brightdata.com/careers/cyber-security-engineer",
    "Deep Instinct": "https://www.deepinstinct.com/pdf/account-executive-new-york",
}

# Patterns to search for in HTML and intercepted URLs
_PATTERNS = [
    re.compile(r"comeet\.co/careers-api/[^/]+/company/([^/\?]+)/positions\?token=([^&\s\"']+)"),
    re.compile(r"comeet\.co/careers-api/[^/]+/company/([^/\?]+)"),
    re.compile(r"comeet\.com/jobs/([^/\"']+)/([0-9A-Fa-f]+\.[0-9A-Fa-f]+)"),
    re.compile(r"[\"']company[_-]uid[\"']\s*[:=]\s*[\"']([^\"']+)[\"']"),
    re.compile(r"[\"']comet[_-]?token[\"']\s*[:=]\s*[\"']([0-9A-Fa-f]+\.[0-9A-Fa-f]+)[\"']"),
    re.compile(r"company[_-]uid\s*=\s*[\"']?([a-z0-9_-]+)[\"']?", re.IGNORECASE),
    re.compile(r"data-comeet-uid=[\"']([^\"']+)[\"']"),
    re.compile(r"data-token=[\"']([0-9A-Fa-f]+\.[0-9A-Fa-f]+)[\"']"),
]


def scan(text: str, company: str) -> dict | None:
    for pat in _PATTERNS:
        m = pat.search(text)
        if m:
            print(f"  [{company}] pattern match: {m.group(0)[:120]}")
            return {"match": m.group(0), "groups": m.groups()}
    return None


def run_company(page, company: str, url: str) -> str:
    intercepted: list[str] = []

    def on_request(req):
        if "comeet" in req.url.lower():
            intercepted.append(req.url)
            print(f"  [{company}] intercepted: {req.url[:120]}")

    page.on("request", on_request)
    try:
        page.goto(url, wait_until="load", timeout=25000)
        page.wait_for_timeout(4000)
        # Scroll to force lazy embeds
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

        html = page.content()

        result = scan(html, company)
        if result:
            return f"HTML match: {result}"

        for req_url in intercepted:
            result = scan(req_url, company)
            if result:
                return f"Request match: {result}"

        if intercepted:
            return f"Comeet requests found but no pattern matched: {intercepted[:3]}"

        # Last resort: dump comeet-related lines
        comeet_lines = [l.strip() for l in html.split("\n") if "comeet" in l.lower()][:5]
        if comeet_lines:
            return f"Comeet lines found: {comeet_lines}"

        return "NOT FOUND"
    except Exception as e:
        return f"ERROR: {e}"
    finally:
        page.remove_listener("request", on_request)


def main():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for company, url in TARGETS.items():
            print(f"\n--- {company} ---")
            page = browser.new_page()
            result = run_company(page, company, url)
            results[company] = result
            page.close()
        browser.close()

    print("\n\n=== SUMMARY ===")
    for company, result in results.items():
        print(f"{company}: {result}")


if __name__ == "__main__":
    main()
