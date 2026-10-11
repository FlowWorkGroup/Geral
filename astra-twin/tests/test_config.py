from pathlib import Path

import dotenv
import pytest

from astra_twin.config import Settings


def test_defaults_and_explicit_database(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dotenv, "load_dotenv", lambda: None)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASTRA_TWIN_PROVIDER", "openai")
    monkeypatch.delenv("ASTRA_TWIN_MODEL", raising=False)
    monkeypatch.delenv("ASTRA_TWIN_BASE_URL", raising=False)
    monkeypatch.setenv("ASTRA_TWIN_DB", str(tmp_path / "state.sqlite3"))
    monkeypatch.delenv("ASTRA_TWIN_REASONING", raising=False)
    settings = Settings.from_env()
    assert settings.provider == "openai"
    assert settings.model == "gpt-6-astra"
    assert settings.reasoning_effort == "high"
    assert settings.database_path == tmp_path / "state.sqlite3"


def test_invalid_reasoning_rejected(monkeypatch) -> None:
    monkeypatch.setenv("ASTRA_TWIN_REASONING", "impossible")
    with pytest.raises(ValueError):
        Settings.from_env()


def test_limits_are_validated(monkeypatch) -> None:
    monkeypatch.setenv("ASTRA_TWIN_MAX_HISTORY", "0")
    with pytest.raises(ValueError):
        Settings.from_env()
