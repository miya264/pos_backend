from sqlalchemy.orm import Session
from db_control.mymodels import Product, Transaction, TransactionDetail
from db_control.schemas import TransactionCreate, TransactionDetailCreate
from datetime import datetime
from typing import List, Optional

def get_product_by_code(db: Session, code: str) -> Optional[Product]:
    return db.query(Product).filter(Product.code == code).first()

def check_product_exists(db: Session, code: str) -> bool:
    return db.query(Product).filter(Product.code == code).first() is not None

def create_transaction_with_details(
    db: Session,
    transaction_data: TransactionCreate,
    transaction_details_data: List[TransactionDetailCreate]
) -> Transaction:
    db_transaction = Transaction(**transaction_data.dict(), datetime=datetime.now())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    for detail in transaction_details_data:
        db_detail = TransactionDetail(
            ted_id=db_transaction.ted_id,
            prd_id=detail.prd_id,
            prd_code=detail.prd_code,
            prd_name=detail.prd_name,
            prd_price=detail.prd_price,
            quantity=detail.quantity,
            tax_cd=detail.tax_cd
        )
        db.add(db_detail)

    db.commit()
    return db_transaction
