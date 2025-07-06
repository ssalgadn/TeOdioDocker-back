from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schema.product_schemas import (
    ReviewCreate,
    ReviewResponse,
)
from app.cruds.review_crud import (
    get_one_review,
    create_review,
    get_all_reviews_by_store_id
)

from app.models.models import Reviews

from app.database import get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("/{store_id}", response_model=list[ReviewResponse])
async def get_reviews(
    store_id: int,
    db: Session = Depends(get_db)
):
    reviews = get_all_reviews_by_store_id(db=db, store_id=store_id)
    return [ReviewResponse.model_validate(review) for review in reviews]

@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review_endpoint(
    review: ReviewCreate,
    db: Session = Depends(get_db)
):
    review_of_db = get_one_review(
        db=db,
        store_id=review.store_id,
        user=review.user
    )
    if not review_of_db:
        review_create = create_review(
            db=db,
            user=review.user,
            store_id=review.store_id,
            rating = review.rating
        )
    else:
        return review_of_db
    return ReviewResponse.model_validate(review_create)