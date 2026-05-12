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

### 4. Run cycle with verbose logging
```bash
python -c "
import logging; logging.basicConfig(level=logging.DEBUG)
from dotenv import load_dotenv; load_dotenv()
from src.scheduler import run_cycle; run_cycle()
"
```
