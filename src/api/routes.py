from pathlib import Path
from threading import Thread
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.repository import get_promotions, dismiss_promotion

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

@router.post("/api/cycles/trigger")
def trigger_cycle():
    from src.scheduler import run_cycle
    Thread(target=run_cycle, daemon=True).start()
    return {"status": "started"}
