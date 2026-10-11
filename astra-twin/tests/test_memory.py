from pathlib import Path

import pytest

from astra_twin.memory import MemoryStore


def test_memory_round_trip_and_order(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "memory.sqlite3")
    memory.add("s1", "user", "Olá")
    memory.add("s1", "assistant", "Olá! Como posso ajudar?")
    assert memory.recent("s1") == [
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "Olá! Como posso ajudar?"},
    ]


def test_memory_isolated_by_session(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "memory.sqlite3")
    memory.add("one", "user", "segredo da sessão um")
    memory.add("two", "user", "sessão dois")
    assert memory.recent("two") == [{"role": "user", "content": "sessão dois"}]


def test_invalid_role_rejected(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "memory.sqlite3")
    with pytest.raises(ValueError):
        memory.add("s1", "system", "não permitido")


def test_clear_session(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "memory.sqlite3")
    memory.add("s1", "user", "apagar")
    assert memory.clear_session("s1") == 1
    assert memory.recent("s1") == []
