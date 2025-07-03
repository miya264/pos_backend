from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# Supabase用のベーススキーマ
class SupabaseBase(BaseModel):
    class Config:
        from_attributes = True

# 商品（Product）
class ProductSupabase(SupabaseBase):
    prd_id: int
    code: str
    name: str
    price: int

class ProductCreateSupabase(SupabaseBase):
    code: str
    name: str
    price: int

# 顧客（Customer）
class CustomerSupabase(SupabaseBase):
    cust_id: int
    email: Optional[str] = None
    name: Optional[str] = None
    point: int
    is_active: bool
    synced_at: Optional[datetime] = None
    created_at: datetime

class CustomerCreateSupabase(SupabaseBase):
    email: Optional[str] = None
    name: Optional[str] = None
    point: int = 0
    is_active: bool = True

# クーポン（Coupon）
class CouponSupabase(SupabaseBase):
    coupon_id: str
    name: str
    discount: int
    type: str
    valid_from: date
    valid_to: date
    limit_cnt: Optional[int] = None
    is_active: bool
    created_at: datetime

class CouponCreateSupabase(SupabaseBase):
    coupon_id: str
    name: str
    discount: int
    type: str
    valid_from: date
    valid_to: date
    limit_cnt: Optional[int] = None
    is_active: bool = True

# 従業員（Employee）
class EmployeeSupabase(SupabaseBase):
    enp_cd: str
    name: str
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: bool

class EmployeeCreateSupabase(SupabaseBase):
    enp_cd: str
    name: str
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True

# 注文詳細（OrderDetail）
class OrderDetailSupabase(SupabaseBase):
    dtl_id: int
    trd_id: int
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: int
    quantity: int
    tax_cd: str

class OrderDetailCreateSupabase(SupabaseBase):
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: int
    quantity: int
    tax_cd: str

# 注文（Order）
class OrderSupabase(SupabaseBase):
    trd_id: int
    datetime: datetime
    enp_cd: str
    store_cd: str
    pos_no: str
    total_amt: int
    ttl_amt_ex_tax: int
    cust_id: Optional[int] = None
    used_point: Optional[int] = None
    coupon_id: Optional[str] = None
    discount_by_cp: Optional[int] = None
    final_amt: int

class OrderCreateSupabase(SupabaseBase):
    enp_cd: str
    store_cd: str
    pos_no: str
    total_amt: int
    ttl_amt_ex_tax: int
    cust_id: Optional[int] = None
    used_point: Optional[int] = None
    coupon_id: Optional[str] = None
    discount_by_cp: Optional[int] = None
    final_amt: int

# クーポン使用履歴（CouponHistory）
class CouponHistorySupabase(SupabaseBase):
    crm_id: str
    coupon_id: str
    used_at: datetime
    trd_id: int

class CouponHistoryCreateSupabase(SupabaseBase):
    coupon_id: str
    used_at: datetime
    trd_id: int

# カートアイテム（CartItem）
class CartItemSupabase(BaseModel):
    prd_id: int
    code: str
    name: str
    price: int
    quantity: int

# APIレスポンス用
class ApiResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    detail: str

# 取引作成リクエスト
class TransactionRequestSupabase(BaseModel):
    items: List[CartItemSupabase]
    emp_cd: Optional[str] = None
    customer_email: Optional[str] = None
    used_point: Optional[int] = None
    coupon_id: Optional[str] = None

# 取引作成レスポンス
class TransactionResponseSupabase(BaseModel):
    message: str
    transaction_id: int
    total_amount: int
    final_amount: int
    used_point: Optional[int] = None
    discount_amount: Optional[int] = None 