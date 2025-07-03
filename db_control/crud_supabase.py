from db_control.supabase_client import get_supabase_client
from db_control.schemas import TransactionCreate, TransactionDetailCreate
from datetime import datetime
from typing import List, Optional, Dict, Any

def get_product_by_code(code: str) -> Optional[Dict[str, Any]]:
    """商品コードで商品を取得（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('products').select('*').eq('code', code).execute()
    return response.data[0] if response.data else None

def check_product_exists(code: str) -> bool:
    """商品の存在確認（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('products').select('prd_id').eq('code', code).execute()
    return len(response.data) > 0

def create_transaction_with_details(
    transaction_data: TransactionCreate,
    transaction_details_data: List[TransactionDetailCreate]
) -> Dict[str, Any]:
    """取引と取引詳細を作成（Supabase版）"""
    supabase = get_supabase_client()
    
    # 取引データの作成
    transaction_dict = transaction_data.dict()
    transaction_dict['datetime'] = datetime.now().isoformat()
    
    # 取引を挿入
    transaction_response = supabase.table('transactions').insert(transaction_dict).execute()
    transaction = transaction_response.data[0]
    
    # 取引詳細を作成
    details_to_insert = []
    for detail in transaction_details_data:
        detail_dict = detail.dict()
        detail_dict['ted_id'] = transaction['ted_id']
        details_to_insert.append(detail_dict)
    
    # 取引詳細を一括挿入
    if details_to_insert:
        supabase.table('transaction_details').insert(details_to_insert).execute()
    
    return transaction

def get_all_products() -> List[Dict[str, Any]]:
    """全商品を取得（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('products').select('*').execute()
    return response.data

def get_employee_by_code(emp_code: str) -> Optional[Dict[str, Any]]:
    """従業員コードで従業員を取得（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('employees').select('*').eq('enp_cd', emp_code).execute()
    return response.data[0] if response.data else None

def create_customer(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """顧客を作成（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('customers').insert(customer_data).execute()
    return response.data[0]

def get_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
    """メールアドレスで顧客を取得（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('customers').select('*').eq('email', email).execute()
    return response.data[0] if response.data else None

def update_customer_points(cust_id: int, new_points: int) -> Dict[str, Any]:
    """顧客のポイントを更新（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('customers').update({'point': new_points}).eq('cust_id', cust_id).execute()
    return response.data[0]

def get_coupon_by_id(coupon_id: str) -> Optional[Dict[str, Any]]:
    """クーポンIDでクーポンを取得（Supabase版）"""
    supabase = get_supabase_client()
    response = supabase.table('coupons').select('*').eq('coupon_id', coupon_id).execute()
    return response.data[0] if response.data else None

def create_order_with_details(order_data: Dict[str, Any], order_details_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """注文と注文詳細を作成（Supabase版）"""
    supabase = get_supabase_client()
    
    # 注文データの作成
    order_data['datetime'] = datetime.now().isoformat()
    
    # 注文を挿入
    order_response = supabase.table('orders').insert(order_data).execute()
    order = order_response.data[0]
    
    # 注文詳細を作成
    details_to_insert = []
    for detail in order_details_data:
        detail['trd_id'] = order['trd_id']
        details_to_insert.append(detail)
    
    # 注文詳細を一括挿入
    if details_to_insert:
        supabase.table('order_details').insert(details_to_insert).execute()
    
    return order 