# Card Watch BR — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an automated monitor that discovers and validates premium/black credit card promotions from forums and social media, delivering results via a web dashboard and Telegram alerts — while demonstrating Claude Code best practices throughout.

**Architecture:** A LangGraph agent pipeline (Discovery → PromoSearch → CrossValidate → Persist & Alert) runs on APScheduler every 2 hours. It uses Reddit PRAW API, Brave Search API, and Playwright scraping as data sources. FastAPI serves the dashboard; python-telegram-bot delivers real-time alerts. Claude Sonnet 4.6 orchestrates all LLM calls.

**Tech Stack:** Python 3.11+, LangGraph 0.2+, LangChain-Anthropic, FastAPI, SQLAlchemy + SQLite, python-telegram-bot 21+, PRAW, Playwright, APScheduler 3+

---

## File Map

```
(project root = C:\Users\hugor\Desktop\aprendizado\)
├── CLAUDE.md
├── .claude/
│   ├── settings.json
│   └── skills/
│       ├── run-agent.md
│       ├── add-source.md
│       └── debug-search.md
├── hooks/
│   ├── pre-search.sh
│   └── post-alert.sh
├── mcp/
│   └── brave-search-config.json
├── docs/                             ← already exists (spec lives here)
├── .github/workflows/
│   ├── backup.yml
│   └── security-scan.yml
├── src/
│   ├── __init__.py
│   ├── scheduler.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── discovery.py
│   │       ├── promo_search.py
│   │       ├── cross_validate.py
│   │       └── persist_alert.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── reddit_tool.py
│   │   ├── brave_tool.py
│   │   └── scraper_tool.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── templates/
│   │       └── index.html
│   ├── bot/
│   │   ├── __init__.py
│   │   └── bot.py
│   └── db/
│       ├── __init__.py
│       ├── database.py
│       ├── models.py
│       └── repository.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_db.py
│   ├── test_tools.py
│   ├── test_nodes.py
│   ├── test_api.py
│   └── test_bot.py
├── data/                             ← gitignored
├── logs/                             ← gitignored
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Phase 1: Foundation

### Task 1: Project Scaffold + Git Init

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `src/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)

- [ ] **Step 1: Create directory structure**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force src, src/agent, src/agent/nodes, src/tools, src/api, src/api/templates, src/bot, src/db, tests, data, logs, hooks, mcp, .github/workflows, .claude/skills
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[project]
name = "card-watch-br"
version = "0.1.0"
description = "Monitor de promoções de cartões black/premium"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 3: Create `requirements.txt`**

```
langchain==0.3.25
langgraph==0.2.60
langchain-anthropic==0.3.15
fastapi==0.115.12
uvicorn[standard]==0.34.0
python-telegram-bot==21.10
praw==7.8.1
playwright==1.50.0
requests==2.32.3
apscheduler==3.11.0
sqlalchemy==2.0.40
python-dotenv==1.1.0
pytest==8.3.5
pytest-asyncio==0.25.3
httpx==0.28.1
jinja2==3.1.5
```

- [ ] **Step 4: Create `.gitignore`**

```
.env
*.db
data/
logs/
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
*.egg-info/
dist/
build/
```

- [ ] **Step 5: Create `.env.example`**

```env
# LLM
ANTHROPIC_API_KEY=

# Reddit (obtenha em https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=CardWatchBR/1.0

# Brave Search (obtenha em https://api.search.brave.com)
BRAVE_SEARCH_API_KEY=

# Telegram (crie um bot em @BotFather)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# App
SEARCH_INTERVAL_HOURS=2
MIN_SOURCES_TO_VALIDATE=2
DATABASE_URL=sqlite:///data/cardwatch.db
DASHBOARD_PORT=8000
```

- [ ] **Step 6: Create empty `__init__.py` files**

```powershell
"" | Out-File src/__init__.py -Encoding utf8
"" | Out-File src/agent/__init__.py -Encoding utf8
"" | Out-File src/agent/nodes/__init__.py -Encoding utf8
"" | Out-File src/tools/__init__.py -Encoding utf8
"" | Out-File src/api/__init__.py -Encoding utf8
"" | Out-File src/bot/__init__.py -Encoding utf8
"" | Out-File src/db/__init__.py -Encoding utf8
"" | Out-File tests/__init__.py -Encoding utf8
```

- [ ] **Step 7: Git init + first commit**

```bash
git init
git add pyproject.toml requirements.txt .gitignore .env.example src/ tests/
git commit -m "chore: scaffold project structure"
```

- [ ] **Step 8: Install dependencies**

```bash
pip install -r requirements.txt
playwright install chromium
```

Expected: all packages install without errors.

---

### Task 2: Database Layer

**Files:**
- Create: `src/db/models.py`
- Create: `src/db/database.py`
- Create: `src/db/repository.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_db.py`:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, Promotion, Cycle
from src.db.repository import upsert_promotion, get_promotions, dismiss_promotion, mark_alerted

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_upsert_promotion_creates_new(db):
    promo, is_new = upsert_promotion(
        db, "Inter Black", "Anuidade zero por 12 meses",
        ["Reddit", "Brave"], 2, ["https://reddit.com/r/investimentos/123"]
    )
    assert is_new is True
    assert promo.card_name == "Inter Black"
    assert promo.confidence == 2

def test_upsert_promotion_deduplicates(db):
    upsert_promotion(db, "C6 Carbon", "Aprovação facilitada", ["Reddit"], 1, ["https://url1.com"])
    _, is_new = upsert_promotion(db, "C6 Carbon", "Aprovação facilitada", ["Brave"], 2, ["https://url2.com"])
    assert is_new is False

def test_get_promotions_excludes_dismissed(db):
    upsert_promotion(db, "BTG Black", "50k bônus", ["Reddit", "Brave"], 2, ["https://url.com"])
    promos = get_promotions(db)
    assert len(promos) == 1
    dismiss_promotion(db, promos[0].id)
    assert len(get_promotions(db)) == 0

def test_mark_alerted(db):
    promo, _ = upsert_promotion(db, "Nubank Ultra", "Cashback 5%", ["Reddit"], 1, ["https://url.com"])
    assert promo.alerted is False
    mark_alerted(db, promo.id)
    db.refresh(promo)
    assert promo.alerted is True
```

- [ ] **Step 2: Run tests to verify failure**

```bash
python -m pytest tests/test_db.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.db.models'`

- [ ] **Step 3: Create `src/db/models.py`**

```python
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(String, primary_key=True)
    card_name = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    sources = Column(JSON, nullable=False)
    confidence = Column(Integer, nullable=False)
    raw_urls = Column(JSON, nullable=False)
    found_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dismissed = Column(Boolean, default=False)
    alerted = Column(Boolean, default=False)

class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(String, primary_key=True)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    cards_found = Column(Integer, default=0)
    promos_found = Column(Integer, default=0)
    promos_validated = Column(Integer, default=0)
```

- [ ] **Step 4: Create `src/db/database.py`**

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/cardwatch.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def create_tables() -> None:
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Create `src/db/repository.py`**

```python
import hashlib
from sqlalchemy.orm import Session
from .models import Promotion, Cycle

def _promotion_id(card_name: str, summary: str) -> str:
    return hashlib.sha256(f"{card_name}:{summary}".encode()).hexdigest()[:16]

def upsert_promotion(
    db: Session,
    card_name: str,
    summary: str,
    sources: list[str],
    confidence: int,
    raw_urls: list[str],
) -> tuple[Promotion, bool]:
    promo_id = _promotion_id(card_name, summary)
    existing = db.get(Promotion, promo_id)
    if existing:
        return existing, False
    promo = Promotion(
        id=promo_id,
        card_name=card_name,
        summary=summary,
        sources=sources,
        confidence=confidence,
        raw_urls=raw_urls,
    )
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo, True

def get_promotions(db: Session, dismissed: bool = False) -> list[Promotion]:
    return (
        db.query(Promotion)
        .filter(Promotion.dismissed == dismissed)
        .order_by(Promotion.found_at.desc())
        .all()
    )

def dismiss_promotion(db: Session, promo_id: str) -> bool:
    promo = db.get(Promotion, promo_id)
    if not promo:
        return False
    promo.dismissed = True
    db.commit()
    return True

def mark_alerted(db: Session, promo_id: str) -> None:
    promo = db.get(Promotion, promo_id)
    if promo:
        promo.alerted = True
        db.commit()
```

