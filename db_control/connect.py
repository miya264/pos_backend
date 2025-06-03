from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
import os
from pathlib import Path
from dotenv import load_dotenv

# .env の読み込み
base_path = Path(__file__).resolve().parent.parent
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# DB接続情報の読み込み
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME')

# SSL証明書のパス
ssl_cert = base_path / 'DigiCertGlobalRootCA.crt.pem'

# MySQL接続URL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {
            "ssl_ca": str(ssl_cert)
        }
    },
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)

print("Current working directory:", os.getcwd())
print("Certificate file exists:", os.path.exists('DigiCertGlobalRootCA.crt.pem'))

# セッションとBaseの定義（他のファイルから使う用）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DBセッション取得のための依存関数
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()