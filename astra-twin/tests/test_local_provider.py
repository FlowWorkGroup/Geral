from pathlib import Path
from types import SimpleNamespace

from astra_twin.agent import AstraTwinAgent
from astra_twin.config import Settings
from astra_twin.memory import MemoryStore


class FakeChatCompletions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Resposta local"))])


class FakeLocalClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=FakeChatCompletions())


def test_ollama_settings_default_to_local_model(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("ASTRA_TWIN_PROVIDER", "ollama")
    monkeypatch.delenv("ASTRA_TWIN_MODEL", raising=False)
    monkeypatch.delenv("ASTRA_TWIN_BASE_URL", raising=False)
    monkeypatch.setenv("ASTRA_TWIN_DB", str(tmp_path / "memory.sqlite3"))
    settings = Settings.from_env()
    assert settings.provider == "ollama"
    assert settings.model == "qwen3:4b"
    assert settings.base_url == "http://localhost:11434/v1"


def test_ollama_agent_uses_chat_completions_and_persists(tmp_path: Path):
    settings = Settings(
        api_key="", model="qwen3:4b", reasoning_effort="high",
        database_path=tmp_path / "memory.sqlite3", provider="ollama",
        base_url="http://localhost:11434/v1",
    )
    memory = MemoryStore(settings.database_path)
    client = FakeLocalClient()
    agent = AstraTwinAgent(settings, memory, client=client)
    assert agent.ask("Olá", session_id="local") == "Resposta local"
    assert client.chat.completions.calls[0]["model"] == "qwen3:4b"
    assert memory.recent("local") == [
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "Resposta local"},
    ]
