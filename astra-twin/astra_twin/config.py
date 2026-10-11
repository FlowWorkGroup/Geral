"""Configuração validada por variáveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

VALID_REASONING = {"low", "medium", "high", "xhigh", "max"}
VALID_PROVIDERS = {"openai", "ollama"}


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    reasoning_effort: str
    database_path: Path
    provider: str = "openai"
    base_url: str = ""
    max_history: int = 12
    max_input_chars: int = 12_000

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        provider = os.getenv("ASTRA_TWIN_PROVIDER", "openai").strip().lower()
        if provider not in VALID_PROVIDERS:
            raise ValueError(
                f"ASTRA_TWIN_PROVIDER inválido: {provider!r}. "
                f"Valores permitidos: {', '.join(sorted(VALID_PROVIDERS))}"
            )

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

        db_path = Path(os.getenv("ASTRA_TWIN_DB", "~/.astra-twin/memory.sqlite3")).expanduser()
        default_model = "qwen3:4b" if provider == "ollama" else "gpt-6-astra"
        default_base_url = "http://localhost:11434/v1" if provider == "ollama" else ""

        return cls(
            api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            model=os.getenv("ASTRA_TWIN_MODEL", default_model).strip(),
            reasoning_effort=effort,
            database_path=db_path,
            provider=provider,
            base_url=os.getenv("ASTRA_TWIN_BASE_URL", default_base_url).strip(),
            max_history=max_history,
            max_input_chars=max_input_chars,
        )
