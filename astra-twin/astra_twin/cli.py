"""Interface de linha de comandos."""

from __future__ import annotations

import argparse
import sys
import uuid

from .agent import AgentError, AstraTwinAgent
from .config import Settings
from .memory import MemoryStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Astra Twin — agente de IA experimental")
    parser.add_argument("prompt", nargs="?", help="Pergunta opcional; sem ela inicia modo interativo")
    parser.add_argument("--session", default="default", help="Identificador da sessão de memória")
    parser.add_argument("--new-session", action="store_true", help="Criar uma sessão nova")
    args = parser.parse_args()

    try:
        settings = Settings.from_env()
        if not settings.api_key:
            print("Erro: configura OPENAI_API_KEY no ficheiro .env.", file=sys.stderr)
            raise SystemExit(2)
        session_id = str(uuid.uuid4()) if args.new_session else args.session
        agent = AstraTwinAgent(settings, MemoryStore(settings.database_path))

        if args.prompt:
            print(agent.ask(args.prompt, session_id=session_id))
            return

        print(f"Astra Twin | sessão: {session_id}")
        print("Escreve 'sair' para terminar. A memória desta sessão fica guardada localmente.")
        while True:
            try:
                prompt = input("\nTu> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAté breve.")
                break
            if prompt.lower() in {"sair", "exit", "quit"}:
                print("Até breve.")
                break
            if not prompt:
                continue
            try:
                print(f"\nAstra Twin> {agent.ask(prompt, session_id=session_id)}")
            except (AgentError, ValueError) as exc:
                print(f"Erro: {exc}", file=sys.stderr)
    except (AgentError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
