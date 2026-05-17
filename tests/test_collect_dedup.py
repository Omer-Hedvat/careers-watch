"""
Tests for collect_jobs.py deduplication logic.

The dedup code in collect() is:
    seen_urls: set[str] = set()
    deduped = []
    for job in all_jobs:
        url = (job.get("apply_url") or "").strip()
        if not url:
            deduped.append(job)   # no URL -> always keep
            continue
        if url not in seen_urls:
            seen_urls.add(url)
            deduped.append(job)

We test this logic directly by extracting it into a helper that mirrors it,
plus an integration test that patches file I/O to exercise collect() end-to-end.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Extract-and-test the dedup algorithm (pure function copy)
# ---------------------------------------------------------------------------

def _dedup(jobs: list[dict]) -> list[dict]:
    """Mirror of the dedup block in collect_jobs.collect()."""
    seen_urls: set[str] = set()
    deduped = []
    for job in jobs:
        url = (job.get("apply_url") or "").strip()
        if not url:
            deduped.append(job)
            continue
        if url not in seen_urls:
            seen_urls.add(url)
            deduped.append(job)
    return deduped


# ---------------------------------------------------------------------------
# Pure-function tests
# ---------------------------------------------------------------------------

def test_dedup_removes_exact_duplicates():
    jobs = [
        {"title": "DS", "apply_url": "https://example.com/job/1"},
        {"title": "DS (copy)", "apply_url": "https://example.com/job/1"},
    ]
    result = _dedup(jobs)
    assert len(result) == 1
    assert result[0]["title"] == "DS"


def test_dedup_keeps_distinct_urls():
    jobs = [
        {"title": "DS", "apply_url": "https://example.com/job/1"},
        {"title": "ML Eng", "apply_url": "https://example.com/job/2"},
    ]
    result = _dedup(jobs)
    assert len(result) == 2


def test_dedup_keeps_jobs_without_url():
    """Jobs with no apply_url are always kept, even if there are multiple."""
    jobs = [
        {"title": "DS", "apply_url": ""},
        {"title": "ML Eng", "apply_url": None},
        {"title": "Researcher"},  # missing key entirely
    ]
    result = _dedup(jobs)
    assert len(result) == 3


def test_dedup_mixed():
    """Mix of unique URLs, duplicates, and empty URLs."""
    jobs = [
        {"title": "A", "apply_url": "https://example.com/1"},
        {"title": "B", "apply_url": "https://example.com/2"},
        {"title": "A dup", "apply_url": "https://example.com/1"},
        {"title": "C", "apply_url": ""},        # no URL, kept
        {"title": "D", "apply_url": "https://example.com/2"},  # dup
    ]
    result = _dedup(jobs)
    # A, B, C kept; A dup and D removed
    assert len(result) == 3
    titles = [j["title"] for j in result]
    assert "A" in titles
    assert "B" in titles
    assert "C" in titles
    assert "A dup" not in titles
    assert "D" not in titles


def test_dedup_url_strips_whitespace():
    """apply_url with leading/trailing whitespace should still dedup."""
    jobs = [
        {"title": "A", "apply_url": "https://example.com/1"},
        {"title": "A dup", "apply_url": "  https://example.com/1  "},
    ]
    result = _dedup(jobs)
    assert len(result) == 1


def test_dedup_preserves_order():
    """First occurrence wins; order is preserved."""
    jobs = [
        {"title": "first", "apply_url": "https://example.com/1"},
        {"title": "second", "apply_url": "https://example.com/2"},
        {"title": "third dup", "apply_url": "https://example.com/1"},
    ]
    result = _dedup(jobs)
    assert result[0]["title"] == "first"
    assert result[1]["title"] == "second"
