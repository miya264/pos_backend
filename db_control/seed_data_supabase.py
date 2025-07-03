from db_control.supabase_client import get_supabase_client

def seed_products_supabase():
    """商品データをSupabaseに登録"""
    supabase = get_supabase_client()
    
    products = [
        # 多機能ペン
        {"code": "4901991060522", "name": "多機能ペン モノグラフマルチ モノカラー", "price": 660},
        {"code": "4901991060539", "name": "多機能ペン モノグラフマルチ ゴールド", "price": 660},
        {"code": "4901991060546", "name": "多機能ペン モノグラフマルチ ブラック", "price": 660},
        {"code": "4901991060553", "name": "多機能ペン モノグラフマルチ ブルー", "price": 660},

        # 油性ボールペン
        {"code": "4901991059748", "name": "ボールペン ズーム L105 シルバー", "price": 1980},
        {"code": "4901991059755", "name": "ボールペン ズーム L105 シャンパンゴールド", "price": 1980},

        # シャープペン（モノグラフ 0.3mm）
        {"code": "4901991062939", "name": "シャープ モノグラフ 0.3mm クリア", "price": 440},
        {"code": "4901991062946", "name": "シャープ モノグラフ 0.3mm クリアミント", "price": 440},
        {"code": "4901991062953", "name": "シャープ モノグラフ 0.3mm クリアパープル", "price": 440},

        # シャープペン（モノグラフライト 0.5mm）
        {"code": "4901991062663", "name": "シャープ モノグラフライト 0.5mm モノカラー", "price": 242},
        {"code": "4901991062670", "name": "シャープ モノグラフライト 0.5mm フルブラック", "price": 242},
        {"code": "4901991062687", "name": "シャープ モノグラフライト 0.5mm グレイッシュブルー", "price": 242},
    ]

    for prod in products:
        # 既存チェック
        existing = supabase.table('products').select('prd_id').eq('code', prod["code"]).execute()
        if not existing.data:
            # 新規追加
            response = supabase.table('products').insert(prod).execute()
            print(f"✓ 追加: {prod['code']} - {prod['name']}")
        else:
            print(f"スキップ: {prod['code']}（既に存在）")

def seed_employees_supabase():
    """従業員データをSupabaseに登録"""
    supabase = get_supabase_client()
    
    employees = [
        {"enp_cd": "GUEST00001", "name": "ゲストユーザー", "password": None, "role": "guest", "is_active": True},
        {"enp_cd": "EMP00001", "name": "田中", "password": "password1", "role": "staff", "is_active": True},
        {"enp_cd": "EMP00002", "name": "鈴木", "password": "password2", "role": "staff", "is_active": True},
    ]

    for emp in employees:
        # 既存チェック
        existing = supabase.table('employees').select('enp_cd').eq('enp_cd', emp["enp_cd"]).execute()
        if not existing.data:
            # 新規追加
            response = supabase.table('employees').insert(emp).execute()
            print(f"✓ 追加: {emp['name']}（{emp['enp_cd']}）")
        else:
            print(f"スキップ: {emp['enp_cd']}（既に存在）")

def seed_coupons_supabase():
    """クーポンデータをSupabaseに登録"""
    supabase = get_supabase_client()
    
    from datetime import date, timedelta
    
    coupons = [
        {
            "coupon_id": "WELCOME2024",
            "name": "新規顧客限定クーポン",
            "discount": 500,
            "type": "F",  # Fixed amount
            "valid_from": date.today().isoformat(),
            "valid_to": (date.today() + timedelta(days=30)).isoformat(),
            "limit_cnt": 100,
            "is_active": True
        },
        {
            "coupon_id": "SUMMER2024",
            "name": "夏の特別クーポン",
            "discount": 10,
            "type": "P",  # Percentage
            "valid_from": date.today().isoformat(),
            "valid_to": (date.today() + timedelta(days=90)).isoformat(),
            "limit_cnt": 50,
            "is_active": True
        }
    ]

    for coupon in coupons:
        # 既存チェック
        existing = supabase.table('coupons').select('coupon_id').eq('coupon_id', coupon["coupon_id"]).execute()
        if not existing.data:
            # 新規追加
            response = supabase.table('coupons').insert(coupon).execute()
            print(f"✓ 追加: {coupon['coupon_id']} - {coupon['name']}")
        else:
            print(f"スキップ: {coupon['coupon_id']}（既に存在）")

if __name__ == "__main__":
    try:
        seed_employees_supabase()
        seed_products_supabase()
        seed_coupons_supabase()
        print("✅ 初期データ登録が完了しました。")
    except Exception as e:
        print(f"❌ エラー発生: {e}") 