- [ ] **Step 6: Run tests to verify pass**

```bash
python -m pytest tests/test_db.py -v
```

Expected:
```
PASSED tests/test_db.py::test_upsert_promotion_creates_new
PASSED tests/test_db.py::test_upsert_promotion_deduplicates
PASSED tests/test_db.py::test_get_promotions_excludes_dismissed
PASSED tests/test_db.py::test_mark_alerted
```

- [ ] **Step 7: Commit**

```bash
git add src/db/ tests/test_db.py
git commit -m "feat: add database layer with SQLAlchemy models and repository"
```

---

## Phase 2: Search Tools

### Task 3: Reddit Tool

**Files:**
- Create: `src/tools/reddit_tool.py`
- Create: `tests/test_tools.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_tools.py`:
```python
from unittest.mock import MagicMock, patch
from src.tools.reddit_tool import search_reddit_for_black_cards

def test_reddit_tool_returns_list():
    mock_submission = MagicMock()
    mock_submission.title = "Inter Black com anuidade zero aprovado!"
    mock_submission.selftext = "Consegui o Inter Black com renda de 5k"
    mock_submission.permalink = "/r/investimentos/comments/abc123"
    mock_submission.score = 42

    with patch("src.tools.reddit_tool.praw.Reddit") as MockReddit:
        mock_reddit = MockReddit.return_value
        mock_reddit.subreddit.return_value.search.return_value = [mock_submission]
        results = search_reddit_for_black_cards.invoke({"query": "inter black"})

    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0]["title"] == "Inter Black com anuidade zero aprovado!"
    assert "reddit.com" in results[0]["url"]
    assert results[0]["source_name"].startswith("Reddit r/")
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m pytest tests/test_tools.py::test_reddit_tool_returns_list -v
```

Expected: `ModuleNotFoundError: No module named 'src.tools.reddit_tool'`

- [ ] **Step 3: Create `src/tools/reddit_tool.py`**

```python
import os
import praw
from langchain_core.tools import tool

_SUBREDDITS = ["investimentos", "financaspessoais", "brasil", "creditcard"]

def _get_reddit() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.getenv("REDDIT_USER_AGENT", "CardWatchBR/1.0"),
    )

@tool
def search_reddit_for_black_cards(query: str) -> list[dict]:
    """Search Reddit for discussions about premium/black credit cards.

    Args:
        query: search terms (e.g. 'inter black anuidade')

    Returns:
        List of dicts with keys: title, text, url, score, source_name
    """
    reddit = _get_reddit()
    results = []
    for sub in _SUBREDDITS:
        for post in reddit.subreddit(sub).search(query, limit=10, sort="new", time_filter="day"):
            results.append({
                "title": post.title,
                "text": post.selftext[:500],
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,
                "source_name": f"Reddit r/{sub}",
            })
    return results
```

- [ ] **Step 4: Run test to verify pass**

```bash
python -m pytest tests/test_tools.py::test_reddit_tool_returns_list -v
```

Expected: `PASSED`

---

### Task 4: Brave Search Tool

**Files:**
- Modify: `src/tools/brave_tool.py` (create)
- Modify: `tests/test_tools.py` (add test)

- [ ] **Step 1: Add test to `tests/test_tools.py`**

```python
from unittest.mock import patch
from src.tools.brave_tool import search_brave_for_promotions

def test_brave_tool_returns_list():
    mock_response = {
        "web": {
            "results": [
                {
                    "title": "C6 Carbon aprova com 15k de renda",
                    "description": "Promoção especial até junho...",
                    "url": "https://hardmob.com.br/thread/123",
                }
            ]
        }
    }
    with patch("src.tools.brave_tool.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: None
        results = search_brave_for_promotions.invoke({"query": "C6 Carbon promoção"})

    assert len(results) == 1
    assert results[0]["title"] == "C6 Carbon aprova com 15k de renda"
    assert results[0]["source_name"] == "Brave Search"
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m pytest tests/test_tools.py::test_brave_tool_returns_list -v
```

Expected: `ModuleNotFoundError: No module named 'src.tools.brave_tool'`

- [ ] **Step 3: Create `src/tools/brave_tool.py`**

```python
import os
import requests
from langchain_core.tools import tool

_BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"

@tool
def search_brave_for_promotions(query: str) -> list[dict]:
    """Search the web via Brave Search API for premium card promotions.

    Args:
        query: search terms (e.g. 'cartão black promoção anuidade')

    Returns:
        List of dicts with keys: title, description, url, source_name
    """
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.environ["BRAVE_SEARCH_API_KEY"],
    }
    params = {"q": query, "count": 10, "freshness": "pd"}
    response = requests.get(_BRAVE_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return [
        {
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "source_name": "Brave Search",
        }
        for item in data.get("web", {}).get("results", [])
    ]
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest tests/test_tools.py -v
```

Expected: all tests PASS

---

### Task 5: Web Scraper Tool (Playwright)

**Files:**
- Create: `src/tools/scraper_tool.py`
- Modify: `tests/test_tools.py` (add test)

- [ ] **Step 1: Add test to `tests/test_tools.py`**

```python
from unittest.mock import MagicMock, patch
from src.tools.scraper_tool import scrape_hardmob_for_black_cards

def test_scraper_returns_list_on_success():
    mock_thread = MagicMock()
    mock_thread.inner_text.return_value = "Inter Black aprovado com facilidade"
    mock_thread.get_attribute.return_value = "https://hardmob.com.br/thread/456"

    with patch("src.tools.scraper_tool.sync_playwright") as mock_pw:
        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_thread]
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value = mock_page
        results = scrape_hardmob_for_black_cards.invoke({})

    assert isinstance(results, list)

def test_scraper_returns_empty_list_on_error():
    with patch("src.tools.scraper_tool.sync_playwright") as mock_pw:
        mock_pw.return_value.__enter__.return_value.chromium.launch.side_effect = Exception("network error")
        results = scrape_hardmob_for_black_cards.invoke({})
    assert results == []
```

- [ ] **Step 2: Run tests to verify failure**

```bash
python -m pytest tests/test_tools.py::test_scraper_returns_list_on_success tests/test_tools.py::test_scraper_returns_empty_list_on_error -v
```

Expected: `ModuleNotFoundError: No module named 'src.tools.scraper_tool'`

- [ ] **Step 3: Create `src/tools/scraper_tool.py`**

```python
from playwright.sync_api import sync_playwright
from langchain_core.tools import tool

_BLACK_KEYWORDS = ["black", "premium", "infinite", "ultravioleta", "carbon", "platinum"]
_HARDMOB_URL = "https://www.hardmob.com.br/forums/295-Cartoes-de-Credito"

@tool
def scrape_hardmob_for_black_cards() -> list[dict]:
    """Scrape Hardmob credit card forum for recent black/premium card threads.

    Returns:
        List of dicts with keys: title, url, source_name
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(_HARDMOB_URL, timeout=15000)
            page.wait_for_selector("h3.threadtitle", timeout=5000)
            threads = page.query_selector_all("h3.threadtitle a")
            results = []
            for thread in threads[:20]:
                title = thread.inner_text()
                if any(kw in title.lower() for kw in _BLACK_KEYWORDS):
                    results.append({
                        "title": title,
                        "url": thread.get_attribute("href") or _HARDMOB_URL,
                        "source_name": "Hardmob",
                    })
            browser.close()
            return results
    except Exception:
        return []
```

- [ ] **Step 4: Run all tool tests**

