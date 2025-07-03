from supabase import create_client, Client
from fastapi import HTTPException, Depends, Header
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta

# .env の読み込み
base_path = Path(__file__).resolve().parent.parent
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# Supabase接続情報
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # バックエンド用
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')  # フロントエンド用

# Supabaseクライアントの作成（service_role key使用）
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_supabase_auth_client() -> Client:
    """Supabase認証クライアントを取得する関数（service_role key使用）"""
    return supabase

def get_supabase_anon_auth_client() -> Client:
    """Supabase匿名認証クライアントを取得する関数（anon key使用）"""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def verify_jwt_token(token: str) -> dict:
    """JWTトークンを検証する関数"""
    try:
        # SupabaseのJWTトークンを検証（anon keyで検証）
        payload = jwt.decode(
            token, 
            SUPABASE_ANON_KEY, 
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="トークンの有効期限が切れています")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無効なトークンです")

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """現在のユーザーを取得する関数（認証必須）"""
    if not authorization:
        raise HTTPException(status_code=401, detail="認証が必要です")
    
    try:
        # Bearer トークンを取得
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="無効な認証スキームです")
        
        # トークンを検証
        payload = verify_jwt_token(token)
        return payload
    except ValueError:
        raise HTTPException(status_code=401, detail="無効な認証ヘッダーです")

def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """現在のユーザーを取得する関数（認証オプション）"""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        
        payload = verify_jwt_token(token)
        return payload
    except:
        return None

def sign_up_user(email: str, password: str, user_data: dict = None) -> dict:
    """ユーザー登録（anon key使用）"""
    try:
        anon_client = get_supabase_anon_auth_client()
        response = anon_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_data or {}
            }
        })
        return response.user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ユーザー登録に失敗しました: {str(e)}")

def sign_in_user(email: str, password: str) -> dict:
    """ユーザーログイン（anon key使用）"""
    try:
        anon_client = get_supabase_anon_auth_client()
        response = anon_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {
            "user": response.user,
            "session": response.session
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"ログインに失敗しました: {str(e)}")

def sign_out_user(token: str) -> bool:
    """ユーザーログアウト（anon key使用）"""
    try:
        anon_client = get_supabase_anon_auth_client()
        anon_client.auth.sign_out()
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ログアウトに失敗しました: {str(e)}")

def reset_password(email: str) -> bool:
    """パスワードリセット（anon key使用）"""
    try:
        anon_client = get_supabase_anon_auth_client()
        anon_client.auth.reset_password_email(email)
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"パスワードリセットに失敗しました: {str(e)}")

def update_user_profile(user_id: str, profile_data: dict) -> dict:
    """ユーザープロフィール更新（service_role key使用）"""
    try:
        response = supabase.auth.update_user({
            "data": profile_data
        })
        return response.user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"プロフィール更新に失敗しました: {str(e)}")

def check_user_permission(user_id: str, required_role: str = None) -> bool:
    """ユーザーの権限をチェック（service_role key使用）"""
    try:
        # ユーザーの役割を取得
        response = supabase.table('employees').select('role').eq('enp_cd', user_id).execute()
        if not response.data:
            return False
        
        user_role = response.data[0].get('role')
        
        # 役割チェック
        if required_role:
            return user_role == required_role
        
        return True
    except Exception:
        return False

def create_api_key(user_id: str, key_name: str) -> str:
    """APIキーを作成（service_role key使用）"""
    try:
        # 簡単なAPIキー生成（本番環境ではより安全な方法を使用）
        api_key = f"sk_{user_id}_{key_name}_{datetime.now().timestamp()}"
        
        # APIキーをデータベースに保存
        supabase.table('api_keys').insert({
            "user_id": user_id,
            "key_name": key_name,
            "api_key": api_key,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }).execute()
        
        return api_key
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"APIキー作成に失敗しました: {str(e)}")

def verify_api_key(api_key: str) -> Optional[str]:
    """APIキーを検証（service_role key使用）"""
    try:
        response = supabase.table('api_keys').select('user_id').eq('api_key', api_key).eq('is_active', True).execute()
        if response.data:
            return response.data[0]['user_id']
        return None
    except Exception:
        return None 