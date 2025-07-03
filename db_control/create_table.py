from .connect import engine
from .mymodels import Base

# テーブルを作成
Base.metadata.create_all(bind=engine)

print("✅ テーブル作成が完了しました。")