```bash
python -m pytest tests/test_tools.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add src/tools/ tests/test_tools.py
git commit -m "feat: add Reddit, Brave Search, and Playwright scraper tools"
```

---

## Phase 3: Agent Core

### Task 6: Agent State + Graph Skeleton

**Files:**
- Create: `src/agent/state.py`
- Create: `src/agent/graph.py`
- Create: `tests/test_nodes.py`

- [ ] **Step 1: Create `src/agent/state.py`**

```python
from typing import TypedDict

class CardBuzz(TypedDict):
    card_name: str
    buzz_score: int
    mentions_count: int
    sources: list[str]

class RawPromo(TypedDict):
    card_name: str
    text: str
    url: str
    source_name: str

class ValidatedPromo(TypedDict):
    card_name: str
    summary: str
    urls: list[str]
    confidence: int  # 1=baixo, 2=médio, 3=alto
    sources: list[str]

class AgentState(TypedDict):
    cycle_id: str
    discovered_cards: list[CardBuzz]
    raw_promos: list[RawPromo]
    validated_promos: list[ValidatedPromo]
    alerts_sent: list[str]
```

- [ ] **Step 2: Write failing test for graph**

Create `tests/test_nodes.py`:
```python
from src.agent.state import AgentState
from src.agent.graph import build_graph

def test_graph_compiles():
    graph = build_graph()
    assert graph is not None

def test_initial_state_structure():
    state: AgentState = {
        "cycle_id": "test-cycle",
        "discovered_cards": [],
        "raw_promos": [],
        "validated_promos": [],
        "alerts_sent": [],
    }
    assert state["cycle_id"] == "test-cycle"
    assert state["discovered_cards"] == []
```

- [ ] **Step 3: Run to verify failure**

```bash
python -m pytest tests/test_nodes.py::test_graph_compiles -v
```

Expected: `ModuleNotFoundError: No module named 'src.agent.graph'`

- [ ] **Step 4: Create placeholder nodes (stubs) + `src/agent/graph.py`**

Create stubs for each node file first (full implementation in Tasks 7-10):

`src/agent/nodes/discovery.py`:
```python
from ..state import AgentState

def discovery_node(state: AgentState) -> AgentState:
    return state
```

`src/agent/nodes/promo_search.py`:
```python
from ..state import AgentState

def promo_search_node(state: AgentState) -> AgentState:
    return state
```

`src/agent/nodes/cross_validate.py`:
```python
from ..state import AgentState

def cross_validate_node(state: AgentState) -> AgentState:
    return state
```

`src/agent/nodes/persist_alert.py`:
```python
from ..state import AgentState

def persist_alert_node(state: AgentState) -> AgentState:
    return state
```

Now `src/agent/graph.py`:
```python
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.discovery import discovery_node
from .nodes.promo_search import promo_search_node
from .nodes.cross_validate import cross_validate_node
from .nodes.persist_alert import persist_alert_node

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("discovery", discovery_node)
    graph.add_node("promo_search", promo_search_node)
    graph.add_node("cross_validate", cross_validate_node)
    graph.add_node("persist_alert", persist_alert_node)

    graph.set_entry_point("discovery")
    graph.add_edge("discovery", "promo_search")
    graph.add_edge("promo_search", "cross_validate")
    graph.add_edge("cross_validate", "persist_alert")
    graph.add_edge("persist_alert", END)

    return graph.compile()
```

- [ ] **Step 5: Run tests to verify pass**

```bash
python -m pytest tests/test_nodes.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/agent/ tests/test_nodes.py
git commit -m "feat: add agent state types and LangGraph pipeline skeleton"
```

---

### Task 7: Discovery Node (real implementation)

**Files:**
- Modify: `src/agent/nodes/discovery.py`
- Modify: `tests/test_nodes.py` (add test)

- [ ] **Step 1: Add test**

Add to `tests/test_nodes.py`:
```python
from unittest.mock import patch, MagicMock
from src.agent.nodes.discovery import discovery_node
from src.agent.state import AgentState

def _base_state() -> AgentState:
    return {
        "cycle_id": "",
        "discovered_cards": [],
        "raw_promos": [],
        "validated_promos": [],
        "alerts_sent": [],
    }

def test_discovery_node_populates_discovered_cards():
    mock_reddit_results = [{"title": "Inter Black aprovado", "text": "", "url": "https://reddit.com/1", "score": 10, "source_name": "Reddit r/investimentos"}]
    mock_brave_results = [{"title": "C6 Carbon promoção", "description": "Aprovação fácil", "url": "https://hardmob.com/1", "source_name": "Brave Search"}]

    mock_llm_response = MagicMock()
    mock_llm_response.content = '{"cards": [{"card_name": "Inter Black", "buzz_score": 8, "mentions_count": 2, "sources": ["Reddit r/investimentos", "Brave Search"]}]}'

    with patch("src.agent.nodes.discovery.search_reddit_for_black_cards") as mock_reddit, \
         patch("src.agent.nodes.discovery.search_brave_for_promotions") as mock_brave, \
         patch("src.agent.nodes.discovery.ChatAnthropic") as MockLLM:

        mock_reddit.invoke.return_value = mock_reddit_results
        mock_brave.invoke.return_value = mock_brave_results
        MockLLM.return_value.invoke.return_value = mock_llm_response

        result = discovery_node(_base_state())

    assert len(result["discovered_cards"]) == 1
    assert result["discovered_cards"][0]["card_name"] == "Inter Black"
    assert result["cycle_id"] != ""
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_nodes.py::test_discovery_node_populates_discovered_cards -v
```

Expected: FAIL (stub returns empty state)

- [ ] **Step 3: Implement `src/agent/nodes/discovery.py`**

```python
import json
import re
import uuid
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from ..state import AgentState, CardBuzz
from ...tools.reddit_tool import search_reddit_for_black_cards
from ...tools.brave_tool import search_brave_for_promotions

_llm = ChatAnthropic(model="claude-sonnet-4-6")

def discovery_node(state: AgentState) -> AgentState:
    reddit_results = search_reddit_for_black_cards.invoke({"query": "cartão black premium promoção 2026"})
    brave_results = search_brave_for_promotions.invoke({"query": "cartão black premium promoção aprovação hoje 2026 site:reddit.com OR site:hardmob.com.br OR site:reclameaqui.com.br"})

    text_lines = [f"- {r['title']}" for r in reddit_results + brave_results]
    all_text = "\n".join(text_lines) or "Sem menções encontradas"

    response = _llm.invoke([HumanMessage(content=f"""Analise as menções abaixo de cartões de crédito premium/black encontradas hoje.
Liste APENAS os cartões premium/black distintos mencionados com promoções ou buzz positivo.
Inclua qualquer cartão premium mencionado — não se limite a uma lista fixa.

Menções encontradas hoje:
{all_text}

Responda SOMENTE em JSON válido, sem markdown nem explicações:
{{"cards": [{{"card_name": "Nome Completo do Cartão", "buzz_score": 8, "mentions_count": 3, "sources": ["Reddit r/investimentos"]}}]}}

Se não houver menções relevantes, retorne: {{"cards": []}}""")])

    match = re.search(r'\{.*\}', response.content, re.DOTALL)
    try:
        data: dict = json.loads(match.group()) if match else {"cards": []}
    except json.JSONDecodeError:
        data = {"cards": []}

    return {
        **state,
        "cycle_id": str(uuid.uuid4()),
        "discovered_cards": data.get("cards", []),
    }
```

- [ ] **Step 4: Run to verify pass**

```bash
python -m pytest tests/test_nodes.py::test_discovery_node_populates_discovered_cards -v
```

Expected: PASS

---

### Task 8: PromoSearch Node

**Files:**
- Modify: `src/agent/nodes/promo_search.py`
- Modify: `tests/test_nodes.py` (add test)

- [ ] **Step 1: Add test**

