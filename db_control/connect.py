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

# MySQL接続情報（コメントアウト）
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_HOST = os.getenv('DB_HOST')
# DB_PORT = os.getenv('DB_PORT', '3306')
# DB_NAME = os.getenv('DB_NAME')

# SSL証明書のパス（コメントアウト）
# ssl_cert = base_path / 'DigiCertGlobalRootCA.crt.pem'

# MySQL接続URL構築（コメントアウト）
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLite接続URL構築（コメントアウト）
# DATABASE_URL = f"sqlite:///{base_path}/pos.db"

# Supabase接続情報
# SUPABASE_URL = os.getenv('SUPABASE_URL')
# SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')  # フロントエンド用
# SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # バックエンド用
# SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

user = os.getenv("SUPABASE_DB_USER")
password = os.getenv("SUPABASE_DB_PASSWORD")
host = os.getenv("SUPABASE_DB_HOST")
port = os.getenv("SUPABASE_DB_PORT")
dbname = os.getenv("SUPABASE_DB_NAME")

# Supabase接続URL構築（PostgreSQL直接接続用）
# DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{SUPABASE_URL.split('//')[1]}:5432/postgres"
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

# SQLAlchemy エンジンの作成
engine = create_engine(
    DATABASE_URL,
    # MySQL用の設定（コメントアウト）
    # connect_args={
    #     "ssl": {
    #         "ssl_ca": str(ssl_cert)
    #     },
    #     "init_command": "SET time_zone = '+09:00'"
    # },
    # SQLite用の設定（コメントアウト）
    # echo=True,
    # pool_pre_ping=True,
    # pool_recycle=3600
    # Supabase用の設定
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "sslmode": "require"
    }
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