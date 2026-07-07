"""
Regression tests for the ATS puller hardening audit (P11).

Each test pins a real bug found during the audit: a location string that carried
only a bare city or ISO code and would be silently dropped by an "israel"
location_filter (a plain substring match).
"""

from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Shared helpers (ats/utils.py)
# ---------------------------------------------------------------------------

def test_expand_country_maps_iso_code():
    from ats.utils import expand_country
    assert expand_country("IL") == "Israel"
    assert expand_country("il") == "Israel"
    # Unknown/full names pass through untouched.
    assert expand_country("Israel") == "Israel"
    assert expand_country("") == ""


def test_qualify_location_appends_country_for_iso_code():
    from ats.utils import qualify_location
    # jobs2web-style string with a bare ISO code gains the country name.
    assert qualify_location("Ra'anana, IL, 4366202") == "Ra'anana, IL, 4366202, Israel"
    # Already-qualified strings are left alone.
    assert qualify_location("Tel Aviv, Israel") == "Tel Aviv, Israel"
    # No ISO code present -> unchanged.
    assert qualify_location("Tel Aviv") == "Tel Aviv"
    assert qualify_location("") == ""


# ---------------------------------------------------------------------------
# TeamMe: schema.org address must yield "City, Country", not just one field
# ---------------------------------------------------------------------------

def test_teamme_location_joins_city_and_country():
    from ats.teamme import _location_str
    jp = {
        "jobLocation": {
            "address": {
                "addressLocality": "Tel Aviv",
                "addressCountry": "Israel",
            }
        }
    }
    loc = _location_str(jp)
    assert "Tel Aviv" in loc and "Israel" in loc
    assert "israel" in loc.lower()


def test_teamme_location_expands_iso_country_code():
    from ats.teamme import _location_str
    jp = {"jobLocation": {"address": {"addressLocality": "Tel Aviv", "addressCountry": "IL"}}}
    assert _location_str(jp) == "Tel Aviv, Israel"


def test_teamme_location_dedupes_city_equal_country():
    from ats.teamme import _location_str
    # When only the country is known it must not render "Israel, Israel".
    jp = {"jobLocation": {"address": {"addressCountry": "Israel"}}}
    assert _location_str(jp) == "Israel"


# ---------------------------------------------------------------------------
# Workday: multi-location postings collapse to "N Locations" in the list view;
# the puller must recover the real locations from the detail endpoint.
# ---------------------------------------------------------------------------

def test_workday_expands_collapsed_multi_location():
    list_resp = MagicMock()
    list_resp.raise_for_status.return_value = None
    list_resp.json.return_value = {
        "total": 1,
        "jobPostings": [
            {"title": "Staff ML Engineer", "locationsText": "3 Locations", "externalPath": "/job/x"}
        ],
    }

    detail_resp = MagicMock()
    detail_resp.status_code = 200
    detail_resp.json.return_value = {
        "jobPostingInfo": {
            "jobDescription": "<p>Fraud ML.</p>",
            "location": "United States - Remote",
            "additionalLocations": ["Israel - Tel Aviv", "United Kingdom - London"],
        }
    }

    with patch("httpx.post", return_value=list_resp), patch("httpx.get", return_value=detail_resp):
        from ats.workday import fetch_positions
        results = fetch_positions("acme", "wd1", "External")

    assert len(results) == 1
    # "3 Locations" must be replaced with the real, filter-matchable location set.
    assert "israel" in results[0]["location"].lower()
    assert results[0]["location"] != "3 Locations"


def test_workday_keeps_single_location_from_list():
    list_resp = MagicMock()
    list_resp.raise_for_status.return_value = None
    list_resp.json.return_value = {
        "total": 1,
        "jobPostings": [
            {"title": "DS", "locationsText": "Tel Aviv, Israel", "externalPath": "/job/y"}
        ],
    }
    detail_resp = MagicMock()
    detail_resp.status_code = 200
    detail_resp.json.return_value = {
        "jobPostingInfo": {"jobDescription": "", "location": "Somewhere Else"}
    }

    with patch("httpx.post", return_value=list_resp), patch("httpx.get", return_value=detail_resp):
        from ats.workday import fetch_positions
        results = fetch_positions("acme", "wd1", "External")

    # A concrete single location from the list view is authoritative — not overwritten.
    assert results[0]["location"] == "Tel Aviv, Israel"


# ---------------------------------------------------------------------------
# TalentBrew: must use the shared strip_html (tags + entity whitespace cleaned).
# ---------------------------------------------------------------------------

def test_talentbrew_clean_strips_tags():
    from ats.talentbrew import _clean
    assert _clean("<b>Senior</b>   ML   Engineer") == "Senior ML Engineer"
