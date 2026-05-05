"""
Getro VC job board puller.

Getro's public /api/v2/jobs endpoint is WAF-blocked for server-side requests.
This puller uses the Next.js SSR HTML instead: fetch /jobs with a full Chrome
User-Agent, parse __NEXT_DATA__, and extract initialState.jobs.found.

Limitation: SSR renders ~20 most-recent jobs. The full board is loaded
client-side via a blocked API, so only the latest ~20 are accessible without
a paid Getro API subscription.

Usage: uv run ats/getro.py <board_host>
  e.g. uv run ats/getro.py careers.viola-group.com
"""

import json
import re
import sys

import httpx

CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

NEXT_DATA_RE = re.compile(
    r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
)


def fetch_positions(board_host: str) -> list[dict]:
    """
    Fetch open positions from a Getro VC job board.
    Returns list of normalized dicts: {title, location, description, apply_url, company}.
    Returns [] on error.
    """
    url = f"https://{board_host}/jobs"
    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": CHROME_UA},
            follow_redirects=True,
            timeout=20,
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"    Getro fetch error for {board_host}: {e}")
        return []

    m = NEXT_DATA_RE.search(resp.text)
    if not m:
        print(f"    Getro: no __NEXT_DATA__ in response for {board_host}")
        return []

    try:
        page_data = json.loads(m.group(1))
    except Exception as e:
        print(f"    Getro: JSON parse error for {board_host}: {e}")
        return []

    try:
        state = page_data["props"]["pageProps"]["initialState"]
        jobs_found = state["jobs"]["found"]
        total = state["jobs"].get("total", "?")
    except (KeyError, TypeError) as e:
        print(f"    Getro: unexpected data shape for {board_host}: {e}")
        return []

    if not isinstance(jobs_found, list):
        return []

    print(f"    Getro {board_host}: {len(jobs_found)} SSR jobs (total on board: {total})")

    results = []
    for job in jobs_found:
        title = job.get("title", "")
        url_field = job.get("url", "")
        locations = job.get("locations") or []
        location = ", ".join(locations)
        company = (job.get("organization") or {}).get("name", "")

        results.append(
            {
                "title": title,
                "location": location,
                "description": "",
                "apply_url": url_field,
                "company": company,
            }
        )

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ats/getro.py <board_host>")
        print("  e.g. uv run ats/getro.py careers.viola-group.com")
        sys.exit(1)

    host = sys.argv[1]
    positions = fetch_positions(host)
    print(f"\n{len(positions)} positions from {host}:")
    for p in positions:
        print(f"  [{p['company']}] {p['title']} — {p['location']}")
        print(f"    {p['apply_url']}")