Add to `tests/test_nodes.py`:
```python
from src.agent.nodes.promo_search import promo_search_node

def test_promo_search_node_populates_raw_promos():
    state = {**_base_state(), "discovered_cards": [
        {"card_name": "Inter Black", "buzz_score": 8, "mentions_count": 2, "sources": ["Reddit"]}
    ]}
    mock_brave = [{"title": "Inter Black anuidade zero", "description": "Promoção válida por 12 meses", "url": "https://example.com", "source_name": "Brave Search"}]

    with patch("src.agent.nodes.promo_search.search_brave_for_promotions") as mock_b, \
         patch("src.agent.nodes.promo_search.search_reddit_for_black_cards") as mock_r:
        mock_b.invoke.return_value = mock_brave
        mock_r.invoke.return_value = []
        result = promo_search_node(state)

    assert len(result["raw_promos"]) > 0
    assert result["raw_promos"][0]["card_name"] == "Inter Black"
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_nodes.py::test_promo_search_node_populates_raw_promos -v
```

Expected: FAIL

- [ ] **Step 3: Implement `src/agent/nodes/promo_search.py`**

```python
from ..state import AgentState, RawPromo
from ...tools.reddit_tool import search_reddit_for_black_cards
from ...tools.brave_tool import search_brave_for_promotions
from ...tools.scraper_tool import scrape_hardmob_for_black_cards

_PROMO_KEYWORDS = ["promoção", "promocao", "anuidade", "aprovado", "aprovação", "bônus", "bonus", "isenção", "isencao", "facilidade", "black", "gratuito"]

def _is_promo_related(text: str) -> bool:
    return any(kw in text.lower() for kw in _PROMO_KEYWORDS)

def promo_search_node(state: AgentState) -> AgentState:
    raw_promos: list[RawPromo] = []

    for card in state["discovered_cards"]:
        card_name = card["card_name"]
        query = f"{card_name} promoção aprovação anuidade 2026"

        brave_results = search_brave_for_promotions.invoke({"query": query})
        for r in brave_results:
            text = f"{r['title']} {r['description']}"
            if _is_promo_related(text):
                raw_promos.append(RawPromo(
                    card_name=card_name,
                    text=text[:300],
                    url=r["url"],
                    source_name=r["source_name"],
                ))

        reddit_results = search_reddit_for_black_cards.invoke({"query": query})
        for r in reddit_results:
            text = f"{r['title']} {r['text']}"
            if _is_promo_related(text):
                raw_promos.append(RawPromo(
                    card_name=card_name,
                    text=text[:300],
                    url=r["url"],
                    source_name=r["source_name"],
                ))

    hardmob_results = scrape_hardmob_for_black_cards.invoke({})
    for r in hardmob_results:
        raw_promos.append(RawPromo(
            card_name="Descoberta Hardmob",
            text=r["title"],
            url=r["url"],
            source_name="Hardmob",
        ))

    return {**state, "raw_promos": raw_promos}
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_nodes.py -v
```

Expected: all PASS

---

### Task 9: CrossValidate Node

**Files:**
- Modify: `src/agent/nodes/cross_validate.py`
- Modify: `tests/test_nodes.py` (add test)

- [ ] **Step 1: Add test**

Add to `tests/test_nodes.py`:
```python
from src.agent.nodes.cross_validate import cross_validate_node

def test_cross_validate_requires_min_sources():
    """Promos with only 1 source should not pass validation (MIN_SOURCES_TO_VALIDATE=2)."""
    state = {**_base_state(), "raw_promos": [
        {"card_name": "BTG Black", "text": "50k bônus na adesão", "url": "https://reddit.com/1", "source_name": "Reddit r/investimentos"},
        {"card_name": "BTG Black", "text": "50k bônus na adesão de BTG", "url": "https://hardmob.com/1", "source_name": "Hardmob"},
        {"card_name": "Cartão X Desconhecido", "text": "oferta especial", "url": "https://spam.com", "source_name": "Brave Search"},
    ]}

    mock_response = MagicMock()
    mock_response.content = '[{"card_name": "BTG Black", "summary": "Bônus de 50k pontos na adesão ao BTG Black", "confidence": 2, "urls": ["https://reddit.com/1", "https://hardmob.com/1"], "sources": ["Reddit r/investimentos", "Hardmob"]}]'

    with patch("src.agent.nodes.cross_validate.ChatAnthropic") as MockLLM:
        MockLLM.return_value.invoke.return_value = mock_response
        result = cross_validate_node(state)

    assert len(result["validated_promos"]) == 1
    assert result["validated_promos"][0]["card_name"] == "BTG Black"
    assert result["validated_promos"][0]["confidence"] >= 2

def test_cross_validate_empty_when_no_promos():
    result = cross_validate_node(_base_state())
    assert result["validated_promos"] == []
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_nodes.py::test_cross_validate_requires_min_sources tests/test_nodes.py::test_cross_validate_empty_when_no_promos -v
```

Expected: FAIL

- [ ] **Step 3: Implement `src/agent/nodes/cross_validate.py`**

```python
import json
import os
import re
from collections import defaultdict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from ..state import AgentState, RawPromo, ValidatedPromo

_llm = ChatAnthropic(model="claude-sonnet-4-6")
_MIN_SOURCES = int(os.getenv("MIN_SOURCES_TO_VALIDATE", "2"))

def cross_validate_node(state: AgentState) -> AgentState:
    if not state["raw_promos"]:
        return {**state, "validated_promos": []}

    by_card: dict[str, list[RawPromo]] = defaultdict(list)
    for promo in state["raw_promos"]:
        by_card[promo["card_name"]].append(promo)

    candidates = []
    for card_name, promos in by_card.items():
        unique_sources = list({p["source_name"] for p in promos})
        if len(unique_sources) >= _MIN_SOURCES:
            candidates.append({
                "card_name": card_name,
                "texts": [p["text"] for p in promos],
                "urls": [p["url"] for p in promos],
                "sources": unique_sources,
            })

    if not candidates:
        return {**state, "validated_promos": []}

    prompt_data = json.dumps(candidates, ensure_ascii=False)
    response = _llm.invoke([HumanMessage(content=f"""Analise as seguintes promoções de cartões premium/black coletadas de múltiplas fontes.
Para cada grupo, gere um resumo claro e objetivo da promoção em português.
Atribua confidence: 1 (1 fonte), 2 (2 fontes), 3 (3+ fontes).

Dados:
{prompt_data}

Responda SOMENTE em JSON válido sem markdown:
[{{"card_name": "...", "summary": "Resumo claro da promoção", "confidence": 2, "urls": [...], "sources": [...]}}]

Se nenhuma promoção for legítima, retorne: []""")])

    match = re.search(r'\[.*\]', response.content, re.DOTALL)
    try:
        validated: list[ValidatedPromo] = json.loads(match.group()) if match else []
    except json.JSONDecodeError:
        validated = []

    return {**state, "validated_promos": validated}
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_nodes.py -v
```

Expected: all PASS

---

### Task 10: Persist & Alert Node

**Files:**
- Modify: `src/agent/nodes/persist_alert.py`
- Modify: `tests/test_nodes.py` (add test)

- [ ] **Step 1: Add test**

Add to `tests/test_nodes.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.agent.nodes.persist_alert import persist_alert_node

def test_persist_alert_saves_new_promos_to_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    state = {**_base_state(), "validated_promos": [
        {"card_name": "Nubank Ultra", "summary": "Cashback 5% por 3 meses", "confidence": 2,
         "urls": ["https://reddit.com/1", "https://hardmob.com/1"], "sources": ["Reddit", "Hardmob"]}
    ]}

    with patch("src.agent.nodes.persist_alert.SessionLocal", return_value=db), \
         patch("src.agent.nodes.persist_alert._send_telegram_alert") as mock_tg:
        result = persist_alert_node(state)

    assert len(result["alerts_sent"]) == 1
    mock_tg.assert_called_once()
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_nodes.py::test_persist_alert_saves_new_promos_to_db -v
```

