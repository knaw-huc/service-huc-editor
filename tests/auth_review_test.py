from datetime import datetime, timedelta, timezone
import inspect
from types import SimpleNamespace

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import SQLModel, Session, create_engine

from src import commons
from src.auth import authentication
from src.auth.models import User
from src.auth import routes
from src.config import dependencies
from src import database


def test_user_repr_does_not_expose_password_hash():
    user = User(name="alice", password_hash="stored-hash")

    assert "stored-hash" not in repr(user)


def test_jwt_is_limited_to_issuing_app(monkeypatch):
    secret_key = "test-secret-key-with-at-least-32-bytes"
    monkeypatch.setattr(authentication, "get_jwt_secret_key", lambda: secret_key)
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(name="alice", password_hash="stored-hash")
        session.add(user)
        session.commit()
        token = jwt.encode(
            {
                "sub": "alice",
                "aud": "app-a",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            },
            secret_key,
            algorithm=authentication.ALGORITHM,
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        assert authentication.get_user_with_app(
            "app-a", session, basic_credentials=None, bearer_credentials=credentials
        ).name == "alice"
        with pytest.raises(HTTPException):
            authentication.get_user_with_app(
                "app-b", session, basic_credentials=None, bearer_credentials=credentials
            )


def test_missing_jwt_key_has_clear_error(monkeypatch):
    monkeypatch.setattr(authentication.settings, "get", lambda key: None)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be configured"):
        authentication.get_jwt_secret_key()


def test_app_database_initialization_is_repeatable(tmp_path, monkeypatch):
    apps_dir = tmp_path / "apps"
    app_dir = apps_dir / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "config.toml").write_text("[app]\n")
    monkeypatch.setattr(database.settings, "URL_DATA_APPS", str(apps_dir), raising=False)

    database.initialize_app_database("app")
    database.initialize_app_database("app")

    assert list(apps_dir.glob(".*.lock"))


def test_token_login_is_sync_and_uses_app_audience(monkeypatch):
    user = User(name="alice", password_hash="stored-hash")
    monkeypatch.setattr(routes, "get_user_with_password", lambda username, password, session: user)
    token_data = {}

    def create_token(data, expires_delta):
        token_data.update(data)
        return "token"

    monkeypatch.setattr(routes, "create_access_token", create_token)
    form_data = SimpleNamespace(**{"username": "alice", "password": "pw"})

    result = routes.login_for_access_token("app-a", None, form_data)

    assert not inspect.iscoroutinefunction(routes.login_for_access_token)
    assert token_data == {"sub": "alice", "aud": "app-a"}
    assert result.access_token == "token"


def test_app_discovery_requires_config_file(tmp_path, monkeypatch):
    apps_dir = tmp_path / "apps"
    (apps_dir / "valid").mkdir(parents=True)
    (apps_dir / "valid" / "config.toml").write_text("[app]\n")
    (apps_dir / "__pycache__").mkdir()
    monkeypatch.setattr(dependencies.settings, "URL_DATA_APPS", str(apps_dir), raising=False)

    assert dependencies.get_all_apps() == ["valid"]


def test_record_hooks_receive_username_or_none(tmp_path, monkeypatch):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "config.toml").write_text(
        '[app.hooks.record]\nread_pre = "record_hook"\n'
    )
    monkeypatch.setattr(commons.settings, "URL_DATA_APPS", str(tmp_path), raising=False)
    received_users = []

    def record_hook(crud, app, prof, nr, user, record):
        received_users.append(user)
        return record, None

    monkeypatch.setattr(
        commons.importlib,
        "import_module",
        lambda name: SimpleNamespace(record_hook=record_hook),
    )
    record = object()

    commons.call_record_hook("read_pre", "app", "profile", "1", User(
        name="alice", password_hash="stored-hash"
    ), record)
    commons.call_record_hook("read_pre", "app", "profile", "1", None, record)

    assert received_users == ["alice", None]


def test_anonymous_action_hook_receives_none(tmp_path, monkeypatch):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "config.toml").write_text(
        '[app.hooks.action.test]\nhook = "action_hook"\n'
    )
    monkeypatch.setattr(commons.settings, "URL_DATA_APPS", str(tmp_path), raising=False)
    received_args = []

    def action_hook(*args):
        received_args.extend(args)

    monkeypatch.setattr(
        commons.importlib,
        "import_module",
        lambda name: SimpleNamespace(action_hook=action_hook),
    )

    commons.call_action_hook(None, "test", "app", None, None, None)

    assert received_args[-1] is None
