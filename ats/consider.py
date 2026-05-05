"""
Consider VC job board puller.

Consider (consider.com) is a talent platform used by several VC funds.
The public search API is:
  POST https://consider.com/api-boards/search-jobs
  Body: {"meta":{"size":N},"board":{"id":board_id,"isParent":true},
         "query":{"promoteFeatured":false},"grouped":false}
  Response: {"jobs":[...], "total":N, "meta":{...}}

Usage: uv run ats/consider.py <board_id>
  e.g. uv run ats/consider.py jvp
"""

import json
import sys

import httpx

try:
    from ats.utils import HEADERS
except ModuleNotFoundError:
    import os as _os
    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from ats.utils import HEADERS

API_URL = "https://consider.com/api-boards/search-jobs"
PAGE_SIZE = 500


def fetch_positions(board_id: str) -> list[dict]:
    """
    Fetch open positions from a Consider VC board.
    Returns list of normalized dicts: {title, location, description, apply_url, company}.
    Returns [] on error.
    """
    results = []
    cursor = None
    fetched = 0

    while True:
        payload: dict = {
            "meta": {"size": PAGE_SIZE},
            "board": {"id": board_id, "isParent": True},
            "query": {"promoteFeatured": False},
            "grouped": False,
        }
        if cursor:
            payload["meta"]["after"] = cursor

        try:
            resp = httpx.post(
                API_URL,
                json=payload,
                headers={**HEADERS, "Content-Type": "application/json"},
                timeout=20,
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"    Consider API error for board '{board_id}': {e}")
            return results

        try:
            data = resp.json()
        except Exception:
            print(f"    Consider: JSON parse error for board '{board_id}'")
            return results

        jobs = data.get("jobs")
        if not isinstance(jobs, list):
            break

        for job in jobs:
            title = job.get("title", "")
            company = job.get("companyName", "")
            locations = job.get("locations") or []
            location = ", ".join(locations)
            apply_url = job.get("applyUrl") or job.get("url", "")

            results.append(
                {
                    "title": title,
                    "location": location,
                    "description": "",
                    "apply_url": apply_url,
                    "company": company,
                }
            )

        fetched += len(jobs)
        total = data.get("total", 0)
        new_cursor = (data.get("meta") or {}).get("sequence")

        if fetched >= total or not new_cursor or new_cursor == cursor:
            break
        cursor = new_cursor

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ats/consider.py <board_id>")
        print("  e.g. uv run ats/consider.py jvp")
        sys.exit(1)

    board = sys.argv[1]
    positions = fetch_positions(board)
    print(f"\n{len(positions)} positions from Consider board '{board}':")
    for p in positions:
        print(f"  [{p['company']}] {p['title']} — {p['location']}")
        print(f"    {p['apply_url']}")
