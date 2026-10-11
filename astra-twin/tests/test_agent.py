from pathlib import Path
from types import SimpleNamespace

import pytest

from astra_twin.agent import AgentError, AstraTwinAgent
from astra_twin.config import Settings
from astra_twin.memory import MemoryStore


class FakeResponses:
    def __init__(self, output_text="Resposta de teste"):
        self.output_text = output_text
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class FakeClient:
    def __init__(self, output_text="Resposta de teste"):
        self.responses = FakeResponses(output_text)


def make_settings(tmp_path: Path, **overrides) -> Settings:
    values = {
        "api_key": "",
        "model": "test-model",
        "reasoning_effort": "high",
        "database_path": tmp_path / "memory.sqlite3",
        "max_history": 12,
        "max_input_chars": 12000,
    }
    values.update(overrides)
    return Settings(**values)


def test_agent_requires_api_key_without_injected_client(tmp_path: Path) -> None:
    with pytest.raises(AgentError, match="OPENAI_API_KEY"):
        AstraTwinAgent(make_settings(tmp_path), MemoryStore(tmp_path / "db.sqlite3"))


def test_agent_sends_prompt_and_persists_turn(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "db.sqlite3")
    client = FakeClient("Resposta validada")
    agent = AstraTwinAgent(make_settings(tmp_path), memory, client=client)

    assert agent.ask("Olá", session_id="test") == "Resposta validada"
    assert memory.recent("test") == [
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "Resposta validada"},
    ]
    assert client.responses.calls[0]["model"] == "test-model"
    assert client.responses.calls[0]["reasoning"] == {"effort": "high"}


def test_empty_model_response_is_not_persisted(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "db.sqlite3")
    agent = AstraTwinAgent(make_settings(tmp_path), memory, client=FakeClient(""))

    with pytest.raises(AgentError, match="não devolveu texto"):
        agent.ask("Olá", session_id="test")
    assert memory.recent("test") == []


def test_input_limit_is_enforced_before_api_call(tmp_path: Path) -> None:
    client = FakeClient()
    agent = AstraTwinAgent(
        make_settings(tmp_path, max_input_chars=100),
        MemoryStore(tmp_path / "db.sqlite3"),
        client=client,
    )
    with pytest.raises(ValueError, match="excede o limite"):
        agent.ask("x" * 101)
    assert client.responses.calls == []
