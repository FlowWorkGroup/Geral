"""Configuração validada por variáveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

VALID_REASONING = {"low", "medium", "high", "xhigh", "max"}


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    reasoning_effort: str
    database_path: Path
    max_history: int = 12
    max_input_chars: int = 12_000

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        effort = os.getenv("ASTRA_TWIN_REASONING", "high").strip().lower()
        if effort not in VALID_REASONING:
            raise ValueError(
                f"ASTRA_TWIN_REASONING inválido: {effort!r}. "
                f"Valores permitidos: {', '.join(sorted(VALID_REASONING))}"
            )

        try:
            max_history = int(os.getenv("ASTRA_TWIN_MAX_HISTORY", "12"))
            max_input_chars = int(os.getenv("ASTRA_TWIN_MAX_INPUT_CHARS", "12000"))
        except ValueError as exc:
            raise ValueError("Os limites configurados têm de ser números inteiros.") from exc

        if not 1 <= max_history <= 100:
            raise ValueError("ASTRA_TWIN_MAX_HISTORY tem de estar entre 1 e 100.")
        if not 100 <= max_input_chars <= 100_000:
            raise ValueError("ASTRA_TWIN_MAX_INPUT_CHARS tem de estar entre 100 e 100000.")

        raw_db = os.getenv("ASTRA_TWIN_DB", "~/.astra-twin/memory.sqlite3")
        db_path = Path(raw_db).expanduser()

        return cls(
            api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            model=os.getenv("ASTRA_TWIN_MODEL", "gpt-6-astra").strip(),
            reasoning_effort=effort,
            database_path=db_path,
            max_history=max_history,
            max_input_chars=max_input_chars,
        )
