from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import math
from pytz import timezone
import uuid
from db_control.crud_supabase import (
    get_product_by_code,
    get_employee_by_code,
    create_order_with_details,
    get_all_products,
    create_customer,
    get_customer_by_email,
    update_customer_points,
    get_coupon_by_id
)
from db_control.schemas import CartItem

app = FastAPI()

# CORSミドルウェアを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GUEST_CODE = "GUEST00001"  # ゲストコード

@app.get("/")
def read_root():
    return {"message": "POS System API (Supabase)"}

@app.get("/employees/{emp_cd}")
def get_employee(emp_cd: str):
    """
    従業員コードで従業員を検索するAPI（Supabase版）
    - **emp_cd**: 検索する従業員コード
    """
    employee = get_employee_by_code(emp_cd)
    if employee is None:
        raise HTTPException(status_code=404, detail="従業員が見つかりません")
    return employee

@app.get("/products/code/{code}")
def search_product(code: str):
    """
    商品コードで商品を検索するAPI（Supabase版）
    - **code**: 検索する商品コード（13桁）
    """
    product = get_product_by_code(code)
    if product is None:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    return product

@app.get("/products/")
def get_products():
    """
    全商品を取得するAPI（Supabase版）
    """
    products = get_all_products()
    return {"products": products}

@app.post("/transactions/", status_code=201)
def create_transaction(
    items: List[CartItem] = Body(...),
    emp_cd: Optional[str] = Header(default=None)
):
    """
    取引を登録するAPI（Supabase版）
    ・emp_cd がリクエストヘッダーにあればそのコードを使用
    ・なければ GUEST00001 を使用
    """

    try:
        # 合計金額の計算
        total_amount = sum(item.price * item.quantity for item in items)
        total_amount_with_tax = math.floor(total_amount * 1.1)  # 税率10%

        # 日本時間のタイムスタンプを取得
        jst = timezone('Asia/Tokyo')
        current_time = datetime.now(jst)

        # 注文データの作成
        order_data = {
            "datetime": current_time.isoformat(),
            "enp_cd": emp_cd or "GUEST00001",
            "store_cd": "A001",
            "pos_no": "P01",
            "total_amt": total_amount_with_tax,
            "ttl_amt_ex_tax": total_amount,
            "final_amt": total_amount_with_tax
        }

        # 注文詳細データの作成
        order_details_data = []
        for item in items:
            detail_data = {
                "prd_id": item.prd_id,
                "prd_code": item.code,
                "prd_name": item.name,
                "prd_price": item.price,
                "quantity": item.quantity,
                "tax_cd": "10"    # 税区分コード：10%
            }
            order_details_data.append(detail_data)

        # 注文と注文詳細を作成
        order = create_order_with_details(order_data, order_details_data)

        return {
            "message": "取引が登録されました",
            "transaction_id": order["trd_id"],
            "total_amount": total_amount_with_tax
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/customers/", status_code=201)
def create_customer_endpoint(customer_data: dict):
    """
    顧客を作成するAPI（Supabase版）
    """
    try:
        customer = create_customer(customer_data)
        return {"message": "顧客が作成されました", "customer": customer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers/email/{email}")
def get_customer_by_email_endpoint(email: str):
    """
    メールアドレスで顧客を検索するAPI（Supabase版）
    """
    customer = get_customer_by_email(email)
    if customer is None:
        raise HTTPException(status_code=404, detail="顧客が見つかりません")
    return customer

@app.put("/customers/{cust_id}/points")
def update_customer_points_endpoint(cust_id: int, points: int):
    """
    顧客のポイントを更新するAPI（Supabase版）
    """
    try:
        customer = update_customer_points(cust_id, points)
        return {"message": "ポイントが更新されました", "customer": customer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/coupons/{coupon_id}")
def get_coupon_endpoint(coupon_id: str):
    """
    クーポンIDでクーポンを検索するAPI（Supabase版）
    """
    coupon = get_coupon_by_id(coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="クーポンが見つかりません")
    return coupon

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 