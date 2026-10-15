"""Kept CV / profile files: upload, signed link, /user/me metadata, account delete.

Run from webapp/backend:  uv run --with pytest python -m pytest tests -q
Supabase (tables + storage) is stubbed - no network, no secrets needed.
"""
import base64
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

from routers import user  # noqa: E402


class _Bucket:
    def __init__(self, fail=False):
        self.objects, self.removed, self.fail = {}, [], fail

    def upload(self, path, data, opts):
        if self.fail:
            raise RuntimeError("bucket not found")
        self.objects[path] = (data, opts)

    def remove(self, paths):
        self.removed += paths

    def create_signed_url(self, path, seconds):
        return {"signedURL": f"https://example.supabase.co/storage/v1/object/sign/user-files/{path}?token=t"}


class _Users:
    """users table: select returns `row`; update merges into it; select may raise."""

    def __init__(self, row, select_fails=False, exists=True):
        self.row, self.select_fails, self.exists, self._op = row, select_fails, exists, None

    def select(self, *a):
        self._op = "select"
        return self

    def update(self, fields):
        self._op = "update"
        self.row = {**self.row, **fields}
        return self

    def delete(self):
        self._op = "delete"
        return self

    def __getattr__(self, name):  # eq / maybe_single chain
        return lambda *a, **k: self

    def execute(self):
        if self._op == "select" and self.select_fails:
            raise RuntimeError('column users.cv_file does not exist')
        if self._op == "update" and not self.exists:
            return types.SimpleNamespace(data=[])
        return types.SimpleNamespace(data=self.row)


def _setup(monkeypatch, row=None, fail=False, select_fails=False, exists=True):
    users, bucket = _Users(row or {}, select_fails, exists), _Bucket(fail)
    sb = types.SimpleNamespace(table=lambda n: users,
                               storage=types.SimpleNamespace(from_=lambda b: bucket))
    monkeypatch.setattr(user, "supabase", sb)
    monkeypatch.setattr(user, "require_user", lambda a: "user-1")
    return users, bucket


def _upload(kind="cv", name="My CV.docx", data=b"PK\x03\x04docx"):
    body = user.FileUpload(file_b64=base64.b64encode(data).decode(), name=name)
    return user.upload_file(kind, body, authorization="Bearer good")


def test_upload_keeps_file_and_records_meta(monkeypatch):
    users, bucket = _setup(monkeypatch)
    out = _upload()
    assert set(out) == {"name", "size", "uploaded_at"} and out["name"] == "My CV.docx"
    assert list(bucket.objects) == ["user-1/cv.docx"]
    assert users.row["cv_file"]["path"] == "user-1/cv.docx"


def test_reupload_with_new_extension_removes_old_object(monkeypatch):
    users, bucket = _setup(monkeypatch, {"cv_file": {"path": "user-1/cv.pdf", "name": "cv.pdf"}})
    _upload(name="cv.docx")
    assert bucket.removed == ["user-1/cv.pdf"]


def test_upload_rejects_unknown_kind_type_and_size(monkeypatch):
    _setup(monkeypatch)
    for kwargs, code in [({"kind": "photo"}, 404), ({"name": "x.exe"}, 422),
                         ({"data": b"x" * (user.MAX_FILE_BYTES + 1)}, 413)]:
        with pytest.raises(HTTPException) as e:
            _upload(**kwargs)
        assert e.value.status_code == code


def test_filename_cannot_escape_the_user_folder(monkeypatch):
    users, bucket = _setup(monkeypatch)
    _upload(name="../../other-user/cv.pdf")
    assert list(bucket.objects) == ["user-1/cv.pdf"]
    assert users.row["cv_file"]["name"] == "cv.pdf"


def test_storage_failure_is_a_clear_503(monkeypatch):
    _setup(monkeypatch, fail=True)
    with pytest.raises(HTTPException) as e:
        _upload()
    assert e.value.status_code == 503


def test_file_link_is_signed_and_404_without_file(monkeypatch):
    _setup(monkeypatch, {"profile_file": {"path": "user-1/profile.md", "name": "profile.md"}})
    out = user.file_link("profile", authorization="Bearer good")
    assert out["url"].startswith("https://") and "token=" in out["url"]
    with pytest.raises(HTTPException) as e:
        user.file_link("cv", authorization="Bearer good")
    assert e.value.status_code == 404


def test_meta_hides_path_and_survives_missing_migration(monkeypatch):
    _setup(monkeypatch, {"cv_file": {"path": "user-1/cv.pdf", "name": "cv.pdf", "size": 3, "uploaded_at": "t"}})
    assert user._file_meta("user-1") == {"cv_file": {"name": "cv.pdf", "size": 3, "uploaded_at": "t"}}
    _setup(monkeypatch, select_fails=True)
    assert user._file_meta("user-1") == {}


def test_delete_account_removes_kept_files(monkeypatch):
    users, bucket = _setup(monkeypatch, {"cv_file": {"path": "user-1/cv.pdf"}, "profile_file": {"path": "user-1/profile.md"}})
    monkeypatch.setattr(user.supabase, "auth", types.SimpleNamespace(admin=types.SimpleNamespace(delete_user=lambda uid: None)), raising=False)
    user.delete_account(authorization="Bearer good")
    assert sorted(bucket.removed) == ["user-1/cv.pdf", "user-1/profile.md"]


def test_upload_without_users_row_is_409_and_leaves_no_object(monkeypatch):
    _, bucket = _setup(monkeypatch, exists=False)
    with pytest.raises(HTTPException) as e:
        _upload()
    assert e.value.status_code == 409
    assert bucket.removed == ["user-1/cv.docx"]
