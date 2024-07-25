from fastapi import Depends, FastAPI, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..more_app.golf_tournament import GolfTourney
import cachetools
from .database import SessionLocal, engine
from .models import Base
from .crud import get_events, get_event_prizes
from .schemas import EventSchema, PrizeSchema, SweepzySchema

#Initialise Caches here
golf_leaderboard_cache = cachetools.TTLCache(maxsize=20, ttl=20000)
golf_stats_cache = cachetools.TTLCache(maxsize=20, ttl=20000)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/get-all-events/", response_model=List[EventSchema])
def get_all_events(db: Session = Depends(get_db)):
    events = get_events(db)
    return events

@app.get("/get-event-prize-options/{event_id}", response_model=List[PrizeSchema])
def get_event_prize_options(event_id: int, db: Session = Depends(get_db)):
    event_prizes = get_event_prizes(db, event_id)
    return event_prizes

@app.get("/get-golf-leaderboard/{tourney_id}")
def get_golf_leaderboard(tourney_id: int):

    if tourney_id in golf_leaderboard_cache:
        return golf_leaderboard_cache[tourney_id]

    leaderboard = GolfTourney(tourney_id).get_leaderboard()
    leaderboard_data = leaderboard.to_dict(orient="records")
    golf_leaderboard_cache[tourney_id] = leaderboard_data

    return leaderboard_data


@app.get("/get-golf-stats/{tourney_id}")
def get_golf_stats(tourney_id: int):
    if tourney_id in golf_stats_cache:
        return golf_stats_cache[tourney_id]

    stats = GolfTourney(tourney_id).get_tournament_stats()
    stats_data = stats.to_dict(orient="records")
    golf_stats_cache[tourney_id] = stats_data

    return stats_data









