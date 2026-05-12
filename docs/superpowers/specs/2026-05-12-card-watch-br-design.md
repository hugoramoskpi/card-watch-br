# Card Watch BR — Design Spec
**Data:** 2026-05-12
**Status:** Aprovado
**Autor:** Hugo Ramos (via Claude Code brainstorming)

---

## Contexto e Motivação

Promoções de cartões de crédito premium/black surgem e desaparecem rapidamente em fóruns e redes sociais. Acompanhar manualmente Reddit, Hardmob, Reclame Aqui e outras fontes é inviável. O Card Watch BR automatiza essa vigilância: um agente LangGraph descobre dinamicamente quais cartões estão em pauta a cada ciclo, valida promoções em múltiplas fontes e entrega resultados via dashboard web e alertas Telegram.

O projeto também serve como **treinamento completo de Claude Code**, demonstrando na prática: CLAUDE.md, skills customizadas, hooks, integração MCP, backup no GitHub e boas práticas de segurança.

---

## Objetivo do Produto

- Monitorar **todos** os cartões premium/black em discussão — sem lista fixa, descoberta dinâmica
- Validar cada promoção em **≥ 2 fontes independentes** antes de alertar
- Entregar resultados em **dashboard web** (visão geral) e **bot Telegram** (alertas em tempo real)
- Rodar em **ciclos automáticos** contínuos (padrão: a cada 2 horas)

---

## Cartões Primários de Referência

Usados como âncora inicial para cada ciclo; a descoberta dinâmica pode expandir além deles:

| Cartão | Bandeira | Relevância |
|--------|----------|------------|
| Nubank Ultravioleta | Mastercard Black | Muito alta — comunidade ativa |
| Inter Black | Mastercard Black | Muito alta — zero anuidade |
| C6 Carbon | Mastercard Black | Muito alta — mais acessível |
| BTG Black | Mastercard Black | Alta — crescendo em 2026 |
| BRB DUX | Mastercard Black | Alta — melhor pontuação milhas |

---

## Arquitetura

### Visão Geral

```
APScheduler (cron a cada 2h)
        │
        ▼
LangGraph Agent Pipeline
  ├── Nó 1: Discovery
  │     └── "Quais cartões premium estão sendo falados HOJE?"
  │         Reddit PRAW + Brave Search API + Hardmob scraping
  │         Claude extrai lista dinâmica de cartões + buzz
  │
  ├── Nó 2: PromoSearch (por cartão encontrado)
  │     └── Busca promoções específicas de cada cartão
  │         Reddit threads + Brave Search + Reclame Aqui
  │
  ├── Nó 3: CrossValidate
  │     └── Confirma cada promoção em ≥ 2 fontes distintas
  │         Score de confiança: 1 fonte=baixo, 2=médio, 3+=alto
  │
  └── Nó 4: Persist & Alert
        └── Salva no SQLite, dispara Telegram se promoção nova
                │
                ├── SQLite Database
                ├── FastAPI + Dashboard HTML/Tailwind
                └── python-telegram-bot
```

### Fluxo de Dados

1. APScheduler dispara o ciclo a cada 2 horas
2. Nó Discovery busca nas fontes e retorna lista: `[{card, buzz_score, mentions}]`
3. Para cada cartão com buzz, Nó PromoSearch busca promoções ativas
4. Nó CrossValidate filtra: passa apenas promoções confirmadas em ≥ 2 fontes
5. Nó Persist salva no SQLite com hash de deduplicação
6. Se promoção é nova (hash não existe ainda), dispara alerta Telegram
7. Dashboard FastAPI lê SQLite e serve as promoções validadas

---

## Componentes

### 1. LangGraph Agent (`src/agent/`)

```
src/agent/
├── graph.py          ← Definição do StateGraph
├── nodes/
│   ├── discovery.py  ← Nó 1: descobre cartões em buzz
│   ├── promo_search.py ← Nó 2: busca promoções por cartão
│   ├── cross_validate.py ← Nó 3: validação cruzada
│   └── persist_alert.py  ← Nó 4: salva e alerta
├── tools/
│   ├── reddit_tool.py   ← PRAW API wrapper
│   ├── brave_tool.py    ← Brave Search API wrapper
│   └── scraper_tool.py  ← Playwright para Hardmob/Reclame Aqui
└── state.py          ← AgentState TypedDict
```

**Modelo:** Claude Sonnet 4.6 (`claude-sonnet-4-6`) como LLM do agente

