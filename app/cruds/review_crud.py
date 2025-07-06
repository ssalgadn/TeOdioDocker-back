from sqlalchemy.orm import Session
from app.models.models import Reviews
from typing import Optional

def create_review(db: Session, user: str, store_id: int, rating: int) -> Reviews:
    db_review = Reviews(
        user=user,
        store_id=store_id,
        rating=rating
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_all_reviews_by_store_id(db: Session, store_id: int) -> list[Reviews]:
    return db.query(Reviews).filter(Reviews.store_id == store_id).all()

def get_one_review(db: Session, store_id: int, user: str) -> Optional[Reviews]:
    return db.query(Reviews).filter(Reviews.store_id == store_id and Reviews.user == user).first()