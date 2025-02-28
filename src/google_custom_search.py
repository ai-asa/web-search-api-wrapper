# %%

from dotenv import load_dotenv
import os
import json
from time import sleep
from googleapiclient.discovery import build

# 検証事項
# 1. 時事ネタを集めることができるか
    # トレンドデータの取得
    # トレンドデータからキーワード選出し、スクレイピング
    # → Google TrendsはAPIを提供していない
    # → URLにて条件指定が可能
    # → スクレイピングでトレンドワードを取得可能
# 2. 特定の保険商品の情報を集めることができるか
    # 保険会社のサイトをサーチ対象に指定
    # 有効なページをスクレイピング
# 3. 特定の保険商品の口コミ情報を集めることができるか
    # 口コミサイトをサーチ対象に指定
    # 有効なページをスクレイピング
    # → オリコン顧客満足度ランキングはURLにて条件指定が可能
    # → スクレイピングで口コミ情報を取得可能
    # → スクレイピング及びクローイングが必要
    # ※ただし、この方法だと個別の保険商品の口コミは取得できない 
    # 「保険商品名　評判」で検索し、複数のサイトをスクレイピングして整形処理
    # → この方法であれば処理可能

#　具体的な設計
# 1. 時事ネタについて
    # 特定のキーワードを複数用意しておく
    # キーワードごとにDuckDuckGo検索でNewsカテゴリを指定して検索
    # 検索結果を連続して並べたプロンプトを作成
    # AIで時事ネタ候補を複数生成する
# 2. 保険商品の情報について
    # 保険会社のサイトをサーチ対象に指定

# 3. 保険商品の口コミ情報について
    # 口コミサイトをサーチ対象に指定

# 4. 「相談」機能における自動検索について
    # 保険会社のサイトをサーチ対象に指定


# ここに取得したAPIキーと検索エンジンIDを設定

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def get_search_response(keyword, max_results=10, custom_search_engine_id=GOOGLE_CSE_ID):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    responses = []
    
    try:
        result = service.cse().list(
            q=keyword,
            cx=custom_search_engine_id,
            lr='lang_ja',
            num=max_results,# 1リクエストで10件取得可能
        ).execute()
        responses.append(result)
    except Exception as e:
        print("Error:", e)
    return responses

def main():
    target_keyword = "NYダウ　平均株価"
    api_response = get_search_response(target_keyword)
    print(api_response)

if __name__ == '__main__':
    main()

# %%
