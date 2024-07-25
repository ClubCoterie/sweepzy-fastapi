from sqlalchemy.orm import Session
from . import models, schemas


def get_events(db: Session):
    return db.query(models.Event).all()

def get_event_prizes(db: Session, event_id: int):
    return db.query(models.Prizes.prize_type).filter(models.Prizes.event_id == event_id).all()
