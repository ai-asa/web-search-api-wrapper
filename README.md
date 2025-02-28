# Web Search API Wrapper

このリポジトリは、複数のウェブ検索API（Google Custom Search API、Bing Web Search API、DuckDuckGo Instant Answer API）の動作検証およびラッパー実装を目的としています。  
後から他のプロジェクトで簡単に再利用できるよう、各APIへのリクエスト処理とレスポンスのパース処理を統一的なインターフェースで提供します。

## 特長

- **統一インターフェース (WebSearch クラス):**  
  複数の検索エンジンAPIを一元管理し、統一されたインターフェースで利用可能

- **Google Custom Search API Wrapper:**  
  キーワード検索結果（タイトル、URL、抜粋、メタデータ等）の取得

- **Bing Web Search API Wrapper:**  
  検索結果（Webページ、画像、ニュース、ビデオ等）をセクション別に取得

- **DuckDuckGo Instant Answer API Wrapper:**  
  インスタント回答（概要、トピック、関連情報）の取得

## 必要条件

- Python 3.7以上
- 必要なPythonパッケージは `requirements.txt` に記載

## インストール

1. リポジトリをクローン

  ```bash
  git clone https://github.com/yourusername/web-search-api-wrapper.git
  cd web-search-api-wrapper
  ```
   
2. 仮想環境の作成・有効化（任意）

  ```bash
  python -m venv venv
  source venv/bin/activate    # Linux/Mac
  venv\Scripts\activate       # Windows
  ```

3. 必要パッケージのインストール

  ```bash
  pip install -r requirements.txt
  ```

## 環境変数の設定
各APIキーや検索エンジンIDは環境変数で管理します。
以下の例のように .env ファイルを作成し、必要なキーを設定してください。

  ```dotenv
  # .env
  GOOGLE_API_KEY=your_google_api_key_here
  GOOGLE_CSE_ID=your_custom_search_engine_id_here
  BING_API_KEY=your_bing_api_key_here
  ```
※ .env の読み込みには python-dotenv を使用してください。

## ファイル構造
  ```pgsql
  web-search-api-wrapper/
  ├── README.md
  ├── requirements.txt
  ├── .env.example            # 環境変数設定例
  ├── google_custom_search.py # Google Custom Search API用ラッパー
  ├── bing_web_search.py      # Bing Web Search API用ラッパー
  ├── duckduckgo_instant_answer.py  # DuckDuckGo Instant Answer API用ラッパー
  ├── examples/               # 各API動作検証用のサンプルスクリプト
  │   ├── src/
  │   │   ├── web_search.py   # 統一インターフェースクラス
  │   │   └── example_usage.py # WebSearchクラスの使用例
  │   ├── google_example.py
  │   ├── bing_example.py
  │   └── duckduckgo_example.py
  └── tests/                  # 単体テスト用
      ├── test_google.py
      ├── test_bing.py
      └── test_duckduckgo.py
  ```

## 使用例

### WebSearch クラスの使用例
WebSearchクラスは、複数の検索エンジンAPIを統一されたインターフェースで利用するための機能を提供します。

```python
from web_search import WebSearch

# WebSearchインスタンスの作成（デフォルトエンジンを指定）
web_search = WebSearch(default_engine="google")

# 利用可能な検索エンジンの確認
available_engines = web_search.available_engines()
print(f"利用可能な検索エンジン: {available_engines}")

# 検索クエリ
query = "人工知能 最新技術"

# デフォルトエンジン（Google）で検索
google_results = web_search.search(query)
# 結果の処理
web_search.process_results(google_results)

# Bingで検索（追加パラメータを指定）
bing_results = web_search.search(query, engine="bing", count=4, mkt="ja-JP")
# 結果の標準化された形式での取得
bing_standardized = web_search.process_results(bing_results, engine="bing")

# DuckDuckGoで検索
ddg_results = web_search.search(query, engine="duckduckgo", max_results=4)
# 結果の標準化された形式での取得
ddg_standardized = web_search.process_results(ddg_results, engine="duckduckgo")
```

サンプルスクリプトを実行するには：
```bash
python examples/src/example_usage.py
```

### 個別APIの使用例
各APIを個別に使用する例も提供しています：

#### Google Custom Search API の例
  ```bash
  python examples/google_example.py
  ```
サンプルスクリプト内では、環境変数からAPIキーと検索エンジンIDを読み込み、指定したキーワードで検索結果を取得し、結果を表示します。

#### Bing Web Search API の例
  ```bash
  python examples/bing_example.py
  ```
#### DuckDuckGo Instant Answer API の例
  ```bash
  python examples/duckduckgo_example.py
  ```
### テスト
**tests**ディレクトリ内に各API用のテストコードを用意しています。
テストを実行するには、以下のようにしてください。
  ```bash
  pytest tests/
  ```

## 補足
- 各APIの詳細な仕様やレスポンス形式については、公式ドキュメントを確認してください。
  - Google Custom Search API: 公式ドキュメント
  - Bing Web Search API: 公式ドキュメント
  - DuckDuckGo Instant Answer API: 公式ドキュメント
