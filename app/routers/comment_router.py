from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schema.comment_schemas import (
    CommentCreate,
    CommentResponse,
    CommentBase
)
from app.cruds.comment_crud import (
    create_comment,
    get_all_comments_by_product_id
)
from app.cruds.product_crud import (
    get_product_by_id
)
from app.models.models import Comments, Products

from app.database import get_db

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/{product_id}", response_model=list[CommentResponse])
async def get_comments(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    comments = get_all_comments_by_product_id(db=db, product_id=product_id)

    return [CommentResponse.model_validate(comment) for comment in comments]

@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment_endpoint(
    comment: CommentCreate,
    db: Session = Depends(get_db)
):
    product = get_product_by_id(db=db, product_id=comment.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_comment = create_comment(
        db=db,
        user=comment.user,
        product_id=comment.product_id,
        text=comment.text
    )
    
    return CommentResponse.model_validate(db_comment)