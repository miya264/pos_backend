from connect import engine
from mymodels import Base

# テーブルを削除
Base.metadata.drop_all(bind=engine)

# テーブルを作成
Base.metadata.create_all(bind=engine)

print("✅ テーブル作成が完了しました。")
