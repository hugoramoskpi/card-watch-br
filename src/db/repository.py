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
