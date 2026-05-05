import httpx

from ats.utils import HEADERS, strip_html as _strip_html


def fetch_positions(company_uid: str, token: str) -> list[dict]:
    """
    Fetch open positions from the Comeet public API.
    Returns list of normalized job dicts: {title, location, description, apply_url}.
    Returns [] on error (caller logs).
    """
    url = (
        f"https://www.comeet.co/careers-api/2.0/company/{company_uid}/positions"
        f"?token={token}&details=true"
    )
    try:
        resp = httpx.get(url, timeout=15, headers=HEADERS)
        resp.raise_for_status()
    except Exception as e:
        print(f"    Comeet API error for {company_uid}: {e}")
        return []

    try:
        positions = resp.json()
    except Exception:
        return []

    if not isinstance(positions, list):
        return []

    results = []
    for pos in positions:
        if pos.get("is_internal"):
            continue

        title = pos.get("name", "")
        location = _parse_location(pos.get("location"))
        apply_url = pos.get("url_comeet_hosted_page") or pos.get("url_active_page") or ""

        # details is a list of {name, value} dicts; Description is the main one
        description = ""
        for detail in pos.get("details") or []:
            if detail.get("name", "").lower() == "description":
                description = _strip_html(detail.get("value") or "")
                break
        if not description:
            # Fall back: concat all details
            parts = [_strip_html(d.get("value") or "") for d in (pos.get("details") or [])]
            description = " ".join(p for p in parts if p)

        results.append(
            {
                "title": title,
                "location": location,
                "description": description[:4000],  # cap to avoid huge payloads
                "apply_url": apply_url,
            }
        )

    return results


def _parse_location(loc: dict | None) -> str:
    if not loc:
        return ""
    parts = [loc.get("city"), loc.get("state"), loc.get("country"), loc.get("name")]
    filled = [p for p in parts if p]
    if filled:
        return filled[-1]  # 'name' is usually the most descriptive
    return ""
