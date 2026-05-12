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
