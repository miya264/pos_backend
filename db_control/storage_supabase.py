from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv
import base64
from datetime import datetime
import mimetypes

# .env の読み込み
base_path = Path(__file__).resolve().parent.parent
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# Supabase接続情報
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # バックエンド用

# Supabaseクライアントの作成（service_role key使用）
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class SupabaseStorageManager:
    """Supabaseストレージ機能を管理するクラス"""
    
    def __init__(self):
        self.supabase = supabase
        self.default_bucket = "pos-files"
    
    def create_bucket(self, bucket_name: str, public: bool = False) -> bool:
        """
        バケットを作成
        
        Args:
            bucket_name: バケット名
            public: 公開バケットかどうか
        """
        try:
            self.supabase.storage.create_bucket(
                bucket_name,
                {"public": public}
            )
            print(f"✅ バケット '{bucket_name}' を作成しました")
            return True
        except Exception as e:
            print(f"❌ バケット作成に失敗しました: {e}")
            return False
    
    def upload_file(self, file_path: str, bucket_name: str = None, file_name: str = None) -> Optional[str]:
        """
        ファイルをアップロード
        
        Args:
            file_path: アップロードするファイルのパス
            bucket_name: バケット名（デフォルト: pos-files）
            file_name: 保存するファイル名（デフォルト: 元のファイル名）
        """
        try:
            bucket = bucket_name or self.default_bucket
            file_name = file_name or os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            response = self.supabase.storage.from_(bucket).upload(
                file_name,
                file_data
            )
            
            # 公開URLを取得
            public_url = self.supabase.storage.from_(bucket).get_public_url(file_name)
            
            print(f"✅ ファイル '{file_name}' をアップロードしました")
            return public_url
            
        except Exception as e:
            print(f"❌ ファイルアップロードに失敗しました: {e}")
            return None
    
    def upload_file_data(self, file_data: bytes, file_name: str, bucket_name: str = None) -> Optional[str]:
        """
        バイトデータをファイルとしてアップロード
        
        Args:
            file_data: アップロードするバイトデータ
            file_name: 保存するファイル名
            bucket_name: バケット名（デフォルト: pos-files）
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            response = self.supabase.storage.from_(bucket).upload(
                file_name,
                file_data
            )
            
            # 公開URLを取得
            public_url = self.supabase.storage.from_(bucket).get_public_url(file_name)
            
            print(f"✅ ファイル '{file_name}' をアップロードしました")
            return public_url
            
        except Exception as e:
            print(f"❌ ファイルアップロードに失敗しました: {e}")
            return None
    
    def download_file(self, file_name: str, bucket_name: str = None, save_path: str = None) -> Optional[bytes]:
        """
        ファイルをダウンロード
        
        Args:
            file_name: ダウンロードするファイル名
            bucket_name: バケット名（デフォルト: pos-files）
            save_path: 保存先パス（指定した場合、ファイルとして保存）
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            response = self.supabase.storage.from_(bucket).download(file_name)
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(response)
                print(f"✅ ファイル '{file_name}' を '{save_path}' に保存しました")
            
            return response
            
        except Exception as e:
            print(f"❌ ファイルダウンロードに失敗しました: {e}")
            return None
    
    def delete_file(self, file_name: str, bucket_name: str = None) -> bool:
        """
        ファイルを削除
        
        Args:
            file_name: 削除するファイル名
            bucket_name: バケット名（デフォルト: pos-files）
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            self.supabase.storage.from_(bucket).remove([file_name])
            
            print(f"✅ ファイル '{file_name}' を削除しました")
            return True
            
        except Exception as e:
            print(f"❌ ファイル削除に失敗しました: {e}")
            return False
    
    def list_files(self, bucket_name: str = None, folder: str = None) -> List[Dict[str, Any]]:
        """
        ファイル一覧を取得
        
        Args:
            bucket_name: バケット名（デフォルト: pos-files）
            folder: フォルダパス（指定した場合、そのフォルダ内のみ）
        """
        try:
            bucket = bucket_name or self.default_bucket
            
            response = self.supabase.storage.from_(bucket).list(folder or "")
            
            files = []
            for file_info in response:
                files.append({
                    "name": file_info.get("name"),
                    "size": file_info.get("metadata", {}).get("size"),
                    "created_at": file_info.get("created_at"),
                    "updated_at": file_info.get("updated_at"),
                    "public_url": self.supabase.storage.from_(bucket).get_public_url(file_info.get("name"))
                })
            
            return files
            
        except Exception as e:
            print(f"❌ ファイル一覧取得に失敗しました: {e}")
            return []
    
    def get_public_url(self, file_name: str, bucket_name: str = None) -> Optional[str]:
        """
        ファイルの公開URLを取得
        
        Args:
            file_name: ファイル名
            bucket_name: バケット名（デフォルト: pos-files）
        """
        try:
            bucket = bucket_name or self.default_bucket
            return self.supabase.storage.from_(bucket).get_public_url(file_name)
        except Exception as e:
            print(f"❌ 公開URL取得に失敗しました: {e}")
            return None
    
    def upload_product_image(self, image_data: bytes, product_code: str) -> Optional[str]:
        """
        商品画像をアップロード
        
        Args:
            image_data: 画像データ
            product_code: 商品コード
        """
        try:
            # ファイル名を生成（商品コード_タイムスタンプ.jpg）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"products/{product_code}_{timestamp}.jpg"
            
            return self.upload_file_data(image_data, file_name, "product-images")
            
        except Exception as e:
            print(f"❌ 商品画像アップロードに失敗しました: {e}")
            return None
    
    def upload_receipt_pdf(self, pdf_data: bytes, transaction_id: int) -> Optional[str]:
        """
        レシートPDFをアップロード
        
        Args:
            pdf_data: PDFデータ
            transaction_id: 取引ID
        """
        try:
            # ファイル名を生成（取引ID_タイムスタンプ.pdf）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"receipts/{transaction_id}_{timestamp}.pdf"
            
            return self.upload_file_data(pdf_data, file_name, "receipts")
            
        except Exception as e:
            print(f"❌ レシートPDFアップロードに失敗しました: {e}")
            return None
    
    def upload_backup_data(self, backup_data: bytes, backup_name: str) -> Optional[str]:
        """
        バックアップデータをアップロード
        
        Args:
            backup_data: バックアップデータ
            backup_name: バックアップ名
        """
        try:
            # ファイル名を生成（バックアップ名_タイムスタンプ.sql）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"backups/{backup_name}_{timestamp}.sql"
            
            return self.upload_file_data(backup_data, file_name, "backups")
            
        except Exception as e:
            print(f"❌ バックアップアップロードに失敗しました: {e}")
            return None

# グローバルインスタンス
storage_manager = SupabaseStorageManager()

def get_storage_manager() -> SupabaseStorageManager:
    """ストレージマネージャーを取得"""
    return storage_manager

def initialize_storage_buckets():
    """必要なストレージバケットを初期化"""
    buckets = [
        ("pos-files", True),      # 一般ファイル（公開）
        ("product-images", True), # 商品画像（公開）
        ("receipts", False),      # レシート（非公開）
        ("backups", False),       # バックアップ（非公開）
        ("temp", False)           # 一時ファイル（非公開）
    ]
    
    for bucket_name, is_public in buckets:
        storage_manager.create_bucket(bucket_name, is_public)

# 使用例
if __name__ == "__main__":
    # ストレージバケットを初期化
    initialize_storage_buckets()
    
    # ファイルアップロードの例
    # with open("test.txt", "rb") as f:
    #     file_data = f.read()
    #     url = storage_manager.upload_file_data(file_data, "test.txt")
    #     print(f"アップロードされたファイルのURL: {url}") 