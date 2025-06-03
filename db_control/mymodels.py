from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, UniqueConstraint, LargeBinary, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connect import Base


class Product(Base):
    __tablename__ = 'products'

    prd_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False)
    name = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)

    order_details = relationship('OrderDetail', back_populates='product')


class Customer(Base):
    __tablename__ = 'customers'

    cust_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=True)
    name = Column(String(100), nullable=True)
    point = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False)
    synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    orders = relationship('Order', back_populates='customer')


class Coupon(Base):
    __tablename__ = 'coupons'

    coupon_id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    discount = Column(Integer, nullable=False)
    type = Column(String(1), nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)
    limit_cnt = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    coupon_histories = relationship('CouponHistory', back_populates='coupon')
    orders = relationship('Order', back_populates='coupon')  # ✅ 追加


class Employee(Base):
    __tablename__ = 'employees'

    enp_cd = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=True)
    role = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False)

    orders = relationship('Order', back_populates='employee')


class Order(Base):
    __tablename__ = 'orders'

    trd_id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, nullable=False)
    enp_cd = Column(String(10), ForeignKey("employees.enp_cd"), nullable=False)
    store_cd = Column(String(5), nullable=False)
    pos_no = Column(String(3), nullable=False)
    total_amt = Column(Integer, nullable=False)
    ttl_amt_ex_tax = Column(Integer, nullable=False)
    cust_id = Column(Integer, ForeignKey('customers.cust_id'), nullable=True)
    used_point = Column(Integer, nullable=True)
    coupon_id = Column(String(20), ForeignKey('coupons.coupon_id'), nullable=True)
    discount_by_cp = Column(Integer, nullable=True)
    final_amt = Column(Integer, nullable=False)

    customer = relationship('Customer', back_populates='orders')
    coupon = relationship('Coupon', back_populates='orders')  # ✅ 修正
    order_details = relationship('OrderDetail', back_populates='order')
    employee = relationship("Employee", back_populates="orders")
    coupon_histories = relationship('CouponHistory', back_populates='order')  # ✅ 追加


class OrderDetail(Base):
    __tablename__ = 'order_details'

    dtl_id = Column(Integer, primary_key=True, autoincrement=True)
    trd_id = Column(Integer, ForeignKey('orders.trd_id'), nullable=False)
    prd_id = Column(Integer, ForeignKey('products.prd_id'), nullable=False)
    prd_code = Column(String(20), nullable=False)
    prd_name = Column(String(50), nullable=False)
    prd_price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    tax_cd = Column(String(2), nullable=False)

    order = relationship('Order', back_populates='order_details')
    product = relationship('Product', back_populates='order_details')


class CouponHistory(Base):
    __tablename__ = 'coupon_histories'

    crm_id = Column(String(64), primary_key=True)
    coupon_id = Column(String(20), ForeignKey('coupons.coupon_id'), nullable=False)
    used_at = Column(DateTime, nullable=False)
    trd_id = Column(Integer, ForeignKey('orders.trd_id'), nullable=False)

    coupon = relationship('Coupon', back_populates='coupon_histories')
    order = relationship('Order', back_populates='coupon_histories')
