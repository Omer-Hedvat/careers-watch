"""
Tests that each ATS puller returns dicts with the required schema keys:
  title, location, description, apply_url
No live HTTP calls - all responses are mocked.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {"title", "location", "description", "apply_url"}


def _assert_schema(results: list[dict]) -> None:
    assert isinstance(results, list), "puller must return a list"
    for job in results:
        assert isinstance(job, dict), "each item must be a dict"
        missing = REQUIRED_KEYS - job.keys()
        assert not missing, f"job missing keys: {missing} — job={job}"


# ---------------------------------------------------------------------------
# Comeet
# ---------------------------------------------------------------------------

COMEET_API_RESPONSE = [
    {
        "name": "Data Scientist",
        "is_internal": False,
        "location": {"city": "Tel Aviv", "country": "Israel", "name": "Tel Aviv, Israel"},
        "url_comeet_hosted_page": "https://example.comeet.co/jobs/abc",
        "details": [
            {"name": "Description", "value": "<p>Some job description</p>"},
        ],
    },
    {
        "name": "Internal Role",
        "is_internal": True,
        "location": {"name": "Remote"},
        "url_comeet_hosted_page": "https://example.comeet.co/jobs/internal",
        "details": [],
    },
]


def test_comeet_schema():
    mock_resp = MagicMock()
    mock_resp.json.return_value = COMEET_API_RESPONSE
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.get", return_value=mock_resp):
        from ats.comeet import fetch_positions
        results = fetch_positions("uid123", "tok456")

    # Internal role should be filtered out
    assert len(results) == 1
    _assert_schema(results)
    assert results[0]["title"] == "Data Scientist"
    assert "Tel Aviv" in results[0]["location"]


def test_comeet_empty_response():
    """Empty list from API should return empty list, not raise."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = []
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.get", return_value=mock_resp):
        from ats.comeet import fetch_positions
        results = fetch_positions("uid123", "tok456")

    assert results == []


def test_comeet_api_error():
    """HTTP error should return [] not raise."""
    with patch("httpx.get", side_effect=Exception("connection refused")):
        from ats.comeet import fetch_positions
        results = fetch_positions("uid123", "tok456")

    assert results == []


# ---------------------------------------------------------------------------
# Greenhouse
# ---------------------------------------------------------------------------

GREENHOUSE_API_RESPONSE = {
    "jobs": [
        {
            "title": "Security Researcher",
            "location": {"name": "Tel Aviv"},
            "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
            "content": "<p>Hunt threats. Build detections.</p>",
        }
    ]
}


def test_greenhouse_schema():
    mock_resp = MagicMock()
    mock_resp.json.return_value = GREENHOUSE_API_RESPONSE
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.get", return_value=mock_resp):
        from ats.greenhouse import fetch_positions
        results = fetch_positions("acme")

    assert len(results) == 1
    _assert_schema(results)
    assert results[0]["title"] == "Security Researcher"
    assert results[0]["apply_url"] == "https://boards.greenhouse.io/acme/jobs/123"


def test_greenhouse_api_error():
    """HTTP error should return [] not raise."""
    with patch("httpx.get", side_effect=Exception("timeout")):
        from ats.greenhouse import fetch_positions
        results = fetch_positions("acme")

    assert results == []


def test_greenhouse_malformed_response():
    """Non-dict response should return []."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = "not a dict"
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.get", return_value=mock_resp):
        from ats.greenhouse import fetch_positions
        results = fetch_positions("acme")

    assert results == []


# ---------------------------------------------------------------------------
# Lever
# ---------------------------------------------------------------------------

LEVER_API_RESPONSE = [
    {
        "text": "ML Engineer",
        "categories": {"location": "Herzliya, Israel"},
        "hostedUrl": "https://jobs.lever.co/company/abc123",
        "descriptionPlain": "Build fraud models at scale.",
        "description": "<p>Build fraud models at scale.</p>",
    }
]


def test_lever_schema():
    mock_resp = MagicMock()
    mock_resp.json.return_value = LEVER_API_RESPONSE
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.get", return_value=mock_resp):
        from ats.lever import fetch_positions
        results = fetch_positions("company")

    assert len(results) == 1
    _assert_schema(results)
    assert results[0]["title"] == "ML Engineer"
    assert results[0]["location"] == "Herzliya, Israel"
    # Prefers plain text description
    assert results[0]["description"] == "Build fraud models at scale."


def test_lever_api_error():
    """HTTP error should return [] not raise."""
    with patch("httpx.get", side_effect=Exception("timeout")):
        from ats.lever import fetch_positions
        results = fetch_positions("company")

    assert results == []
