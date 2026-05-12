from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(String, primary_key=True)
    card_name = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    sources = Column(JSON, nullable=False)
    confidence = Column(Integer, nullable=False)
    raw_urls = Column(JSON, nullable=False)
    found_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dismissed = Column(Boolean, default=False)
    alerted = Column(Boolean, default=False)

class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(String, primary_key=True)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    cards_found = Column(Integer, default=0)
    promos_found = Column(Integer, default=0)
    promos_validated = Column(Integer, default=0)
