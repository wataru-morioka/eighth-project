## Flask Api サーバ
### 概要
お問い合わせリクエスト受付　Restful Api（POST）
### 機能一覧
- アプリケーションサーバ機能（uwsgi）  
- リクエスト受付（flask_restful）  
- CORS対策（flask_cors）  
- お問い合わせ内容をDBに登録（postgreSQL）  
- お問い合わせ内容を管理者にメール送信（googleメールサーバ使用）  
- firebase認証機能利用（匿名認証）  
- ORマッパー（flask_sqlalchemy）  
- DBマイグレーション機能（flask_migrate）  
- ロギング（/var/log/uwsgi配下）  

