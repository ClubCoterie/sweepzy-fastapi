from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from .database import Base

class Event(Base):
    __tablename__ = "all_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    betfair_id = Column(Integer)
    leaderboard_id = Column(Integer)
    name = Column(String)
    sport = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

class Sweepzy(Base):
    __tablename__ = "all_sweepzys"

    sweepzy_id = Column(Integer, primary_key=True)
    sweepzy_name = Column(String)
    event_id = Column(Integer)
    fair_odds = Column(Boolean)
    even_draw = Column(Boolean)

class Prizes(Base):
    __tablename__ = "prizes"

    prize_id = Column(Integer, primary_key=True, autoincrement=True)
    prize_type = Column(String)
    event_id = Column(Integer)

