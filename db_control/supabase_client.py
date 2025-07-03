from supabase import create_client, Client
import os
from pathlib import Path
from dotenv import load_dotenv

# .env の読み込み
base_path = Path(__file__).resolve().parent.parent
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# Supabase接続情報
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # バックエンド用

# Supabaseクライアントの作成（service_role key使用）
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_supabase_client() -> Client:
    """Supabaseクライアントを取得する関数（service_role key使用）"""
    return supabase

def get_supabase_anon_client() -> Client:
    """Supabase匿名クライアントを取得する関数（anon key使用）"""
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY) 