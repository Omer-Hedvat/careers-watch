"""
Tests for refresh_companies.py's merge_big_companies() function.

Key behaviors:
1. New big-companies entry is added to the companies dict.
2. Existing VC-discovered entry is UPDATED by big_companies.yml (big wins).
3. Fields preserved: vc metadata (source_vc, vc_tier) should not be wiped.
4. An entry with no changes does NOT bump last_verified_at / updated_count.
5. Missing big_companies.yml returns (0, 0) without raising.
"""

import io
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from refresh_companies import merge_big_companies


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_companies(*names) -> dict[str, dict]:
    """Build a minimal companies dict from a list of names."""
    return {
        name: {
            "name": name,
            "website": f"https://{name.lower()}.io",
            "source_vc": "YL Ventures",
            "vc_tier": 1,
            "careers_url": f"https://{name.lower()}.comeet.co/jobs",
            "ats": "comeet",
            "ats_params": {"company_uid": "uid", "token": "tok"},
            "category": "cyber",
            "location_filter": None,
            "discovered_at": "2026-01-01T00:00:00Z",
            "last_verified_at": "2026-01-01T00:00:00Z",
            "last_jobs_pulled_at": None,
            "consecutive_failures": 0,
        }
        for name in names
    }


YAML_ONE_NEW = """
- name: NewCo
  website: https://newco.io
  careers_url: https://boards.greenhouse.io/newco
  ats: greenhouse
  ats_params:
    board_token: newco
  category: cyber
  location_filter: israel
"""

YAML_EXISTING_UPDATE = """
- name: ExistingCo
  website: https://existingco.io
  careers_url: https://newurl.greenhouse.io/existingco
  ats: greenhouse
  ats_params:
    board_token: existingco_new
  category: cyber
  location_filter: israel
"""

YAML_NO_CHANGE = """
- name: ExistingCo
  website: https://existingco.io
  careers_url: https://existingco.comeet.co/jobs
  ats: comeet
  ats_params:
    company_uid: uid
    token: tok
  category: cyber
  location_filter: null
"""


# ---------------------------------------------------------------------------
# Test: new entry added
# ---------------------------------------------------------------------------

def test_merge_adds_new_company(tmp_path):
    yml_file = tmp_path / "big_companies.yml"
    yml_file.write_text(YAML_ONE_NEW, encoding="utf-8")

    companies = {}
    with patch("refresh_companies.BIG_COMPANIES_FILE", yml_file):
        new_count, updated_count = merge_big_companies(companies)

    assert new_count == 1
    assert updated_count == 0
    assert "NewCo" in companies
    assert companies["NewCo"]["ats"] == "greenhouse"
    assert companies["NewCo"]["source"] == "big_companies_list"
    assert companies["NewCo"]["location_filter"] == "israel"


# ---------------------------------------------------------------------------
# Test: existing entry updated (big_companies wins)
# ---------------------------------------------------------------------------

def test_merge_updates_existing_company(tmp_path):
    yml_file = tmp_path / "big_companies.yml"
    yml_file.write_text(YAML_EXISTING_UPDATE, encoding="utf-8")

    companies = _make_companies("ExistingCo")
    old_vc = companies["ExistingCo"]["source_vc"]  # should be preserved

    with patch("refresh_companies.BIG_COMPANIES_FILE", yml_file):
        new_count, updated_count = merge_big_companies(companies)

    assert new_count == 0
    assert updated_count == 1
    # big_companies.yml values override VC-discovered values
    assert companies["ExistingCo"]["ats"] == "greenhouse"
    assert companies["ExistingCo"]["careers_url"] == "https://newurl.greenhouse.io/existingco"
    # source is updated to big_companies_list
    assert companies["ExistingCo"]["source"] == "big_companies_list"
    # vc metadata should still be there (merge does not wipe)
    assert companies["ExistingCo"].get("source_vc") == old_vc


# ---------------------------------------------------------------------------
# Test: no change → updated_count == 0
# ---------------------------------------------------------------------------

def test_merge_no_change_not_counted(tmp_path):
    yml_file = tmp_path / "big_companies.yml"
    yml_file.write_text(YAML_NO_CHANGE, encoding="utf-8")

    companies = _make_companies("ExistingCo")

    with patch("refresh_companies.BIG_COMPANIES_FILE", yml_file):
        new_count, updated_count = merge_big_companies(companies)

    assert new_count == 0
    assert updated_count == 0


# ---------------------------------------------------------------------------
# Test: missing file returns (0, 0) without raising
# ---------------------------------------------------------------------------

def test_merge_missing_file_returns_zero_zero(tmp_path):
    non_existent = tmp_path / "does_not_exist.yml"
    companies = {}

    with patch("refresh_companies.BIG_COMPANIES_FILE", non_existent):
        new_count, updated_count = merge_big_companies(companies)

    assert new_count == 0
    assert updated_count == 0
    assert companies == {}


# ---------------------------------------------------------------------------
# Test: multiple entries in YAML - all processed
# ---------------------------------------------------------------------------

YAML_MULTIPLE = """
- name: AlphaCo
  website: https://alphaco.io
  careers_url: https://boards.greenhouse.io/alphaco
  ats: greenhouse
  ats_params:
    board_token: alphaco
  category: cyber
  location_filter: israel

- name: BetaCo
  website: https://betaco.io
  careers_url: https://betaco.comeet.co/jobs
  ats: comeet
  ats_params:
    company_uid: betaco
    token: tok123
  category: fraud
"""


def test_merge_multiple_new_entries(tmp_path):
    yml_file = tmp_path / "big_companies.yml"
    yml_file.write_text(YAML_MULTIPLE, encoding="utf-8")

    companies = {}
    with patch("refresh_companies.BIG_COMPANIES_FILE", yml_file):
        new_count, updated_count = merge_big_companies(companies)

    assert new_count == 2
    assert updated_count == 0
    assert "AlphaCo" in companies
    assert "BetaCo" in companies
    assert companies["BetaCo"]["ats"] == "comeet"
