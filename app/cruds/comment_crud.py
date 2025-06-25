from sqlalchemy.orm import Session
from app.models.models import Comments, Products

def create_comment(db: Session, user: str, product_id: int, text: str) -> Comments:
    db_comment = Comments(
        user=user,
        product_id=product_id,
        text=text
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_all_comments_by_product_id(db: Session, product_id: int) -> list[Comments]:
    return db.query(Comments).filter(Comments.product_id == product_id).all()