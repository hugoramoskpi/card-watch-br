# Card Watch BR

Monitor automático de promoções de cartões black/premium.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env  # preencha as chaves
```

## Uso

```bash
# Executar um ciclo de busca
python src/scheduler.py --once

# Iniciar dashboard web
uvicorn src.api.main:app --port 8000 --reload

# Iniciar scheduler contínuo
python src/scheduler.py
```
