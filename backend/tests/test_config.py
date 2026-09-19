from app.config import Settings


def _clear_ambient(monkeypatch):
    """Settings reads the real environment, and CI sets some of these itself.

    A test that leaves them in place asserts against whatever the runner happens
    to export — which is how this file passed locally and failed in CI. Clear the
    ones under test so the case is hermetic.
    """
    for key in ("DATABASE_URL", "REDIS_URL", "SESSION_TOKEN_BUDGET", "ENVIRONMENT"):
        monkeypatch.delenv(key, raising=False)


def test_settings_read_from_environment(monkeypatch):
    _clear_ambient(monkeypatch)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("SESSION_TOKEN_BUDGET", "1234")

    settings = Settings(_env_file=None)

    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.session_token_budget == 1234


def test_environment_defaults_when_unset(monkeypatch):
    _clear_ambient(monkeypatch)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    assert Settings(_env_file=None).environment == "development"


def test_environment_is_read_when_set(monkeypatch):
    _clear_ambient(monkeypatch)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("ENVIRONMENT", "test")

    assert Settings(_env_file=None).environment == "test"
