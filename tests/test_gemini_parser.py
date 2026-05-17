"""
Tests for the JSON parsing / markdown fence-stripping logic in
matcher/gemini_scorer.py.

The stripping logic (from score_jobs_batch / score_job) is:
    raw = resp.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw)

We test this logic directly using a helper that mirrors it exactly,
then also verify build_prompt / build_batch_prompt output structure.
"""

import json

import pytest

from matcher.gemini_scorer import build_prompt, build_batch_prompt


# ---------------------------------------------------------------------------
# Mirror of the fence-stripping + parse logic used in score_jobs_batch
# ---------------------------------------------------------------------------

def _parse_gemini_response(raw: str):
    """
    Mirrors the fence-stripping + JSON parse logic inside score_jobs_batch.
    Returns parsed object or raises on failure.
    """
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Case 1: Clean JSON string
# ---------------------------------------------------------------------------

def test_clean_json_array():
    raw = '[{"score": 8, "reasoning": "Good fit", "flags": []}]'
    result = _parse_gemini_response(raw)
    assert isinstance(result, list)
    assert result[0]["score"] == 8
    assert result[0]["reasoning"] == "Good fit"


def test_clean_json_object():
    raw = '{"score": 7, "reasoning": "Decent match", "flags": ["location-unclear"]}'
    result = _parse_gemini_response(raw)
    assert isinstance(result, dict)
    assert result["score"] == 7
    assert "location-unclear" in result["flags"]


# ---------------------------------------------------------------------------
# Case 2: JSON wrapped in ```json ... ``` fences
# ---------------------------------------------------------------------------

def test_json_fence_array():
    raw = '```json\n[{"score": 9, "reasoning": "Excellent fit", "flags": ["lead-path-implied"]}]\n```'
    result = _parse_gemini_response(raw)
    assert isinstance(result, list)
    assert result[0]["score"] == 9


def test_json_fence_without_language_tag():
    """Some models emit ``` without 'json' tag."""
    raw = '```\n[{"score": 5, "reasoning": "Partial match", "flags": []}]\n```'
    result = _parse_gemini_response(raw)
    assert isinstance(result, list)
    assert result[0]["score"] == 5


def test_json_fence_object():
    raw = '```json\n{"score": 3, "reasoning": "Wrong domain", "flags": ["wrong-domain"]}\n```'
    result = _parse_gemini_response(raw)
    assert isinstance(result, dict)
    assert result["flags"] == ["wrong-domain"]


def test_json_fence_with_trailing_newlines():
    raw = '```json\n[{"score": 6, "reasoning": "OK fit", "flags": []}]\n\n```'
    result = _parse_gemini_response(raw)
    assert isinstance(result, list)
    assert result[0]["score"] == 6


# ---------------------------------------------------------------------------
# Case 3: Malformed JSON - should raise (caller catches and returns fallback)
# ---------------------------------------------------------------------------

def test_malformed_json_raises():
    raw = "not json at all"
    with pytest.raises(json.JSONDecodeError):
        _parse_gemini_response(raw)


def test_truncated_json_raises():
    raw = '[{"score": 8, "reasoning": "fit"'  # truncated
    with pytest.raises(json.JSONDecodeError):
        _parse_gemini_response(raw)


# ---------------------------------------------------------------------------
# build_prompt structure tests
# ---------------------------------------------------------------------------

def test_build_prompt_contains_job_fields():
    job = {
        "company": "Acme",
        "title": "Data Scientist",
        "location": "Tel Aviv",
        "description": "Build fraud models",
        "apply_url": "https://example.com/job/1",
        "source_vc": "YL Ventures",
        "vc_tier": "tier1",
    }
    prompt = build_prompt(job, profile_md="# Profile", cv_md="# CV")
    assert "Acme" in prompt
    assert "Data Scientist" in prompt
    assert "Tel Aviv" in prompt
    assert "Build fraud models" in prompt
    assert "# Profile" in prompt
    assert "# CV" in prompt


def test_build_batch_prompt_has_all_jobs():
    jobs = [
        {"company": "Alpha", "title": "ML Eng", "location": "TLV", "description": "d1",
         "apply_url": "https://alpha.com/1", "source_vc": "", "vc_tier": ""},
        {"company": "Beta", "title": "Data Sci", "location": "Herzliya", "description": "d2",
         "apply_url": "https://beta.com/1", "source_vc": "", "vc_tier": ""},
    ]
    prompt = build_batch_prompt(jobs, profile_md="# Profile", cv_md="# CV")
    assert 'index="1"' in prompt
    assert 'index="2"' in prompt
    assert "Alpha" in prompt
    assert "Beta" in prompt
    assert "exactly 2 objects" in prompt


def test_build_batch_prompt_single_job():
    jobs = [
        {"company": "Solo", "title": "Researcher", "location": "TA", "description": "d",
         "apply_url": "https://solo.com/1", "source_vc": "", "vc_tier": ""},
    ]
    prompt = build_batch_prompt(jobs, profile_md="# P", cv_md="# C")
    assert "exactly 1 objects" in prompt or "exactly 1 object" in prompt or "1 jobs" in prompt
