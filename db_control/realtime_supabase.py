from supabase import create_client, Client
from typing import Callable, Dict, Any, Optional
import asyncio
import json
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

class SupabaseRealtimeManager:
    """Supabaseリアルタイム機能を管理するクラス"""
    
    def __init__(self):
        self.supabase = supabase
        self.channels = {}
        self.callbacks = {}
    
    def subscribe_to_table(self, table_name: str, event: str = "*", callback: Callable = None):
        """
        テーブルの変更を監視する
        
        Args:
            table_name: 監視するテーブル名
            event: 監視するイベント（INSERT, UPDATE, DELETE, *）
            callback: 変更時のコールバック関数
        """
        try:
            channel = self.supabase.channel(f"table-{table_name}")
            
            if event == "*":
                channel = channel.on(
                    "postgres_changes",
                    event="*",
                    schema="public",
                    table=table_name,
                    callback=callback or self._default_callback
                )
            else:
                channel = channel.on(
                    "postgres_changes",
                    event=event,
                    schema="public",
                    table=table_name,
                    callback=callback or self._default_callback
                )
            
            channel.subscribe()
            self.channels[table_name] = channel
            self.callbacks[table_name] = callback
            
            print(f"✅ {table_name}テーブルの監視を開始しました（イベント: {event}）")
            
        except Exception as e:
            print(f"❌ {table_name}テーブルの監視開始に失敗しました: {e}")
    
    def unsubscribe_from_table(self, table_name: str):
        """テーブルの監視を停止"""
        if table_name in self.channels:
            try:
                self.channels[table_name].unsubscribe()
                del self.channels[table_name]
                del self.callbacks[table_name]
                print(f"✅ {table_name}テーブルの監視を停止しました")
            except Exception as e:
                print(f"❌ {table_name}テーブルの監視停止に失敗しました: {e}")
    
    def _default_callback(self, payload):
        """デフォルトのコールバック関数"""
        print(f"📡 リアルタイム更新: {payload}")
    
    def subscribe_to_orders(self, callback: Callable = None):
        """注文テーブルの監視"""
        def order_callback(payload):
            event_type = payload.get('eventType')
            record = payload.get('record', {})
            
            if event_type == 'INSERT':
                print(f"🆕 新しい注文が作成されました: 注文ID {record.get('trd_id')}")
            elif event_type == 'UPDATE':
                print(f"📝 注文が更新されました: 注文ID {record.get('trd_id')}")
            elif event_type == 'DELETE':
                print(f"🗑️ 注文が削除されました: 注文ID {record.get('trd_id')}")
            
            if callback:
                callback(payload)
        
        self.subscribe_to_table('orders', '*', order_callback)
    
    def subscribe_to_products(self, callback: Callable = None):
        """商品テーブルの監視"""
        def product_callback(payload):
            event_type = payload.get('eventType')
            record = payload.get('record', {})
            
            if event_type == 'INSERT':
                print(f"🆕 新しい商品が追加されました: {record.get('name')}")
            elif event_type == 'UPDATE':
                print(f"📝 商品が更新されました: {record.get('name')}")
            elif event_type == 'DELETE':
                print(f"🗑️ 商品が削除されました: {record.get('name')}")
            
            if callback:
                callback(payload)
        
        self.subscribe_to_table('products', '*', product_callback)
    
    def subscribe_to_customers(self, callback: Callable = None):
        """顧客テーブルの監視"""
        def customer_callback(payload):
            event_type = payload.get('eventType')
            record = payload.get('record', {})
            
            if event_type == 'INSERT':
                print(f"🆕 新しい顧客が登録されました: {record.get('name')}")
            elif event_type == 'UPDATE':
                print(f"📝 顧客情報が更新されました: {record.get('name')}")
            elif event_type == 'DELETE':
                print(f"🗑️ 顧客が削除されました: {record.get('name')}")
            
            if callback:
                callback(payload)
        
        self.subscribe_to_table('customers', '*', customer_callback)
    
    def broadcast_message(self, channel: str, message: Dict[str, Any]):
        """チャンネルにメッセージをブロードキャスト"""
        try:
            self.supabase.channel(channel).send({
                "type": "broadcast",
                "event": "message",
                "payload": message
            })
            print(f"📢 チャンネル {channel} にメッセージを送信しました")
        except Exception as e:
            print(f"❌ メッセージ送信に失敗しました: {e}")
    
    def subscribe_to_channel(self, channel: str, callback: Callable = None):
        """カスタムチャンネルを監視"""
        try:
            channel_obj = self.supabase.channel(channel)
            channel_obj.on("broadcast", {"event": "message"}, callback or self._default_callback)
            channel_obj.subscribe()
            self.channels[channel] = channel_obj
            print(f"✅ チャンネル {channel} の監視を開始しました")
        except Exception as e:
            print(f"❌ チャンネル {channel} の監視開始に失敗しました: {e}")

# グローバルインスタンス
realtime_manager = SupabaseRealtimeManager()

def get_realtime_manager() -> SupabaseRealtimeManager:
    """リアルタイムマネージャーを取得"""
    return realtime_manager

def start_realtime_monitoring():
    """リアルタイム監視を開始"""
    try:
        # 主要テーブルの監視を開始
        realtime_manager.subscribe_to_orders()
        realtime_manager.subscribe_to_products()
        realtime_manager.subscribe_to_customers()
        
        print("✅ リアルタイム監視を開始しました")
        
    except Exception as e:
        print(f"❌ リアルタイム監視の開始に失敗しました: {e}")

def stop_realtime_monitoring():
    """リアルタイム監視を停止"""
    try:
        for table_name in list(realtime_manager.channels.keys()):
            realtime_manager.unsubscribe_from_table(table_name)
        
        print("✅ リアルタイム監視を停止しました")
        
    except Exception as e:
        print(f"❌ リアルタイム監視の停止に失敗しました: {e}")

# 使用例
if __name__ == "__main__":
    # リアルタイム監視を開始
    start_realtime_monitoring()
    
    try:
        # 監視を継続
        while True:
            asyncio.sleep(1)
    except KeyboardInterrupt:
        # Ctrl+Cで停止
        stop_realtime_monitoring()
        print("リアルタイム監視を終了しました") 