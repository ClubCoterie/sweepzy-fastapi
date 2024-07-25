from typing import Optional
from datetime import date
from pydantic import BaseModel

class EventSchema(BaseModel):
    id: int
    betfair_id: int
    leaderboard_id: Optional[int] = None
    name: str
    sport: str
    start_date: date
    end_date: date

    class Config:
        orm_mode = True

class SweepzySchema(BaseModel):
    sweepzy_id: int
    sweepzy_name: str
    event_id: int
    fair_odds: bool
    even_draw: bool

    class Config:
        orm_mode = True

class PrizeSchema(BaseModel):
    # prize_id: int
    prize_type: str
    # event_id: int

    class Config:
        orm_mode = True