Expected: FAIL

- [ ] **Step 3: Implement `src/agent/nodes/persist_alert.py`**

```python
import asyncio
import logging
import os
import telegram
from ..state import AgentState
from ...db.database import SessionLocal
from ...db.repository import upsert_promotion, mark_alerted

logger = logging.getLogger(__name__)

def _send_telegram_alert(promo_summary: str, card_name: str, confidence: int, urls: list[str]) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        logger.warning("Telegram não configurado — alerta suprimido")
        return

    conf_label = {1: "🟡 Baixa", 2: "🟡 Média", 3: "🟢 Alta"}.get(confidence, "🔵")
    sources_text = "\n".join(f"  • {u}" for u in urls[:3])
    message = (
        f"🃏 *CARD WATCH BR — Nova Promoção!*\n\n"
        f"📌 *Cartão:* {card_name}\n"
        f"💬 {promo_summary}\n"
        f"✅ Confiança: {conf_label}\n\n"
        f"📎 Fontes:\n{sources_text}"
    )

    async def _send():
        bot = telegram.Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

    try:
        asyncio.run(_send())
    except Exception as e:
        logger.error("Erro ao enviar alerta Telegram: %s", e)

def persist_alert_node(state: AgentState) -> AgentState:
    alerts_sent: list[str] = []
    db = SessionLocal()
    try:
        for promo in state["validated_promos"]:
            saved, is_new = upsert_promotion(
                db,
                card_name=promo["card_name"],
                summary=promo["summary"],
                sources=promo["sources"],
                confidence=promo["confidence"],
                raw_urls=promo["urls"],
            )
            if is_new:
                _send_telegram_alert(promo["summary"], promo["card_name"], promo["confidence"], promo["urls"])
                mark_alerted(db, saved.id)
                alerts_sent.append(saved.id)
    finally:
        db.close()

    return {**state, "alerts_sent": alerts_sent}
```

- [ ] **Step 4: Run all node tests**

```bash
python -m pytest tests/test_nodes.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add src/agent/nodes/ tests/test_nodes.py
git commit -m "feat: implement all 4 LangGraph agent nodes (discovery, search, validate, persist)"
```

---

### Task 19: Anti-Piracy, License, Training Docs, and conftest

**Files:**
- Create: `LICENSE`
- Create: `docs/anti-piracy.md`
- Create: `docs/guia-claude-code.md`
- Create: `docs/guia-skills.md`
- Create: `docs/guia-hooks.md`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `tests/conftest.py`** (shared fixtures)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()
```

- [ ] **Step 2: Create `LICENSE`**

```
MIT License

Copyright (c) 2026 Hugo Ramos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Create `docs/anti-piracy.md`**

```markdown
# Uso Aceitável e Anti-Pirataria

## Licença

Este projeto é licenciado sob MIT. Você pode usar, modificar e distribuir livremente,
desde que mantenha a atribuição de copyright.

## Proteção de Secrets

NUNCA cometa arquivos com dados sensíveis:
- `.env` está no `.gitignore` — jamais remova essa linha
- API keys devem estar SEMPRE em variáveis de ambiente
- O CI (security-scan.yml) bloqueia PRs com secrets detectados via Gitleaks

## Uso Responsável das APIs

- **Reddit PRAW:** respeite rate limits (60 req/min). Use `time_filter="day"` para buscas recentes
- **Brave Search:** plano gratuito = 2.000 req/mês. Ciclos de 2h = ~360 req/mês. Dentro do limite
- **Playwright:** não sobrescreva mecanismos anti-bot. Use headless e respeite `robots.txt`

## O que NÃO fazer

- Não use este projeto para spam ou scraping agressivo
- Não revenda os dados coletados sem atribuição
- Não remova avisos de copyright do código
```

- [ ] **Step 4: Create `docs/guia-claude-code.md`**

```markdown
# Guia de Claude Code — Boas Práticas

## O que é Claude Code

Claude Code é uma CLI interativa da Anthropic que auxilia no desenvolvimento de software.
Ele lê seu projeto, entende o contexto e executa tarefas complexas de forma autônoma.

## Configuração Inicial

1. Instale: `npm install -g @anthropic-ai/claude-code`
2. Configure: `claude` (abre a interface)
3. Crie um `CLAUDE.md` na raiz — é a "memória do projeto" para o Claude

## Boas Práticas

### CLAUDE.md
- Documente comandos essenciais, arquitetura e variáveis de ambiente
- Mantenha atualizado sempre que a stack mudar
- Seja conciso: Claude lê o arquivo a cada sessão

### Permissões (.claude/settings.json)
- Use `permissions.allow` para liberar comandos seguros (pytest, git, uvicorn)
- Nunca libere `rm -rf` ou comandos destrutivos globalmente

### Commits frequentes
- Faça commit após cada feature funcional
- Mensagens no formato `feat:`, `fix:`, `docs:`, `chore:`

### Não commite secrets
- `.env` no `.gitignore` sempre
- Use `.env.example` como template público

## Skills e Hooks

Ver `docs/guia-skills.md` e `docs/guia-hooks.md` para detalhes.
```

- [ ] **Step 5: Create `docs/guia-skills.md`**

```markdown
# Guia de Skills Customizadas

## O que são Skills

Skills são arquivos Markdown em `.claude/skills/` que ensinam ao Claude Code
como executar tarefas específicas do projeto. Funcionam como "receitas" que
o Claude segue quando o contexto da conversa se encaixa.

## Estrutura de uma Skill

```markdown
---
name: nome-da-skill
description: O que essa skill faz
triggers:
  - "frase que ativa a skill"
  - "outra frase trigger"
---

# Nome da Skill

## Steps

1. Primeiro passo
   ```bash
   comando aqui
   ```

2. Segundo passo
```

## Skills deste projeto

| Skill | Quando usar |
|-------|-------------|
| `run-agent` | Executar ciclo manual de busca |
| `add-source` | Adicionar nova fonte de dados |
| `debug-search` | Depurar ciclo sem resultados |

## Criando uma nova Skill

1. Crie `.claude/skills/minha-skill.md`
2. Adicione frontmatter com `name`, `description`, `triggers`
3. Descreva os passos claramente com comandos exatos
4. Teste: mencione um dos triggers na conversa com Claude Code
```

- [ ] **Step 6: Create `docs/guia-hooks.md`**

```markdown
# Guia de Hooks

## O que são Hooks

Hooks são scripts executados automaticamente em eventos do Claude Code:
antes/depois de usar ferramentas (`PreToolUse`, `PostToolUse`),
antes de parar (`Stop`), etc.

Configurados em `.claude/settings.json` na chave `"hooks"`.

## Hooks deste projeto

### pre-search (`hooks/pre-search.py`)
- **Quando:** antes de qualquer comando Bash
- **O que faz:** valida que todas as API keys estão no `.env`
- **Por que:** evita ciclos que falham silenciosamente por falta de credenciais

### post-alert (`hooks/post-alert.py`)
- **Quando:** após rodar o scheduler
- **O que faz:** registra timestamp em `logs/alerts.log`
- **Por que:** auditoria de quando alertas foram enviados

## Estrutura no settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "python hooks/pre-search.py"}]
      }
    ]
  }
}
```

## Criando um novo Hook

1. Crie o script em `hooks/meu-hook.py`
2. Adicione a entrada em `.claude/settings.json`
3. Teste manualmente: `python hooks/meu-hook.py`
4. Verifique que não bloqueia fluxos legítimos (exit code 0 = OK, 1 = bloqueia)
```

- [ ] **Step 7: Commit**

```bash
git add LICENSE docs/ tests/conftest.py
git commit -m "docs: add LICENSE, anti-piracy policy, Claude Code training guides, and conftest"
```

---

## Phase 4: Interfaces

### Task 11: FastAPI Dashboard

**Files:**
- Create: `src/api/main.py`
- Create: `src/api/routes.py`
- Create: `src/api/templates/index.html`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_api.py`:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.db.repository import upsert_promotion
from src.api.main import app
from src.db.database import get_db

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        db = TestSession()
        upsert_promotion(db, "Inter Black", "Anuidade zero", ["Reddit"], 2, ["https://url.com"])
        db.close()
        yield c
    app.dependency_overrides.clear()

