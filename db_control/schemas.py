from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

# 共通ベース（ORM対応）
class ORMBase(BaseModel):
    class Config:
        orm_mode = True

# 商品（Product）
class ProductBase(ORMBase):
    code: str
    name: str
    price: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    prd_id: int

# 顧客（Customer）
class CustomerBase(ORMBase):
    email: Optional[str]
    name: Optional[str]
    point: int
    is_active: bool

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    cust_id: int
    synced_at: Optional[datetime]
    created_at: datetime

# クーポン（Coupon）
class CouponBase(ORMBase):
    name: str
    discount: int
    type: str
    valid_from: date
    valid_to: date
    limit_cnt: Optional[int]
    is_active: bool

class CouponCreate(CouponBase):
    coupon_id: str

class Coupon(CouponBase):
    coupon_id: str
    created_at: datetime

# 従業員（Employee）
class EmployeeBase(ORMBase):
    name: str
    password: Optional[str]
    role: str
    is_active: bool

class EmployeeCreate(EmployeeBase):
    enp_cd: str

class Employee(EmployeeBase):
    enp_cd: str

# 注文詳細（OrderDetail）
class OrderDetailBase(ORMBase):
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: int
    quantity: int
    tax_cd: str

class OrderDetailCreate(OrderDetailBase):
    trd_id: int

class OrderDetail(OrderDetailBase):
    dtl_id: int
    trd_id: int

# 注文（Order）
class OrderBase(ORMBase):
    ordered_at: datetime
    enp_cd: str
    store_cd: str
    pos_no: str
    total_amt: int
    ttl_amt_ex_tax: int
    cust_id: Optional[int]
    used_point: Optional[int]
    coupon_id: Optional[str]
    discount_by_cp: Optional[int]
    final_amt: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    trd_id: int
    order_details: List[OrderDetail] = []

# クーポン使用履歴（CouponHistory）
class CouponHistoryBase(ORMBase):
    coupon_id: str
    used_at: datetime
    trd_id: int

class CouponHistoryCreate(CouponHistoryBase):
    crm_id: str

class CouponHistory(CouponHistoryBase):
    crm_id: str

# カートアイテム（CartItem）
class CartItem(BaseModel):
    prd_id: int
    code: str
    name: str
    price: float
    quantity: int