**AgentState:**
```python
class AgentState(TypedDict):
    cycle_id: str
    discovered_cards: list[CardBuzz]    # {card_name, buzz_score, mentions_count, sources}
    raw_promos: list[RawPromo]          # {card_name, text, url, source_name, found_at}
    validated_promos: list[ValidatedPromo]  # {card_name, summary, urls, confidence (1-3)}
    alerts_sent: list[str]              # IDs das promoções já alertadas neste ciclo
```

### 2. Fontes de Dados (`src/agent/tools/`)

| Fonte | Método | API Key? | Observação |
|-------|--------|----------|-----------|
| Reddit | PRAW API | Sim (gratuita) | 60 req/min no plano free |
| Brave Search | REST API | Sim (free: 2000 req/mês) | Suficiente para ciclos de 2h |
| Hardmob | Playwright scraping | Não | Fórum de finanças BR |
| Reclame Aqui | Playwright scraping | Não | Reclamações + promoções |

> **Nota sobre Twitter/X:** excluído da v1 por custo proibitivo da API (plano Basic: US$100/mês). Brave Search captura tweets relevantes indiretamente via resultados de busca.

**Subreddits monitorados:** `r/investimentos`, `r/financaspessoais`, `r/brasil`, `r/creditcard`

### 3. Database (`src/db/`)

```sql
-- Tabela principal
CREATE TABLE promotions (
    id          TEXT PRIMARY KEY,  -- SHA256(card+promo_text)
    card_name   TEXT NOT NULL,
    summary     TEXT NOT NULL,
    sources     JSON NOT NULL,     -- lista de fontes confirmadas
    confidence  INTEGER NOT NULL,  -- 1=baixo, 2=médio, 3=alto
    raw_urls    JSON NOT NULL,
    found_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dismissed   BOOLEAN DEFAULT FALSE,
    alerted     BOOLEAN DEFAULT FALSE
);

-- Histórico de ciclos
CREATE TABLE cycles (
    id          TEXT PRIMARY KEY,
    started_at  TIMESTAMP,
    finished_at TIMESTAMP,
    cards_found INTEGER,
    promos_found INTEGER,
    promos_validated INTEGER
);
```

### 4. Dashboard (`src/api/`)

> **Processos separados:** o scheduler (`scheduler.py`) e o dashboard (`uvicorn`) rodam como dois processos independentes. Ambos acessam o mesmo arquivo SQLite. Em produção, podem ser gerenciados via `supervisord` ou dois terminais separados.

- **Framework:** FastAPI
- **Frontend:** HTML + Tailwind CSS (CDN, sem build step)
- **Rotas:**
  - `GET /` — dashboard principal
  - `GET /api/promotions` — JSON das promoções (filtros: card, confidence, date)
  - `POST /api/promotions/{id}/dismiss` — descarta promoção
  - `GET /api/cycles` — histórico de ciclos
  - `POST /api/cycles/trigger` — força novo ciclo manualmente

### 5. Telegram Bot (`src/bot/`)

- **Lib:** `python-telegram-bot`
- **Comandos:**
  - `/status` — resumo do último ciclo
  - `/buscar` — força novo ciclo
  - `/promos` — lista últimas 5 promoções validadas
- **Alertas automáticos:** enviados após cada ciclo quando há promoções novas

---

## Estrutura de Projeto Completa