def test_get_dashboard_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200

def test_get_promotions_returns_list(client):
    response = client.get("/api/promotions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["card_name"] == "Inter Black"

def test_dismiss_promotion(client):
    promos = client.get("/api/promotions").json()
    promo_id = promos[0]["id"]
    response = client.post(f"/api/promotions/{promo_id}/dismiss")
    assert response.status_code == 200
    assert client.get("/api/promotions").json() == []
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_api.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create `src/api/routes.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.repository import get_promotions, dismiss_promotion
from pathlib import Path

router = APIRouter()
_TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

@router.get("/", response_class=HTMLResponse)
def dashboard():
    return _TEMPLATE

@router.get("/api/promotions")
def list_promotions(db: Session = Depends(get_db)):
    promos = get_promotions(db)
    return [
        {
            "id": p.id,
            "card_name": p.card_name,
            "summary": p.summary,
            "sources": p.sources,
            "confidence": p.confidence,
            "raw_urls": p.raw_urls,
            "found_at": p.found_at.isoformat() if p.found_at else None,
        }
        for p in promos
    ]

@router.post("/api/promotions/{promo_id}/dismiss")
def dismiss(promo_id: str, db: Session = Depends(get_db)):
    ok = dismiss_promotion(db, promo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return {"status": "dismissed"}

@router.get("/api/cycles")
def list_cycles(db: Session = Depends(get_db)):
    from src.db.models import Cycle
    cycles = db.query(Cycle).order_by(Cycle.started_at.desc()).limit(20).all()
    return [
        {
            "id": c.id,
            "started_at": c.started_at.isoformat() if c.started_at else None,
            "finished_at": c.finished_at.isoformat() if c.finished_at else None,
            "cards_found": c.cards_found,
            "promos_validated": c.promos_validated,
        }
        for c in cycles
    ]
```

- [ ] **Step 4: Create `src/api/main.py`**

```python
from fastapi import FastAPI
from src.db.database import create_tables
from src.api.routes import router

app = FastAPI(title="Card Watch BR")
app.include_router(router)

@app.on_event("startup")
def startup():
    create_tables()
```

- [ ] **Step 5: Create `src/api/templates/index.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Card Watch BR</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen p-6">
  <header class="mb-8">
    <h1 class="text-3xl font-bold text-purple-400">🃏 Card Watch BR</h1>
    <p class="text-gray-400 mt-1">Monitor de promoções de cartões black e premium</p>
  </header>

  <div class="flex gap-3 mb-6">
    <select id="filterConf" onchange="loadPromos()" class="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
      <option value="">Todas as confianças</option>
      <option value="3">🟢 Alta (3 fontes)</option>
      <option value="2">🟡 Média (2 fontes)</option>
      <option value="1">🔴 Baixa (1 fonte)</option>
    </select>
    <button onclick="triggerCycle()" class="bg-purple-700 hover:bg-purple-600 px-4 py-2 rounded text-sm font-medium">
      🔄 Buscar Agora
    </button>
  </div>

  <div id="promos" class="space-y-4"></div>

  <script>
    async function loadPromos() {
      const conf = document.getElementById('filterConf').value;
      const res = await fetch('/api/promotions');
      const promos = await res.json();
      const filtered = conf ? promos.filter(p => p.confidence == conf) : promos;
      const confLabel = {1:'🔴 Baixa',2:'🟡 Média',3:'🟢 Alta'};
      document.getElementById('promos').innerHTML = filtered.length === 0
        ? '<p class="text-gray-500">Nenhuma promoção encontrada.</p>'
        : filtered.map(p => `
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div class="flex justify-between items-start">
              <div>
                <span class="text-xs text-gray-500">${confLabel[p.confidence] || ''} — ${p.sources.join(' · ')}</span>
                <h2 class="text-lg font-semibold text-white mt-1">${p.card_name}</h2>
                <p class="text-gray-300 mt-1">${p.summary}</p>
                <div class="mt-2 flex flex-wrap gap-2">
                  ${p.raw_urls.slice(0,2).map(u => `<a href="${u}" target="_blank" class="text-purple-400 text-xs hover:underline">Ver fonte →</a>`).join('')}
                </div>
              </div>
              <button onclick="dismiss('${p.id}')" class="text-gray-600 hover:text-red-400 text-xs ml-4">✕ Descartar</button>
            </div>
          </div>`).join('');
    }

    async function dismiss(id) {
      await fetch('/api/promotions/' + id + '/dismiss', {method:'POST'});
      loadPromos();
    }

    async function triggerCycle() {
      await fetch('/api/cycles/trigger', {method:'POST'});
      alert('Ciclo de busca iniciado! Aguarde alguns minutos.');
    }

    loadPromos();
    setInterval(loadPromos, 60000);
  </script>
</body>
</html>
```

- [ ] **Step 6: Run tests**

```bash
python -m pytest tests/test_api.py -v
```

Expected: all PASS

- [ ] **Step 7: Commit**

```bash
git add src/api/ tests/test_api.py
git commit -m "feat: add FastAPI dashboard with HTML/Tailwind frontend"
```

---

### Task 12: Telegram Bot

**Files:**
- Create: `src/bot/bot.py`
- Create: `tests/test_bot.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_bot.py`:
```python
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from src.bot.bot import format_status_message, format_promo_list

def test_format_status_message():
    msg = format_status_message(cards_found=5, promos_validated=2, alerts_sent=1)
    assert "5" in msg
    assert "2" in msg
    assert "1" in msg

def test_format_promo_list_empty():
    msg = format_promo_list([])
    assert "nenhuma" in msg.lower()

def test_format_promo_list_with_promos():
    promos = [{"card_name": "Inter Black", "summary": "Anuidade zero", "confidence": 2}]
    msg = format_promo_list(promos)
    assert "Inter Black" in msg
    assert "Anuidade zero" in msg
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_bot.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create `src/bot/bot.py`**

```python
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.db.database import SessionLocal
from src.db.repository import get_promotions
from src.agent.graph import build_graph
from src.agent.state import AgentState
import uuid

logger = logging.getLogger(__name__)

def format_status_message(cards_found: int, promos_validated: int, alerts_sent: int) -> str:
    return (
        f"📊 *Status do último ciclo*\n\n"
        f"🔍 Cartões encontrados: *{cards_found}*\n"
        f"✅ Promoções validadas: *{promos_validated}*\n"
        f"🔔 Alertas enviados: *{alerts_sent}*"
    )

def format_promo_list(promos: list[dict]) -> str:
    if not promos:
        return "Nenhuma promoção ativa no momento."
    conf_label = {1: "🔴", 2: "🟡", 3: "🟢"}
    lines = []
    for p in promos[:5]:
        label = conf_label.get(p.get("confidence", 1), "🔵")
        lines.append(f"{label} *{p['card_name']}*\n  {p['summary']}")
    return "\n\n".join(lines)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        format_status_message(0, 0, 0),
        parse_mode="Markdown"
    )

async def cmd_promos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = SessionLocal()
    try:
        promos = get_promotions(db)
        promo_dicts = [{"card_name": p.card_name, "summary": p.summary, "confidence": p.confidence} for p in promos]
        await update.message.reply_text(format_promo_list(promo_dicts), parse_mode="Markdown")
    finally:
        db.close()

async def cmd_buscar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🔄 Iniciando busca... Pode levar alguns minutos.")
    graph = build_graph()
    initial: AgentState = {
        "cycle_id": str(uuid.uuid4()),
        "discovered_cards": [],
        "raw_promos": [],
        "validated_promos": [],
        "alerts_sent": [],
    }
    result = graph.invoke(initial)
    await update.message.reply_text(
        format_status_message(
            len(result["discovered_cards"]),
            len(result["validated_promos"]),
            len(result["alerts_sent"]),
        ),
        parse_mode="Markdown"
    )

