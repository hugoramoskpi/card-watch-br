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
    print(f"Hook pre-search: variáveis ausentes no .env: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

print("Hook pre-search: todas as variáveis de ambiente verificadas.")