```
card-watch-br/
├── CLAUDE.md                        ← Documentação do projeto p/ Claude Code
├── .claude/
│   ├── settings.json                ← Permissões, hooks, configs
│   └── skills/
│       ├── run-agent.md             ← Skill: executa ciclo manualmente
│       ├── add-source.md            ← Skill: adiciona nova fonte de busca
│       └── debug-search.md         ← Skill: depura ciclo sem resultados
├── hooks/
│   ├── pre-search.sh               ← Valida API keys antes de cada ciclo
│   └── post-alert.sh               ← Loga alertas enviados
├── mcp/
│   └── brave-search/               ← Configuração do MCP Brave Search
├── docs/
│   ├── superpowers/specs/          ← Este arquivo
│   ├── guia-claude-code.md         ← Guia de boas práticas Claude Code
│   ├── guia-skills.md              ← Como criar e usar skills
│   ├── guia-hooks.md               ← Como criar e usar hooks
│   ├── guia-mcp.md                 ← Integração MCP passo a passo
│   └── anti-piracy.md              ← Licença, proteção, segurança
├── .github/
│   └── workflows/
│       ├── backup.yml              ← Backup automático a cada push
│       └── security-scan.yml       ← Scan de secrets (trufflehog/gitleaks)
├── src/
│   ├── agent/                      ← LangGraph agent (ver acima)
│   ├── api/                        ← FastAPI dashboard
│   ├── bot/                        ← Telegram bot
│   ├── db/                         ← SQLite models e migrations
│   └── scheduler.py                ← APScheduler entry point
├── tests/
│   ├── test_agent.py
│   ├── test_api.py
│   └── test_bot.py
├── .env.example                    ← Template de variáveis (sem valores reais)
├── .gitignore                      ← Inclui .env, *.db, __pycache__
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Módulos de Treinamento Claude Code

### CLAUDE.md
Documenta: propósito do projeto, stack, comandos principais (`python src/scheduler.py`, `uvicorn src.api.main:app`), variáveis de ambiente necessárias, estrutura de pastas e como contribuir.

### Skills Customizadas (`.claude/skills/`)

| Skill | Trigger | Ação |
|-------|---------|------|
| `run-agent` | "executar busca / rodar ciclo" | Roda `src/scheduler.py --once` |
| `add-source` | "adicionar fonte / novo fórum" | Guia para adicionar nova tool ao agente |
| `debug-search` | "busca vazia / sem resultados" | Checklist de debug: API keys, conectividade, logs |

### Hooks (`.claude/settings.json`)

| Hook | Evento | Ação |
|------|--------|------|
| `pre-search` | Antes de rodar o agente | Verifica `.env` completo e APIs acessíveis |
| `post-alert` | Após enviar alerta Telegram | Loga no arquivo `logs/alerts.log` |
| `pre-commit` | Antes de commit git | Bloqueia se `.env` estiver no staging |

### Integração MCP
- **Brave Search MCP:** configurado em `.claude/settings.json` como servidor MCP local
- Permite que Claude Code use Brave Search diretamente nas conversas do projeto
- Documentado em `docs/guia-mcp.md` com passo a passo de setup

### GitHub Backup e Segurança
- **`backup.yml`:** GitHub Action que cria release automática a cada push na `main`
- **`security-scan.yml`:** Roda `gitleaks` a cada PR para detectar secrets acidentais
- **`.gitignore`:** `.env`, `*.db`, `logs/`, `__pycache__/` sempre ignorados
- **`.env.example`:** Template com nomes das variáveis mas sem valores

### Anti-Piracy
- Licença MIT incluída (`LICENSE`)
- Todas as API keys via variáveis de ambiente (jamais hardcoded)
- `docs/anti-piracy.md` documenta: uso aceitável, atribuição, restrições comerciais
- CI bloqueia merge se secrets detectados no código

---

## Variáveis de Ambiente

```env
# LLM
ANTHROPIC_API_KEY=

# Fontes de busca
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=CardWatchBR/1.0
BRAVE_SEARCH_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# App
SEARCH_INTERVAL_HOURS=2
MIN_SOURCES_TO_VALIDATE=2
DATABASE_URL=sqlite:///data/cardwatch.db
DASHBOARD_PORT=8000
```

---

## Tratamento de Erros

| Cenário | Comportamento |
|---------|--------------|
| API key inválida | Hook pre-search bloqueia ciclo, loga erro claro |
| Fonte indisponível (ex: Reddit fora) | Agente continua com fontes restantes, registra no ciclo |
| Nenhuma promoção encontrada | Ciclo registrado normalmente, nenhum alerta enviado |
| Erro no Telegram | Promoção salva no DB, alerta reenviado no próximo ciclo |
| Promoção duplicada | Hash SHA256 detecta, ignora silenciosamente |

---

## Testes e Verificação

### Como testar end-to-end:
1. Copiar `.env.example` para `.env` e preencher todas as chaves
2. Rodar `python -m pytest tests/` — todos os testes devem passar
3. Rodar `python src/scheduler.py --once` — executa um ciclo completo
4. Verificar saída no terminal: deve mostrar cartões descobertos, promoções validadas
5. Abrir `http://localhost:8000` — promoções devem aparecer no dashboard
6. Verificar Telegram — alert deve ter chegado para cada promoção nova
7. Rodar `/status` no bot Telegram — deve retornar resumo do ciclo

### Testes unitários:
- `test_agent.py`: mock das APIs externas, valida o fluxo do StateGraph
- `test_api.py`: testa rotas FastAPI com banco SQLite em memória
- `test_bot.py`: testa formatação dos alertas Telegram

---

## Dependências Principais

```
langchain
langgraph
langchain-anthropic
fastapi
uvicorn
python-telegram-bot
praw
playwright
requests
apscheduler
sqlalchemy
python-dotenv
pytest
pytest-asyncio
```

---

## Fora do Escopo (v1)

- Autenticação no dashboard (acesso local apenas)
- Notificações por email
- Histórico de preços de anuidade
- App mobile
- Múltiplos usuários / multi-tenant
