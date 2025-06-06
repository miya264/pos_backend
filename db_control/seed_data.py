from sqlalchemy.orm import Session
from .connect import SessionLocal
from .mymodels import Product, Employee


def seed_products(db: Session):
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
        existing = db.query(Product).filter(Product.code == prod["code"]).first()
        if not existing:
            db_product = Product(**prod)
            db.add(db_product)
            print(f"✓ 追加: {prod['code']} - {prod['name']}")
        else:
            print(f"スキップ: {prod['code']}（既に存在）")

def seed_employees(db: Session):
    employees = [
        {"enp_cd": "GUEST00001", "name": "ゲストユーザー", "password": None, "role": "guest", "is_active": True},
        {"enp_cd": "EMP00001", "name": "田中", "password": "password1", "role": "staff", "is_active": True},
        {"enp_cd": "EMP00002", "name": "鈴木", "password": "password2", "role": "staff", "is_active": True},
    ]

    for emp in employees:
        existing = db.query(Employee).filter(Employee.enp_cd == emp["enp_cd"]).first()
        if not existing:
            db_employee = Employee(**emp)
            db.add(db_employee)
            print(f"✓ 追加: {emp['name']}（{emp['enp_cd']}）")
        else:
            print(f"スキップ: {emp['enp_cd']}（既に存在）")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_employees(db)
        seed_products(db)
        db.commit()
        print("✅ 初期データ登録が完了しました。")
    except Exception as e:
        db.rollback()
        print(f"❌ エラー発生: {e}")
    finally:
        db.close()
