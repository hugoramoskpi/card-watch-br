# Card Watch BR

Monitor automático de promoções de cartões black/premium usando LangGraph + Claude Sonnet 4.6.

## Comandos Essenciais

```bash
# Instalar dependências
pip install -r requirements.txt && playwright install chromium

# Configurar variáveis de ambiente
cp .env.example .env  # preencha as chaves antes de usar

# Executar um ciclo de busca (modo manual)
python src/scheduler.py --once

# Iniciar scheduler contínuo (ciclos a cada 2h)
python src/scheduler.py

# Iniciar dashboard web (processo separado)
uvicorn src.api.main:app --port 8000 --reload

# Iniciar bot Telegram
python -m src.bot.bot

# Rodar todos os testes
python -m pytest tests/ -v
```

## Arquitetura

Pipeline LangGraph com 4 nós em sequência:

1. **discovery** (`src/agent/nodes/discovery.py`) — descobre cartões em buzz hoje via Reddit + Brave Search. Claude extrai lista dinâmica
2. **promo_search** (`src/agent/nodes/promo_search.py`) — busca promoções específicas por cartão
3. **cross_validate** (`src/agent/nodes/cross_validate.py`) — valida promoções em ≥2 fontes, Claude resume e atribui score de confiança
4. **persist_alert** (`src/agent/nodes/persist_alert.py`) — salva no SQLite com deduplicação SHA256, envia alerta Telegram para novas promoções

Graph definido em `src/agent/graph.py` via `build_graph()`.

## Variáveis de Ambiente Obrigatórias

| Variável | Onde obter |
|----------|-----------|
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` | reddit.com/prefs/apps |
| `BRAVE_SEARCH_API_KEY` | api.search.brave.com |
| `TELEGRAM_BOT_TOKEN` | @BotFather no Telegram |
| `TELEGRAM_CHAT_ID` | ID do chat ou canal destino |

## Skills Disponíveis

Invocar ao conversar com Claude Code:
- `run-agent` — executa ciclo manual de busca
- `add-source` — guia para adicionar nova fonte de dados
- `debug-search` — checklist de debug quando busca retorna vazio

## Estrutura de Pastas

```
src/agent/    — LangGraph agent (nós + graph + state)
src/tools/    — Ferramentas de busca (Reddit, Brave, Playwright)
src/api/      — FastAPI dashboard (rotas + template HTML)
src/bot/      — Telegram bot (/status, /promos, /buscar)
src/db/       — SQLAlchemy models + repository + database
src/scheduler.py — APScheduler entry point (--once flag)
tests/        — 22 testes com TDD
hooks/        — Scripts de hook (pre-search, post-alert)
.claude/      — Configurações e skills do Claude Code
docs/         — Spec, plano de implementação e guias
```

## Processos em Produção

O scheduler e o dashboard são **dois processos separados** que compartilham o SQLite:
1. `python src/scheduler.py` — roda em background, busca a cada 2h
2. `uvicorn src.api.main:app --port 8000` — serve o dashboard