def create_bot() -> Application:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("promos", cmd_promos))
    app.add_handler(CommandHandler("buscar", cmd_buscar))
    return app

if __name__ == "__main__":
    create_bot().run_polling()
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_bot.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot/ tests/test_bot.py
git commit -m "feat: add Telegram bot with /status, /promos, /buscar commands"
```

---

## Phase 5: Integration

### Task 13: Scheduler + Full Integration

**Files:**
- Create: `src/scheduler.py`

- [ ] **Step 1: Create `src/scheduler.py`**

```python
#!/usr/bin/env python3
"""Entry point for the Card Watch BR scheduler.

Usage:
  python src/scheduler.py          # run scheduler loop (every SEARCH_INTERVAL_HOURS)
  python src/scheduler.py --once   # run one cycle and exit
"""
import argparse
import logging
import os
import uuid
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from src.agent.graph import build_graph
from src.agent.state import AgentState
from src.db.database import create_tables, SessionLocal
from src.db.models import Cycle

def run_cycle() -> None:
    logger.info("=== Iniciando ciclo de busca ===")
    db = SessionLocal()
    cycle = Cycle(id=str(uuid.uuid4()), started_at=datetime.now(timezone.utc))
    db.add(cycle)
    db.commit()

    try:
        graph = build_graph()
        initial: AgentState = {
            "cycle_id": cycle.id,
            "discovered_cards": [],
            "raw_promos": [],
            "validated_promos": [],
            "alerts_sent": [],
        }
        result = graph.invoke(initial)

        cycle.finished_at = datetime.now(timezone.utc)
        cycle.cards_found = len(result["discovered_cards"])
        cycle.promos_found = len(result["raw_promos"])
        cycle.promos_validated = len(result["validated_promos"])
        db.commit()

        logger.info(
            "Ciclo concluído: %d cartões, %d promos validadas, %d alertas enviados",
            cycle.cards_found, cycle.promos_validated, len(result["alerts_sent"])
        )
    except Exception:
        logger.exception("Erro durante o ciclo")
    finally:
        db.close()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Executa um ciclo e sai")
    args = parser.parse_args()

    create_tables()

    if args.once:
        run_cycle()
        return

    interval = int(os.getenv("SEARCH_INTERVAL_HOURS", "2"))
    scheduler = BlockingScheduler()
    scheduler.add_job(run_cycle, "interval", hours=interval)
    logger.info("Scheduler iniciado — ciclos a cada %dh. Ctrl+C para parar.", interval)
    run_cycle()  # run immediately on start
    scheduler.start()

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add trigger route to `src/api/routes.py`**

Add this import at the top of `src/api/routes.py`:
```python
from threading import Thread
from src.scheduler import run_cycle
```

Add this route:
```python
@router.post("/api/cycles/trigger")
def trigger_cycle():
    Thread(target=run_cycle, daemon=True).start()
    return {"status": "started"}
```

- [ ] **Step 3: Smoke test with --once (requires real API keys)**

```bash
cp .env.example .env
# Preencha as chaves no .env antes de continuar
python src/scheduler.py --once
```

Expected output:
```
=== Iniciando ciclo de busca ===
Ciclo concluído: X cartões, Y promos validadas, Z alertas enviados
```

- [ ] **Step 4: Smoke test dashboard**

```bash
uvicorn src.api.main:app --port 8000 --reload
```

Open `http://localhost:8000` — dashboard must load with promotions (or "nenhuma promoção").

- [ ] **Step 5: Commit**

```bash
git add src/scheduler.py src/api/routes.py
git commit -m "feat: add APScheduler integration and cycle trigger API endpoint"
```

---

## Phase 6: Claude Code Training Artifacts

### Task 14: CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create `CLAUDE.md`**

```markdown
# Card Watch BR

Monitor automático de promoções de cartões black/premium usando LangGraph + Claude.

## Comandos Essenciais

```bash
# Instalar dependências
pip install -r requirements.txt && playwright install chromium

# Configurar variáveis de ambiente
cp .env.example .env  # preencha as chaves antes de usar

# Executar um ciclo de busca (modo manual)
python src/scheduler.py --once

# Iniciar scheduler contínuo
python src/scheduler.py

# Iniciar dashboard web (processo separado)
uvicorn src.api.main:app --port 8000 --reload

# Iniciar bot Telegram
python -m src.bot.bot

# Rodar testes
python -m pytest tests/ -v
```

## Arquitetura

Pipeline LangGraph com 4 nós em sequência:
1. **discovery** (`src/agent/nodes/discovery.py`) — descobre cartões em buzz hoje
2. **promo_search** (`src/agent/nodes/promo_search.py`) — busca promoções por cartão
3. **cross_validate** (`src/agent/nodes/cross_validate.py`) — valida em ≥2 fontes
4. **persist_alert** (`src/agent/nodes/persist_alert.py`) — salva e alerta Telegram

## Variáveis de Ambiente Obrigatórias

- `ANTHROPIC_API_KEY` — para Claude Sonnet 4.6
- `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` — Reddit PRAW API
- `BRAVE_SEARCH_API_KEY` — Brave Search API
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` — alertas Telegram

## Skills Disponíveis

- `run-agent` — executa ciclo manual
- `add-source` — adiciona nova fonte de busca
- `debug-search` — depura ciclo sem resultados

## Estrutura de Pastas

```
src/agent/    — LangGraph agent (nós + graph)
src/tools/    — Reddit, Brave Search, Playwright
src/api/      — FastAPI dashboard
src/bot/      — Telegram bot
src/db/       — SQLAlchemy models + repository
```
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md with project documentation for Claude Code"
```

---

### Task 15: Custom Skills

**Files:**
- Create: `.claude/skills/run-agent.md`
- Create: `.claude/skills/add-source.md`
- Create: `.claude/skills/debug-search.md`

- [ ] **Step 1: Create `.claude/skills/run-agent.md`**

```markdown
---
name: run-agent
description: Executa um ciclo completo de busca por promoções de cartões black
triggers:
  - "executar busca"
  - "rodar ciclo"
  - "buscar promoções"
  - "run agent"
---

# Run Agent Skill

Execute one full search cycle via the scheduler.

## Steps

1. Verify `.env` exists and has required keys:
   ```bash
   python hooks/pre-search.py
   ```

2. Run one cycle:
   ```bash
   python src/scheduler.py --once
   ```

3. Check results:
   ```bash
   # Open dashboard
   uvicorn src.api.main:app --port 8000
   # Then visit http://localhost:8000
   ```

## Expected Output

```
=== Iniciando ciclo de busca ===
Ciclo concluído: X cartões, Y promos validadas, Z alertas enviados
```

If output shows 0 promos, use the `debug-search` skill.
```

- [ ] **Step 2: Create `.claude/skills/add-source.md`**

```markdown
---
name: add-source
description: Guia para adicionar uma nova fonte de busca ao agente
triggers:
  - "adicionar fonte"
  - "novo fórum"
  - "add source"
  - "adicionar site"
---

# Add Source Skill

## Steps to Add a New Search Source

1. Create a new tool file in `src/tools/`:
   ```python
   # src/tools/my_new_source_tool.py
   from langchain_core.tools import tool

   @tool
   def search_my_source(query: str) -> list[dict]:
       """Search MySource for card promotions.
       Returns: list of {title, url, source_name}
       """
       # implementation here
       return []
   ```

2. Write a test in `tests/test_tools.py`:
   ```python
   from src.tools.my_new_source_tool import search_my_source

   def test_my_source_returns_list():
       results = search_my_source.invoke({"query": "cartão black"})
       assert isinstance(results, list)
   ```

3. Import and call the tool in `src/agent/nodes/promo_search.py`:
   ```python
   from ...tools.my_new_source_tool import search_my_source
   # add call inside promo_search_node()
   ```

