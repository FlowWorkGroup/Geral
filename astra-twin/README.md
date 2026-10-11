# Astra Twin — MVP executável

Projeto inicial de uma IA própria inspirada na arquitetura descrita em `Estudo-tecnico-GPT-6-Astra.md`. Não é uma cópia dos pesos nem uma garantia de equivalência ao GPT-6 Astra: reproduz a arquitetura envolvente — controlador, memória persistente, limites e verificação básica — usando um modelo acessível pela API.

## Requisitos

- Python 3.11+
- Uma chave API com acesso ao modelo configurado
- Acesso à Internet para chamadas à API

## Instalação

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"
cp .env.example .env
```

Edite `.env` e defina `OPENAI_API_KEY`. Nunca coloque a chave no Git.

## Executar

```bash
astra-twin
```

Ou passe uma pergunta diretamente:

```bash
astra-twin "Explica como funciona uma fila de mensagens"
```

## Testes

```bash
pytest
```

Os testes não chamam a API e não exigem uma chave.

## Arquitetura

- `config.py`: configuração por variáveis de ambiente.
- `memory.py`: memória de conversação SQLite, persistente e local.
- `agent.py`: controlador limitado, chamada ao modelo e validação da resposta.
- `cli.py`: interface de terminal.
- `tests/`: testes offline.

## Limites de segurança atuais

Esta versão é uma prova de conceito, não um agente autónomo de produção. Não executa comandos, não altera ficheiros, não navega na rede por iniciativa própria e não tem ferramentas externas. A memória local pode conter dados pessoais; protege o ficheiro SQLite e elimina-o se já não for necessário. Para produção, acrescentar autenticação, gestão de segredos, limites de custo medidos, auditoria, testes de prompt injection e revisão humana para ações com impacto.

## Configuração

| Variável | Predefinição | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | — | Chave da API |
| `ASTRA_TWIN_MODEL` | `gpt-6-astra` | Identificador do modelo |
| `ASTRA_TWIN_REASONING` | `high` | `low`, `medium`, `high`, `xhigh` ou `max` |
| `ASTRA_TWIN_DB` | `~/.astra-twin/memory.sqlite3` | Caminho da base de dados |
| `ASTRA_TWIN_MAX_HISTORY` | `12` | Número máximo de mensagens recentes recuperadas |
| `ASTRA_TWIN_MAX_INPUT_CHARS` | `12000` | Limite de caracteres por pedido |

O identificador e os limites do modelo devem ser confirmados na documentação atual da API e na conta utilizada. O custo real depende do uso faturável e do acesso contratado.
