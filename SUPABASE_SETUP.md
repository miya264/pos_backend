# Supabaseセットアップガイド

このプロジェクトはSQLite、MySQL、Supabaseの3つのデータベースに対応しています。現在はSQLiteが使用されており、Supabaseに移行する場合は以下の手順に従ってください。

## 1. Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com)にアクセスしてアカウントを作成
2. 新しいプロジェクトを作成
3. プロジェクトの設定から以下の情報を取得：
   - Project URL
   - **Anon Key** (フロントエンド用)
   - **Service Role Key** (バックエンド用)
   - Database Password

## 2. Supabaseキーの種類と使用方法

### Anon Key（匿名キー）
- **用途**: フロントエンド（ブラウザ）からのアクセス
- **権限**: 制限された権限（RLSポリシーに従う）
- **セキュリティ**: 公開しても安全（ただし適切なRLS設定が必要）
- **使用場面**: ユーザー登録、ログイン、JWT検証

### Service Role Key（サービスロールキー）
- **用途**: バックエンド（サーバー）からのアクセス
- **権限**: 管理者権限（RLSをバイパス）
- **セキュリティ**: **絶対に公開してはいけない**
- **使用場面**: データベース操作、ユーザー管理、APIキー管理

## 3. 環境変数の設定

`pos_back/env.example`を参考に、`pos_back/.env`ファイルを作成し、以下の情報を設定：

```env
# Supabase設定
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_DB_PASSWORD=your_database_password

# アプリケーション設定
APP_ENV=development
DEBUG=True
```

**重要**: `SUPABASE_SERVICE_ROLE_KEY`は絶対に公開リポジトリにコミットしないでください！

## 4. 依存関係のインストール

```bash
cd pos_back
pip install -r requirements.txt
```

## 5. テーブルの作成

SupabaseのSQL Editorで以下のSQLを実行：

```sql
-- 商品テーブル
CREATE TABLE products (
    prd_id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    price INTEGER NOT NULL
);

-- 顧客テーブル
CREATE TABLE customers (
    cust_id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(100),
    point INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    synced_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- クーポンテーブル
CREATE TABLE coupons (
    coupon_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    discount INTEGER NOT NULL,
    type VARCHAR(1) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    limit_cnt INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 従業員テーブル
CREATE TABLE employees (
    enp_cd VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255),
    role VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- 注文テーブル
CREATE TABLE orders (
    trd_id SERIAL PRIMARY KEY,
    datetime TIMESTAMP NOT NULL,
    enp_cd VARCHAR(10) NOT NULL REFERENCES employees(enp_cd),
    store_cd VARCHAR(5) NOT NULL,
    pos_no VARCHAR(3) NOT NULL,
    total_amt INTEGER NOT NULL,
    ttl_amt_ex_tax INTEGER NOT NULL,
    cust_id INTEGER REFERENCES customers(cust_id),
    used_point INTEGER,
    coupon_id VARCHAR(20) REFERENCES coupons(coupon_id),
    discount_by_cp INTEGER,
    final_amt INTEGER NOT NULL
);

-- 注文詳細テーブル
CREATE TABLE order_details (
    dtl_id SERIAL PRIMARY KEY,
    trd_id INTEGER NOT NULL REFERENCES orders(trd_id),
    prd_id INTEGER NOT NULL REFERENCES products(prd_id),
    prd_code VARCHAR(20) NOT NULL,
    prd_name VARCHAR(50) NOT NULL,
    prd_price INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    tax_cd VARCHAR(2) NOT NULL
);

-- クーポン履歴テーブル
CREATE TABLE coupon_histories (
    crm_id VARCHAR(64) PRIMARY KEY,
    coupon_id VARCHAR(20) NOT NULL REFERENCES coupons(coupon_id),
    used_at TIMESTAMP NOT NULL,
    trd_id INTEGER NOT NULL REFERENCES orders(trd_id)
);

-- APIキーテーブル（認証機能用）
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- RLS（Row Level Security）の設定
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE coupons ENABLE ROW LEVEL SECURITY;
ALTER TABLE coupon_histories ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- 基本的なポリシー（全ユーザーが読み取り可能）
CREATE POLICY "Allow public read access" ON products FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON customers FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON orders FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON order_details FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON employees FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON coupons FOR SELECT USING (true);
```

## 6. ストレージバケットの作成

Supabaseのダッシュボードで以下のストレージバケットを作成：

- `pos-files` (公開)
- `product-images` (公開)
- `receipts` (非公開)
- `backups` (非公開)
- `temp` (非公開)

または、以下のPythonスクリプトを実行：

```bash
cd pos_back
python -c "from db_control.storage_supabase import initialize_storage_buckets; initialize_storage_buckets()"
```

## 7. 初期データの登録

```bash
cd pos_back
python -m db_control.seed_data_supabase
```

## 8. データベース接続の切り替え