4. Run tests: `python -m pytest tests/test_tools.py -v`
5. Commit: `git commit -m "feat: add MySource as search tool"`
```

- [ ] **Step 3: Create `.claude/skills/debug-search.md`**

```markdown
---
name: debug-search
description: Checklist de debug quando o agente retorna zero promoções
triggers:
  - "busca vazia"
  - "sem resultados"
  - "zero promoções"
  - "debug search"
  - "agente não encontrou nada"
---

# Debug Search Skill

## Checklist (run in order)

### 1. Check API keys
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('ANTHROPIC:', bool(os.getenv('ANTHROPIC_API_KEY'))); print('REDDIT:', bool(os.getenv('REDDIT_CLIENT_ID'))); print('BRAVE:', bool(os.getenv('BRAVE_SEARCH_API_KEY')))"
```
All must print `True`. If not, fix `.env`.

### 2. Test Reddit tool
```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from src.tools.reddit_tool import search_reddit_for_black_cards
results = search_reddit_for_black_cards.invoke({'query': 'cartao black'})
print(f'Reddit results: {len(results)}')
"
```

### 3. Test Brave Search tool
```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from src.tools.brave_tool import search_brave_for_promotions
results = search_brave_for_promotions.invoke({'query': 'cartao black promoção'})
print(f'Brave results: {len(results)}')
"
```

### 4. Check logs
```bash
cat logs/scheduler.log | tail -50
```

### 5. Run cycle with verbose logging
```bash
PYTHONPATH=. python -c "
import logging; logging.basicConfig(level=logging.DEBUG)
from src.scheduler import run_cycle; run_cycle()
"
```
```

- [ ] **Step 4: Create `.claude/settings.json`**

```json
{
  "skills_dir": ".claude/skills",
  "permissions": {
    "allow": [
      "Bash(python*)",
      "Bash(uvicorn*)",
      "Bash(pytest*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "Bash(git status*)",
      "Bash(git log*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/pre-search.py 2>/dev/null || true"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash(python src/scheduler*)",
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/post-alert.py 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 5: Commit**

```bash
git add .claude/
git commit -m "feat: add Claude Code skills and settings (run-agent, add-source, debug-search)"
```

---

### Task 16: Hooks

**Files:**
- Create: `hooks/pre-search.py`
- Create: `hooks/post-alert.py`

- [ ] **Step 1: Create `hooks/pre-search.py`**

```python
#!/usr/bin/env python3
"""Pre-search hook: validates required env vars before any agent cycle."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

REQUIRED = [
    "ANTHROPIC_API_KEY",
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "BRAVE_SEARCH_API_KEY",
]

missing = [k for k in REQUIRED if not os.getenv(k)]
if missing:
    print(f"❌ Hook pre-search: variáveis ausentes no .env: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

print("✅ Hook pre-search: todas as variáveis de ambiente verificadas.")
```

- [ ] **Step 2: Create `hooks/post-alert.py`**

```python
#!/usr/bin/env python3
"""Post-alert hook: logs sent alerts to logs/alerts.log."""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

log_path = Path("logs/alerts.log")
log_path.parent.mkdir(exist_ok=True)

timestamp = datetime.now(timezone.utc).isoformat()
entry = f"[{timestamp}] Agent cycle completed\n"
log_path.open("a").write(entry)
print(f"✅ Hook post-alert: logged to {log_path}")
```

- [ ] **Step 3: Test hooks manually**

```bash
python hooks/pre-search.py
```

Expected (with `.env` filled): `✅ Hook pre-search: todas as variáveis de ambiente verificadas.`

```bash
python hooks/post-alert.py
```

Expected: `✅ Hook post-alert: logged to logs/alerts.log`

- [ ] **Step 4: Commit**

```bash
git add hooks/
git commit -m "feat: add pre-search and post-alert hooks for environment validation and logging"
```

---

### Task 17: MCP Configuration

**Files:**
- Create: `mcp/brave-search-config.json`
- Create: `docs/guia-mcp.md`

- [ ] **Step 1: Create `mcp/brave-search-config.json`**

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_SEARCH_API_KEY}"
      }
    }
  }
}
```

- [ ] **Step 2: Add MCP server reference to `.claude/settings.json`**

Add after the `"hooks"` block in `.claude/settings.json`:
```json
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_SEARCH_API_KEY}"
      }
    }
  }
```

- [ ] **Step 3: Create `docs/guia-mcp.md`**

```markdown
# Guia de Integração MCP

## O que é MCP?

Model Context Protocol (MCP) é um protocolo aberto que permite ao Claude Code
usar ferramentas externas (servidores MCP) diretamente nas conversas.

## MCP Configurado: Brave Search

O servidor `brave-search` permite que o Claude Code faça buscas na web
diretamente, sem precisar de código intermediário.

### Instalação

Requer Node.js instalado:
```bash
node --version  # deve ser 18+
```

O servidor é instalado automaticamente via `npx` na primeira execução.

### Como usar no Claude Code

Após configurar `.claude/settings.json`, o Claude Code pode usar:
```
use_mcp_tool brave-search search "cartão black promoção"
```

### Verificar se está funcionando

No Claude Code, digite:
```
/mcp
```
Deve listar `brave-search` como servidor disponível.

### Adicionando outros servidores MCP

Consulte https://github.com/modelcontextprotocol/servers para servidores disponíveis.
```

- [ ] **Step 4: Commit**

```bash
git add mcp/ docs/guia-mcp.md .claude/settings.json
git commit -m "feat: configure Brave Search MCP server integration"
```

---

### Task 18: GitHub Actions (Backup + Security Scan)

**Files:**
- Create: `.github/workflows/backup.yml`
- Create: `.github/workflows/security-scan.yml`

- [ ] **Step 1: Create `.github/workflows/backup.yml`**

```yaml
name: Backup on Push

on:
  push:
    branches: [main]

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create backup tag
        run: |
          TAG="backup-$(date +'%Y%m%d-%H%M%S')"
          git config user.email "github-actions@github.com"
          git config user.name "GitHub Actions"
          git tag $TAG
          git push origin $TAG
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: Create `.github/workflows/security-scan.yml`**

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  scan-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  run-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: python -m pytest tests/ -v
        env:
          DATABASE_URL: sqlite:///:memory:
          ANTHROPIC_API_KEY: test-key
          REDDIT_CLIENT_ID: test
          REDDIT_CLIENT_SECRET: test
          BRAVE_SEARCH_API_KEY: test
          TELEGRAM_BOT_TOKEN: test
          TELEGRAM_CHAT_ID: test
```

- [ ] **Step 3: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions for automatic backup tags and security scanning"
```

- [ ] **Step 4: Push to GitHub (one-time setup)**

```bash
# Crie um repositório no GitHub chamado card-watch-br, depois:
git remote add origin https://github.com/SEU_USUARIO/card-watch-br.git
git branch -M main
git push -u origin main
```

Expected: Actions rodam automaticamente no GitHub. Verifique em `Actions` tab.

---

## Verificação Final End-to-End

- [ ] **1. Run all tests**
```bash
python -m pytest tests/ -v
```
Expected: all PASS

- [ ] **2. Run one complete cycle**
```bash
python src/scheduler.py --once
```
Expected: logs showing cards discovered, promos validated

- [ ] **3. Verify dashboard**
```bash
uvicorn src.api.main:app --port 8000
```
Open `http://localhost:8000` — promotions appear in dashboard

- [ ] **4. Verify Telegram alert arrived** (check your Telegram chat)

- [ ] **5. Test bot commands**
Send to your bot: `/status`, `/promos`, `/buscar`

- [ ] **6. Verify hooks work**
```bash
python hooks/pre-search.py && echo "Hook OK"
```

- [ ] **7. Final commit**
```bash
git add -A
git commit -m "chore: complete Card Watch BR v1.0 implementation"
git push origin main
```
