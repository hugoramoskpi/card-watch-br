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
   Open `http://localhost:8000` (start dashboard first if needed: `uvicorn src.api.main:app --port 8000`)

## Expected Output

```
=== Iniciando ciclo de busca ===
Ciclo concluído: X cartões, Y promos validadas, Z alertas enviados
```

If output shows 0 promos, use the `debug-search` skill.
