import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.db.repository import upsert_promotion
from src.api.main import app
from src.db.database import get_db

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Use a single connection so in-memory DB is shared across sessions
    connection = engine.connect()
    Base.metadata.create_all(connection)
    TestSession = sessionmaker(bind=connection)

    def override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        db = TestSession()
        upsert_promotion(db, "Inter Black", "Anuidade zero", ["Reddit"], 2, ["https://url.com"])
        db.close()
        yield c
    app.dependency_overrides.clear()
    connection.close()

def test_get_dashboard_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200

def test_get_promotions_returns_list(client):
    response = client.get("/api/promotions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["card_name"] == "Inter Black"

def test_dismiss_promotion(client):
    promos = client.get("/api/promotions").json()
    promo_id = promos[0]["id"]
    response = client.post(f"/api/promotions/{promo_id}/dismiss")
    assert response.status_code == 200
    assert client.get("/api/promotions").json() == []
