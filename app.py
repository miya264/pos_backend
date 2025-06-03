from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import db_control.mymodels as models
import db_control.schemas as schemas
from db_control.connect import engine, get_db
from typing import Optional, List
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORSミドルウェアを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GUEST_CODE = "GUEST00001"  # ゲストコード

@app.get("/")
def read_root():
    return {"message": "POS System API"}

@app.get("/products/code/{code}", response_model=schemas.Product)
def search_product(code: str, db: Session = Depends(get_db)):
    """
    商品コードで商品を検索するAPI
    - **code**: 検索する商品コード（13桁）
    """
    product = db.query(models.Product).filter(models.Product.code == code).first()
    if product is None:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    return product



@app.post("/transactions/", status_code=201)
def create_transaction(
    items: List[schemas.CartItem],
    db: Session = Depends(get_db),
    emp_cd: Optional[str] = Header(default=None)
):
    """
    取引を登録するAPI
    ・emp_cd がリクエストヘッダーにあればそのコードを使用
    ・なければ GUEST00001 を使用
    """

    # 店員コードを決定
    employee_code = emp_cd if emp_cd else GUEST_CODE

    # 安全確認：DBに存在する店員コードかチェック（オプション）
    employee = db.query(models.Employee).filter(models.Employee.enp_cd == employee_code).first()
    if not employee:
        raise HTTPException(status_code=400, detail=f"店員コード '{employee_code}' は存在しません")

    # 合計金額の算出
    total_amount = sum(item.price * item.quantity for item in items)

    # 取引の作成
    transaction = models.Transaction(
        datetime=datetime.now(),
        emp_cd=employee_code,
        store_cd="ST001",
        pos_no="001",
        total_amt=total_amount
    )

    db.add(transaction)
    db.flush()

    # 取引明細の作成
    for idx, item in enumerate(items, 1):
        detail = models.TransactionDetail(
            ted_id=transaction.ted_id,
            dtl_id=idx,
            prd_id=item.prd_id,
            prd_code=item.code,
            prd_name=item.name,
            prd_price=item.price
        )
        db.add(detail)

    try:
        db.commit()
        return {"message": "取引が登録されました", "transaction_id": transaction.ted_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))