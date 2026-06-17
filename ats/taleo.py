"""
Taleo (Oracle Taleo Enterprise) ATS puller.

The job list is rendered client-side from a hidden `initialHistory` form field
embedded in the initial page HTML.  Each page holds up to 25 jobs; subsequent
pages are fetched via an AJAX POST to jobsearch.ajax using the CSRF token and
ftlhistory value from the initial page.

Response format: sections delimited by !$!, fields within a section by !|!.
Section 2 of both the initial and AJAX responses holds the job list:
  false !|! false !|! false !|! {id} !|! {title} !|! ... !|! {job_num} !|! {location} !|! ...
  42 fields per job, repeating.

Job detail URLs: https://{host}/careersection/{section}/jobdetail.ftl?job={job_num}
apply_url links to the same detail page; description is not available without
fetching each individual page (expensive) so we leave it empty.
"""
import re
import sys
from urllib.parse import unquote

import httpx

try:
    from ats.utils import HEADERS
except ModuleNotFoundError:
    import os as _os
    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from ats.utils import HEADERS

# Fields per job block in the Taleo job list section.
_JOB_STRIDE = 42
# Within each block (0-based from the block start):
_TITLE_IDX = 1
_JOB_NUM_IDX = 9   # external requisition number (used in apply URL)
_LOCATION_IDX = 10  # format: CC-CC-CityName (e.g. IL-IL-Tel Aviv)

_COUNTRY_CODES = {
    "IL": "Israel", "US": "United States", "IN": "India",
    "IT": "Italy", "FR": "France", "GB": "United Kingdom",
    "DE": "Germany", "AU": "Australia", "SG": "Singapore",
    "CO": "Colombia", "JP": "Japan", "HK": "Hong Kong",
    "NL": "Netherlands", "CA": "Canada", "BR": "Brazil",
}


def _decode_location(raw: str) -> str:
    """
    Convert Taleo location code CC-CC-CityName to 'CityName, CountryName'.
    Falls back to the raw value for unrecognised patterns.
    """
    parts = raw.split("-", 2)
    if len(parts) == 3:
        country_code, _, city = parts
        city = city.strip()
        country = _COUNTRY_CODES.get(country_code, country_code)
        return f"{city}, {country}" if city else country
    return raw.strip()


def _parse_job_section(section: str, apply_base: str) -> list[dict]:
    """
    Parse a job-list section (already split on !$!) into normalized dicts.

    section may be URL-encoded (initialHistory) or plain text (AJAX); this
    function decodes before parsing.
    """
    decoded = unquote(section)
    fields = decoded.split("!|!")

    # Skip the 3-field header (false, false, false)
    start = 0
    for idx, f in enumerate(fields):
        if re.match(r"^\d{4,6}$", f.strip()):
            start = idx
            break
    else:
        return []

    # The minimum fields needed to extract the key data: up to _LOCATION_IDX (offset 10).
    _MIN_FIELDS = _LOCATION_IDX + 1

    jobs = []
    i = start
    while i + _MIN_FIELDS <= len(fields):
        job_id = fields[i].strip()
        if not re.match(r"^\d{4,6}$", job_id):
            break

        title = unquote(fields[i + _TITLE_IDX]).strip()
        job_num = unquote(fields[i + _JOB_NUM_IDX]).strip()
        location_raw = unquote(fields[i + _LOCATION_IDX]).strip()
        location = _decode_location(location_raw)
        apply_url = f"{apply_base}{job_num}"

        jobs.append({"title": title, "location": location,
                     "description": "", "apply_url": apply_url})
        # Advance by full stride; last job in a page may have < STRIDE remaining fields
        i += _JOB_STRIDE
        if i + _MIN_FIELDS > len(fields):
            break

    return jobs


def fetch_positions(host: str, careers_section: str = "ex") -> list[dict]:
    """
    Fetch open positions from a Taleo careers site.

    host:             Taleo subdomain, e.g. radware.taleo.net
    careers_section:  careers-section path segment (default: ex for external)
    """
    base_url = f"https://{host}/careersection/{careers_section}"
    search_url = f"{base_url}/jobsearch.ftl"
    ajax_url = f"{base_url}/jobsearch.ajax"
    apply_base = f"{base_url}/jobdetail.ftl?job="

    try:
        resp = httpx.get(search_url, headers=HEADERS, timeout=20, follow_redirects=True)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"    Taleo fetch error for {host}: {e}")
        return []

    # Extract CSRF token and ftlhistory
    csrf_m = re.search(r'name="csrftoken"[^>]+value="([^"]+)"', html, re.IGNORECASE)
    hist_m = re.search(r'name="ftlhistory"[^>]+value="([^"]+)"', html, re.IGNORECASE)
    if not csrf_m or not hist_m:
        print(f"    Taleo: could not find CSRF or history tokens for {host}")
        return []

    csrf_val = csrf_m.group(1)
    hist_val = hist_m.group(1)

    # Parse page 1 from the embedded initialHistory field
    init_m = re.search(r'name="initialHistory"[^>]+value="([^"]+)"', html, re.IGNORECASE)
    raw_init = init_m.group(1) if init_m else ""
    init_sections = unquote(raw_init).split("!$!")
    results = _parse_job_section(init_sections[2] if len(init_sections) > 2 else "", apply_base)

    # Determine total count
    total_m = re.search(r'listRequisition\.nbElements!\|!(\d+)', html)
    total = int(total_m.group(1)) if total_m else len(results)
    page_size = 25

    # Fetch additional pages via AJAX
    page = 2
    while len(results) < total:
        try:
            r2 = httpx.post(
                ajax_url,
                data={
                    "ftlpageid": "reqListBasicPage",
                    "ftlinterfaceid": "requisitionListInterface",
                    "jsfCmdId": "rlPager_goToPage",
                    "ftlcompid": "rlPager",
                    "ftlcompclass": "Pager",
                    "ftlcallback": "requisitionListInterface_refreshList",
                    "ftlajaxid": "ftlx1",
                    "lang": "en",
                    "ftlhistory": hist_val,
                    "csrftoken": csrf_val,
                    "rlPager.currentPage": str(page),
                    "rlPager.nbDisplayPage": "5",
                    "dropListSize": str(page_size),
                    "serializedCriteria": "19::;;20::;;21::;;",
                },
                headers={**HEADERS, "X-Requested-With": "XMLHttpRequest"},
                timeout=20,
            )
            r2.raise_for_status()
        except Exception as e:
            print(f"    Taleo AJAX page {page} error for {host}: {e}")
            break

        sections = r2.text.split("!$!")
        # Section 2 has the job list; section 1 has rlPager state
        job_section = next(
            (s for s in sections if re.search(r"false!\|!false!\|!false!\|!\d", s)),
            "",
        )
        page_jobs = _parse_job_section(job_section, apply_base)
        if not page_jobs:
            break
        results.extend(page_jobs)
        page += 1
        if page > 20:  # safety cap
            break

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run ats/taleo.py <host> [section]")
        print("  e.g. uv run ats/taleo.py radware.taleo.net ex")
        sys.exit(1)

    host = sys.argv[1]
    section = sys.argv[2] if len(sys.argv) > 2 else "ex"
    print(f"Fetching Taleo postings for: {host} section={section}")
    jobs = fetch_positions(host, section)
    print(f"Found {len(jobs)} job(s)")
    for i, job in enumerate(jobs[:10]):
        print(f"  [{i + 1}] {job['title'][:55]} - {job['location']}")
        print(f"       {job['apply_url'][:80]}")
    if len(jobs) > 10:
        print(f"  ... and {len(jobs) - 10} more")
