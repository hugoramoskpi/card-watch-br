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

def test_get_dismissed_promotions(db):
    upsert_promotion(db, "BRB DUX", "7 pontos por dólar", ["Reddit", "Hardmob"], 2, ["https://url.com"])
    promos = get_promotions(db)
    dismiss_promotion(db, promos[0].id)
    dismissed = get_promotions(db, dismissed=True)
    assert len(dismissed) == 1
    assert dismissed[0].card_name == "BRB DUX"
