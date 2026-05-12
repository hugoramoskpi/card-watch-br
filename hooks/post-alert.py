#!/usr/bin/env python3
"""Post-alert hook: logs cycle completion to logs/alerts.log."""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

log_path = Path("logs/alerts.log")
log_path.parent.mkdir(exist_ok=True)

timestamp = datetime.now(timezone.utc).isoformat()
entry = f"[{timestamp}] Agent cycle completed\n"
with log_path.open("a", encoding="utf-8") as f:
    f.write(entry)
print(f"Hook post-alert: logged to {log_path}")