`pos_back/db_control/connect.py`で、SQLiteの設定をコメントアウトし、Supabaseの設定を有効にします：

```python
# SQLite接続URL構築（コメントアウト）
# DATABASE_URL = f"sqlite:///{base_path}/pos.db"

# Supabase接続URL構築
DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{SUPABASE_URL.split('//')[1]}:5432/postgres"
```

## 9. APIサーバーの起動

### SQLAlchemy版（従来）
```bash
cd pos_back
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Supabase版（新規）
```bash
cd pos_back
uvicorn app_supabase:app --reload --host 0.0.0.0 --port 8001
```

## 10. 認証機能の使用

### ユーザー登録（Anon Key使用）
```bash
curl -X POST "http://localhost:8001/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### ユーザーログイン（Anon Key使用）
```bash
curl -X POST "http://localhost:8001/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 認証付きAPI呼び出し
```bash
curl -X GET "http://localhost:8001/products/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 11. リアルタイム機能の使用

```python
from db_control.realtime_supabase import start_realtime_monitoring

# リアルタイム監視を開始
start_realtime_monitoring()
```

## 12. ストレージ機能の使用

```python
from db_control.storage_supabase import get_storage_manager

storage = get_storage_manager()

# ファイルアップロード
with open("image.jpg", "rb") as f:
    image_data = f.read()
    url = storage.upload_product_image(image_data, "PRODUCT001")
    print(f"画像URL: {url}")
```

## ファイル構成

### 新規作成されたファイル
- `db_control/supabase_client.py` - Supabaseクライアント設定
- `db_control/crud_supabase.py` - Supabase用CRUD操作
- `db_control/create_table_supabase.py` - Supabase用テーブル作成
- `db_control/seed_data_supabase.py` - Supabase用シードデータ
- `db_control/schemas_supabase.py` - Supabase用スキーマ定義
- `db_control/auth_supabase.py` - Supabase認証・セキュリティ機能
- `db_control/realtime_supabase.py` - Supabaseリアルタイム機能
- `db_control/storage_supabase.py` - Supabaseストレージ機能
- `app_supabase.py` - Supabase用APIエンドポイント
- `env.example` - 環境変数サンプル
- `SUPABASE_SETUP.md` - このファイル

### 既存ファイルの変更
- `requirements.txt` - Supabase依存関係を追加
- `db_control/connect.py` - Supabase接続設定を追加（SQLiteをコメントアウト）

## 主な機能

### 1. データベース機能
- PostgreSQLベースのSupabase接続
- 全テーブルのCRUD操作
- トランザクション管理
- データ整合性チェック

### 2. 認証・セキュリティ機能
- JWTトークン認証（Anon Keyで検証）
- ユーザー登録・ログイン（Anon Key使用）
- パスワードリセット（Anon Key使用）
- 権限管理（Service Role Key使用）
- APIキー管理（Service Role Key使用）

### 3. リアルタイム機能
- テーブル変更のリアルタイム監視
- WebSocket接続
- イベント通知
- カスタムチャンネル

### 4. ストレージ機能
- ファイルアップロード・ダウンロード
- 商品画像管理
- レシートPDF保存
- バックアップ管理

### 5. API機能
- RESTful API
- 認証付きエンドポイント
- エラーハンドリング
- CORS対応

## セキュリティのベストプラクティス

### 1. キーの管理
- **Anon Key**: フロントエンドで使用可能（公開しても安全）
- **Service Role Key**: バックエンドでのみ使用（絶対に公開しない）
- 環境変数で管理し、`.env`ファイルを`.gitignore`に追加

### 2. RLS（Row Level Security）
- すべてのテーブルでRLSを有効化
- 適切なポリシーを設定
- 必要最小限の権限のみ付与

### 3. 認証フロー
- ユーザー登録・ログインはAnon Key使用
- JWT検証はAnon Key使用
- 管理者操作はService Role Key使用

## 注意事項

1. **セキュリティ**: 本番環境では適切なセキュリティ設定を行ってください
2. **制限**: Supabaseの無料プランには制限があります（月間500MB、同時接続数2など）
3. **移行**: データベースの切り替え時は、既存データの移行が必要です
4. **バックアップ**: 定期的なバックアップを設定してください
5. **監視**: リアルタイム機能は適切に管理してください
6. **キー管理**: Service Role Keyは絶対に公開しないでください

## トラブルシューティング

### 接続エラー
- 環境変数が正しく設定されているか確認
- Supabaseプロジェクトが有効か確認
- ネットワーク接続を確認

### 認証エラー
- JWTトークンが有効か確認
- ユーザーが正しく登録されているか確認
- 権限設定を確認
- 適切なキー（Anon/Service Role）を使用しているか確認

### ストレージエラー
- バケットが作成されているか確認
- ファイルサイズ制限を確認
- 権限設定を確認

### 権限エラー
- RLSポリシーが正しく設定されているか確認
- Service Role Keyを使用しているか確認
- テーブルの権限設定を確認 