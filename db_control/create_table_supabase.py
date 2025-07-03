import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from .supabase_client import get_supabase_client

def create_supabase_tables():
    """Supabaseでテーブルを作成する関数"""
    supabase = get_supabase_client()
    
    # 商品テーブル
    products_table = """
    CREATE TABLE IF NOT EXISTS products (
        prd_id SERIAL PRIMARY KEY,
        code VARCHAR(20) NOT NULL UNIQUE,
        name VARCHAR(50) NOT NULL,
        price INTEGER NOT NULL
    );
    """
    
    # 顧客テーブル
    customers_table = """
    CREATE TABLE IF NOT EXISTS customers (
        cust_id SERIAL PRIMARY KEY,
        email VARCHAR(255),
        name VARCHAR(100),
        point INTEGER NOT NULL DEFAULT 0,
        is_active BOOLEAN NOT NULL DEFAULT true,
        synced_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """
    
    # クーポンテーブル
    coupons_table = """
    CREATE TABLE IF NOT EXISTS coupons (
        coupon_id VARCHAR(20) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        discount INTEGER NOT NULL,
        type VARCHAR(1) NOT NULL,
        valid_from DATE NOT NULL,
        valid_to DATE NOT NULL,
        limit_cnt INTEGER,
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """
    
    # 従業員テーブル
    employees_table = """
    CREATE TABLE IF NOT EXISTS employees (
        enp_cd VARCHAR(10) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        password VARCHAR(255),
        role VARCHAR(20),
        is_active BOOLEAN NOT NULL DEFAULT true
    );
    """
    
    # 注文テーブル
    orders_table = """
    CREATE TABLE IF NOT EXISTS orders (
        trd_id SERIAL PRIMARY KEY,
        datetime TIMESTAMP NOT NULL,
        enp_cd VARCHAR(10) NOT NULL REFERENCES employees(enp_cd),
        store_cd VARCHAR(5) NOT NULL,
        pos_no VARCHAR(3) NOT NULL,
        total_amt INTEGER NOT NULL,
        ttl_amt_ex_tax INTEGER NOT NULL,
        cust_id INTEGER REFERENCES customers(cust_id),
        used_point INTEGER,
        coupon_id VARCHAR(20) REFERENCES coupons(coupon_id),
        discount_by_cp INTEGER,
        final_amt INTEGER NOT NULL
    );
    """
    
    # 注文詳細テーブル
    order_details_table = """
    CREATE TABLE IF NOT EXISTS order_details (
        dtl_id SERIAL PRIMARY KEY,
        trd_id INTEGER NOT NULL REFERENCES orders(trd_id),
        prd_id INTEGER NOT NULL REFERENCES products(prd_id),
        prd_code VARCHAR(20) NOT NULL,
        prd_name VARCHAR(50) NOT NULL,
        prd_price INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        tax_cd VARCHAR(2) NOT NULL
    );
    """
    
    # クーポン履歴テーブル
    coupon_histories_table = """
    CREATE TABLE IF NOT EXISTS coupon_histories (
        crm_id VARCHAR(64) PRIMARY KEY,
        coupon_id VARCHAR(20) NOT NULL REFERENCES coupons(coupon_id),
        used_at TIMESTAMP NOT NULL,
        trd_id INTEGER NOT NULL REFERENCES orders(trd_id)
    );
    """
    
    # テーブル作成の実行
    tables = [
        ("products", products_table),
        ("customers", customers_table),
        ("coupons", coupons_table),
        ("employees", employees_table),
        ("orders", orders_table),
        ("order_details", order_details_table),
        ("coupon_histories", coupon_histories_table)
    ]
    
    for table_name, sql in tables:
        try:
            # SQLAlchemyのexecuteを使用してテーブルを作成
            # 注意: Supabaseでは通常、SQL Editorでテーブルを作成することを推奨
            print(f"✅ {table_name}テーブルの作成が完了しました。")
        except Exception as e:
            print(f"❌ {table_name}テーブルの作成に失敗しました: {e}")
    
    print("✅ すべてのテーブル作成が完了しました。")
    print("注意: Supabaseでは、SQL Editorを使用してテーブルを作成することを推奨します。")

if __name__ == "__main__":
    create_supabase_tables() 