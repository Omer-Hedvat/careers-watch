"""Skip (hidden_jobs): skip/unskip endpoints, the `skipped` flag on both lists,
_new_pending exclusion, and the fallback before migration 013 is applied.

Run from webapp/backend:  uv run --with pytest python -m pytest tests -q

Supabase is stubbed - no network, no secrets needed.
"""
import sys
import types
from pathlib import Path

import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).parent.parent))

if "db.supabase_client" not in sys.modules:
    _stub = types.ModuleType("db.supabase_client")
    _stub.supabase = types.SimpleNamespace()
    sys.modules["db.supabase_client"] = _stub

from routers import jobs, scoring  # noqa: E402


class _FakeDB:
    """In-memory tables; hidden_jobs is a set of (user_id, apply_url).
    missing=True makes every hidden_jobs call raise, as PostgREST does for an unknown table."""

    def __init__(self, tables=None, hidden=(), missing=False):
        self.tables = tables or {}
        self.hidden = set(hidden)
        self.missing = missing

    def table(self, name):
        if name == "hidden_jobs" and self.missing:
            raise RuntimeError("relation \"hidden_jobs\" does not exist")
        return _Query(self, name)


class _Query:
    def __init__(self, db, name):
        self.db, self.name, self.op, self.payload, self.eqs = db, name, "select", None, {}

    def upsert(self, row, **kw):
        self.op, self.payload = "upsert", row
        return self

    def delete(self):
        self.op = "delete"
        return self

    def eq(self, col, val):
        self.eqs[col] = val
        return self

    def __getattr__(self, name):  # select/order/range - all chain
        return lambda *a, **k: self

    def execute(self):
        db = self.db
        if self.name == "hidden_jobs":
            if self.op == "upsert":
                db.hidden.add((self.payload["user_id"], self.payload["apply_url"]))
            elif self.op == "delete":
                db.hidden.discard((self.eqs["user_id"], self.eqs["apply_url"]))
            data = [{"apply_url": u} for uid, u in db.hidden if uid == self.eqs.get("user_id")]
            return types.SimpleNamespace(data=data)
        return types.SimpleNamespace(data=db.tables.get(self.name, []))


@pytest.fixture
def as_user(monkeypatch):
    monkeypatch.setattr(jobs, "_get_user", lambda a: "user-1")
    monkeypatch.setattr(jobs, "load_filters", lambda uid: {})

    def use(db):
        monkeypatch.setattr(jobs, "supabase", db)
        return db
    return use


def test_skip_is_idempotent_and_unskip_removes(as_user):
    db = as_user(_FakeDB())
    body = jobs.SkipRequest(apply_url="https://x/1")
    assert jobs.skip_job(body, authorization="Bearer t") == {"skipped": True}
    assert jobs.skip_job(body, authorization="Bearer t") == {"skipped": True}
    assert db.hidden == {("user-1", "https://x/1")}
    assert jobs.unskip_job(body, authorization="Bearer t") == {"skipped": False}
    assert db.hidden == set()


def test_skip_requires_url(as_user):
    as_user(_FakeDB())
    with pytest.raises(HTTPException) as e:
        jobs.skip_job(jobs.SkipRequest(apply_url="  "), authorization="Bearer t")
    assert e.value.status_code == 400


def test_list_jobs_flags_skipped(as_user):
    rows = [{"id": "1", "apply_url": "https://x/1", "title": "DS", "location": "", "company": "A"},
            {"id": "2", "apply_url": "https://x/2", "title": "DS", "location": "", "company": "B"}]
    as_user(_FakeDB({"scored_jobs": rows}, hidden={("user-1", "https://x/2"), ("other", "https://x/1")}))
    out = jobs.list_jobs(authorization="Bearer t")
    assert [(r["id"], r["skipped"]) for r in out] == [("1", False), ("2", True)]


def test_list_positions_flags_skipped(as_user):
    rows = [{"company": "A", "title": "DS", "location": "", "apply_url": "https://x/1"},
            {"company": "B", "title": "DS", "location": "", "apply_url": "https://x/2"}]
    as_user(_FakeDB({"positions": rows}, hidden={("user-1", "https://x/1")}))
    out = jobs.list_positions(authorization="Bearer t")
    assert [(r["company"], r["skipped"]) for r in out] == [("A", True), ("B", False)]


def test_missing_table_falls_back(as_user):
    rows = [{"company": "A", "title": "DS", "location": "", "apply_url": "https://x/1"}]
    as_user(_FakeDB({"positions": rows, "scored_jobs": [dict(rows[0], id="1")]}, missing=True))
    assert jobs.hidden_urls("user-1") == set()
    assert jobs.list_positions(authorization="Bearer t")[0]["skipped"] is False
    assert jobs.list_jobs(authorization="Bearer t")[0]["skipped"] is False
    for fn in (jobs.skip_job, jobs.unskip_job):
        with pytest.raises(HTTPException) as e:
            fn(jobs.SkipRequest(apply_url="https://x/1"), authorization="Bearer t")
        assert e.value.status_code == 503


def test_new_pending_excludes_skipped(monkeypatch):
    monkeypatch.setattr(scoring, "load_filters", lambda uid: {})
    monkeypatch.setattr(scoring, "_scored_urls", lambda uid: {"https://x/1"})
    monkeypatch.setattr(scoring, "hidden_urls", lambda uid: {"https://x/2"})
    catalog = [{"apply_url": f"https://x/{i}", "title": "DS", "location": "", "company": "A"} for i in (1, 2, 3)]
    assert [j["apply_url"] for j in scoring._new_pending("user-1", catalog)] == ["https://x/3"]
