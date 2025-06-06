from fastapi import FastAPI, Depends, HTTPException, Header, Body
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

@app.get("/employees/{emp_cd}", response_model=schemas.Employee)
def get_employee(emp_cd: str, db: Session = Depends(get_db)):
    """
    従業員コードで従業員を検索するAPI
    - **emp_cd**: 検索する従業員コード
    """
    employee = db.query(models.Employee).filter(models.Employee.enp_cd == emp_cd).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="従業員が見つかりません")
    return employee

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
    items: List[schemas.CartItem] = Body(...),  # Bodyパラメータとして直接リストを受け取る
    db: Session = Depends(get_db),
    emp_cd: Optional[str] = Header(default=None)
):
    """
    取引を登録するAPI
    ・emp_cd がリクエストヘッダーにあればそのコードを使用
    ・なければ GUEST00001 を使用
    """

    try:
        # 店員コードを決定
        employee_code = emp_cd if emp_cd else GUEST_CODE

        # 安全確認：DBに存在する店員コードかチェック
        employee = db.query(models.Employee).filter(models.Employee.enp_cd == employee_code).first()
        if not employee:
            raise HTTPException(status_code=400, detail=f"店員コード '{employee_code}' は存在しません")

        # 合計金額の算出（税抜き）
        total_amount = sum(item.price * item.quantity for item in items)
        # 税込み合計金額の算出（10%固定）
        total_amount_with_tax = int(total_amount * 1.1)

        # 注文（Order）の作成
        order = models.Order(
            datetime=datetime.now(),
            enp_cd=employee_code,
            store_cd="A001",  # 仮の店舗コード
            pos_no="P01",     # POSナンバー（3文字以内）
            total_amt=total_amount_with_tax,  # 税込み合計
            ttl_amt_ex_tax=total_amount,      # 税抜き合計
            final_amt=total_amount_with_tax   # 最終金額（割引なしの場合は税込み合計と同じ）
        )

        db.add(order)
        db.flush()  # order.trd_idを取得するためにflush

        # 注文明細（OrderDetail）の作成
        for idx, item in enumerate(items, 1):
            detail = models.OrderDetail(
                trd_id=order.trd_id,
                prd_id=item.prd_id,
                prd_code=item.code,
                prd_name=item.name,
                prd_price=item.price,
                quantity=item.quantity,
                tax_cd="10"    # 税区分コード：10%
            )
            db.add(detail)

        db.commit()
        return {
            "message": "取引が登録されました",
            "transaction_id": order.trd_id,
            "total_amount": total_amount_with_tax
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))