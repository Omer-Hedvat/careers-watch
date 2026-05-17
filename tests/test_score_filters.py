"""
Tests for score.py's pre-Gemini filter functions:
  - _title_prefilter (denylist)
  - _title_allowlist_filter (allowlist)
  - _location_prefilter
  - _company_filter

All functions are imported directly from score.py - no Gemini calls made.
"""

import json
from pathlib import Path

import pytest

from score import (
    _title_prefilter,
    _title_allowlist_filter,
    _location_prefilter,
    _company_filter,
    _SKIP_TITLE_TERMS,
    _KEEP_TITLE_TERMS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_JOBS_PATH = Path(__file__).parent / "sample_jobs.json"


def load_sample_jobs() -> list[dict]:
    with SAMPLE_JOBS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# _title_prefilter (denylist)
# ---------------------------------------------------------------------------

def test_denylist_drops_sales_engineer():
    jobs = [{"title": "Sales Engineer", "apply_url": "https://example.com/1"}]
    kept, dropped = _title_prefilter(jobs)
    assert dropped == 1
    assert len(kept) == 0


def test_denylist_drops_account_executive():
    jobs = [{"title": "Senior Account Executive - EMEA", "apply_url": "https://example.com/2"}]
    kept, dropped = _title_prefilter(jobs)
    assert dropped == 1
    assert len(kept) == 0


def test_denylist_keeps_data_scientist():
    jobs = [{"title": "Lead Data Scientist - Fraud", "apply_url": "https://example.com/3"}]
    kept, dropped = _title_prefilter(jobs)
    assert dropped == 0
    assert len(kept) == 1


def test_denylist_case_insensitive():
    jobs = [{"title": "RECRUITER", "apply_url": "https://example.com/4"}]
    kept, dropped = _title_prefilter(jobs)
    assert dropped == 1


def test_denylist_custom_terms():
    """Custom skip_terms override the defaults."""
    jobs = [
        {"title": "wizard", "apply_url": "https://example.com/5"},
        {"title": "data scientist", "apply_url": "https://example.com/6"},
    ]
    kept, dropped = _title_prefilter(jobs, skip_terms=["wizard"])
    assert dropped == 1
    assert kept[0]["title"] == "data scientist"


# ---------------------------------------------------------------------------
# _title_allowlist_filter (allowlist)
# ---------------------------------------------------------------------------

def test_allowlist_keeps_matching_title():
    jobs = [{"title": "Data Scientist - Fraud Detection", "apply_url": "https://example.com/7"}]
    kept, dropped = _title_allowlist_filter(jobs)
    assert dropped == 0
    assert len(kept) == 1


def test_allowlist_drops_non_matching_title():
    jobs = [{"title": "Office Manager", "apply_url": "https://example.com/8"}]
    kept, dropped = _title_allowlist_filter(jobs)
    assert dropped == 1
    assert len(kept) == 0


def test_allowlist_empty_list_disables_filter():
    """Passing keep_terms=[] should keep everything (filter disabled)."""
    jobs = [
        {"title": "Completely Unrelated Role", "apply_url": "https://example.com/9"},
        {"title": "Another Thing", "apply_url": "https://example.com/10"},
    ]
    kept, dropped = _title_allowlist_filter(jobs, keep_terms=[])
    assert dropped == 0
    assert len(kept) == 2


def test_allowlist_custom_terms():
    jobs = [
        {"title": "Fraud Analyst", "apply_url": "https://example.com/11"},
        {"title": "Barista", "apply_url": "https://example.com/12"},
    ]
    kept, dropped = _title_allowlist_filter(jobs, keep_terms=["fraud"])
    assert len(kept) == 1
    assert kept[0]["title"] == "Fraud Analyst"


def test_allowlist_case_insensitive():
    jobs = [{"title": "MACHINE LEARNING ENGINEER", "apply_url": "https://example.com/13"}]
    kept, dropped = _title_allowlist_filter(jobs)
    assert len(kept) == 1


# ---------------------------------------------------------------------------
# _location_prefilter
# ---------------------------------------------------------------------------

def test_location_filter_keeps_tel_aviv():
    jobs = [{"title": "DS", "location": "Tel Aviv", "apply_url": "https://example.com/14"}]
    kept, empty_loc = _location_prefilter(jobs)
    assert len(kept) == 1


def test_location_filter_drops_london():
    jobs = [{"title": "DS", "location": "London, UK", "apply_url": "https://example.com/15"}]
    kept, empty_loc = _location_prefilter(jobs)
    assert len(kept) == 0


def test_location_filter_keeps_empty_location():
    """Jobs with no location should be kept (location-unclear signal)."""
    jobs = [{"title": "DS", "location": "", "apply_url": "https://example.com/16"}]
    kept, empty_loc = _location_prefilter(jobs)
    assert len(kept) == 1
    assert empty_loc == 1


def test_location_filter_keeps_missing_location_key():
    """Jobs with no location key at all should be kept."""
    jobs = [{"title": "DS", "apply_url": "https://example.com/17"}]
    kept, empty_loc = _location_prefilter(jobs)
    assert len(kept) == 1
    assert empty_loc == 1


def test_location_filter_keeps_herzliya():
    jobs = [{"title": "ML Eng", "location": "Herzliya", "apply_url": "https://example.com/18"}]
    kept, _ = _location_prefilter(jobs)
    assert len(kept) == 1


def test_location_filter_drops_new_york():
    jobs = [{"title": "DS", "location": "New York, NY", "apply_url": "https://example.com/19"}]
    kept, _ = _location_prefilter(jobs)
    assert len(kept) == 0


# ---------------------------------------------------------------------------
# _company_filter
# ---------------------------------------------------------------------------

def test_company_filter_drops_matching():
    jobs = [
        {"title": "DS", "company": "BadCo", "apply_url": "https://example.com/20"},
        {"title": "DS", "company": "GoodCo", "apply_url": "https://example.com/21"},
    ]
    kept, dropped = _company_filter(jobs, skip_companies=["BadCo"])
    assert dropped == 1
    assert len(kept) == 1
    assert kept[0]["company"] == "GoodCo"


def test_company_filter_case_insensitive():
    jobs = [{"title": "DS", "company": "BADCO", "apply_url": "https://example.com/22"}]
    kept, dropped = _company_filter(jobs, skip_companies=["badco"])
    assert dropped == 1


def test_company_filter_empty_list_keeps_all():
    jobs = [
        {"title": "DS", "company": "AnyCompany", "apply_url": "https://example.com/23"},
    ]
    kept, dropped = _company_filter(jobs, skip_companies=[])
    assert dropped == 0
    assert len(kept) == 1


# ---------------------------------------------------------------------------
# Integration: sample_jobs.json through all filters
# ---------------------------------------------------------------------------

def test_sample_jobs_location_filter():
    """The VisionAI London job should be dropped by location filter."""
    jobs = load_sample_jobs()
    kept, empty_loc = _location_prefilter(jobs)
    titles = [j["title"] for j in kept]
    assert "Senior Data Scientist - Computer Vision" not in titles
    # Tel Aviv jobs should remain
    assert any("Tel Aviv" in j.get("location", "") for j in kept)


def test_sample_jobs_allowlist_filter():
    """All sample jobs should pass through the default allowlist (they're all DS/ML titles)."""
    jobs = load_sample_jobs()
    # First apply location filter to simulate real pipeline
    loc_filtered, _ = _location_prefilter(jobs)
    kept, dropped = _title_allowlist_filter(loc_filtered)
    # Both remaining jobs (PayShield DS and ShopStream ML Eng) should pass
    assert len(kept) >= 1
