# Astra Twin — MVP executável

Agente experimental com controlador, memória persistente SQLite e fornecedor de modelos configurável. Pode usar a API local do Ollama ou a API da OpenAI. Não é uma cópia dos pesos nem uma garantia de equivalência ao GPT-6 Astra.

## Opção A — modelo local com Ollama (sem chave de API)

1. Instala o Ollama para macOS: https://ollama.com/download
2. Inicia o Ollama e confirma que a API local responde em `http://localhost:11434`.
3. Descarrega o modelo recomendado para começar num computador com 8 GB de memória:

   ```bash
   ollama pull qwen3:4b
   ```

4. Instala o projeto:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -e ".[dev]"
   cp .env.example .env
   ```

5. No `.env`, confirma estas opções:

   ```dotenv
   ASTRA_TWIN_PROVIDER=ollama
   ASTRA_TWIN_MODEL=qwen3:4b
   ASTRA_TWIN_BASE_URL=http://localhost:11434/v1
   ```

6. Executa uma pergunta de teste:

   ```bash
   astra-twin "Responde em português europeu: explica o que é uma API local."
   ```

A API do Ollama é local; a inferência não requer uma chave externa. A primeira descarga do modelo precisa de Internet. Depois de descarregado, o modelo pode gerar respostas sem Internet, desde que o serviço local esteja a correr.

## Opção B — API OpenAI

No `.env`, define `ASTRA_TWIN_PROVIDER=openai` e preenche `OPENAI_API_KEY` com uma chave válida. O modelo é definido em `ASTRA_TWIN_MODEL`; confirma o identificador e o acesso na tua conta.

## Comandos

```bash
astra-twin "A tua pergunta"
astra-twin --session projeto "Continua a conversa da sessão projeto"
pytest
```

Sem pergunta na linha de comandos, o programa entra em modo interativo. A memória é guardada em `~/.astra-twin/memory.sqlite3` por predefinição.

## Interface web privada de teste

A interface usa uma palavra-passe forte, sessão assinada, proteção CSRF, limitação de tentativas de autenticação e cabeçalhos de segurança. Por defeito, o servidor escuta **apenas em `127.0.0.1:8765`**. Não alteres `ASTRA_TWIN_WEB_HOST` para `0.0.0.0` e não publiques a porta 8765 nem a porta 11434 na Internet.

1. Define `ASTRA_TWIN_WEB_PASSWORD` com pelo menos 16 caracteres aleatórios e `ASTRA_TWIN_WEB_SECRET` com pelo menos 32 caracteres aleatórios no `.env` local. Nunca coloques estes valores no Git.
2. Instala as dependências atualizadas com `python -m pip install -e ".[dev]"`.
3. Inicia com `astra-twin-web` e testa no próprio Mac em `http://127.0.0.1:8765`.
4. Para aceder a partir do iPhone, usa uma rede privada como Tailscale e expõe **apenas a interface web autenticada** através de Tailscale Serve. O iPhone e o Mac têm de estar autenticados no mesmo tailnet. Não uses um túnel público nem exponhas diretamente a API do Ollama.

Se o Tailscale não estiver autenticado no Mac, o acesso pelo iPhone ainda não está configurado; não contornes o login de rede. A interface não fornece acesso ao sistema operativo nem ferramentas para executar comandos.

## Arquitetura

- `config.py`: fornecedor, modelo, URL e limites validados por variáveis de ambiente.
- `memory.py`: memória de conversação SQLite persistente.
- `agent.py`: controlador e integração com OpenAI Responses ou Ollama Chat Completions.
- `cli.py`: interface de terminal.
- `tests/`: testes offline; não exigem uma chave nem um modelo descarregado.

## Limites de segurança

Esta versão é uma prova de conceito, não um agente autónomo de produção. Não executa comandos, não altera ficheiros, não navega na rede por iniciativa própria e não tem ferramentas externas. A memória local pode conter dados pessoais; protege o ficheiro SQLite. Para produção, acrescentar autenticação, auditoria, limites de uso, testes de prompt injection e revisão humana para ações com impacto.
