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
            cycle.cards_found,
            cycle.promos_validated,
            len(result["alerts_sent"]),
        )
    except Exception:
        logger.exception("Erro durante o ciclo")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Card Watch BR Scheduler")
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
