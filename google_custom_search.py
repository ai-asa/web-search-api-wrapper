#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %%

import os
import datetime
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

# ここに取得したAPIキーと検索エンジンIDを設定
GOOGLE_API_KEY          = "AIzaSyDiDEcmi70f72CBdK6Gf-KisasRaXfiBIs"
CUSTOM_SEARCH_ENGINE_ID = "0197bfdc61b76469d"# "75d2dc17ad1bd4ddd" 

def get_search_response(keyword):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    page_limit = 1  # 1リクエストで10件取得可能
    start_index = 1
    responses = []
    
    for _ in range(page_limit):
        try:
            sleep(1)  # API利用制限対策として1秒スリープ
            result = service.cse().list(
                q=keyword,
                cx=CUSTOM_SEARCH_ENGINE_ID,
                lr='lang_ja',
                num=4,
                start=start_index
            ).execute()
            responses.append(result)
            
            # 次ページがある場合はstart_indexを更新
            if "queries" in result and "nextPage" in result["queries"]:
                start_index = result["queries"]["nextPage"][0]["startIndex"]
            else:
                break
        except Exception as e:
            print("Error:", e)
            break
    return responses

def print_raw_response(response):
    print("=== Raw API Response ===")
    print(json.dumps(response, ensure_ascii=False, indent=2))

def process_and_print_response(response):
    print("\n=== Processed Search Results ===")
    results = []
    cnt = 0
    
    # 各APIレスポンスからitems（検索結果）を抽出
    for one_res in response:
        if "items" in one_res:
            for item in one_res["items"]:
                cnt += 1
                results.append({
                    "no": cnt,
                    "display_link": item.get("displayLink", ""),
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "").replace("\n", " ")
                })
    
    # 整形した検索結果をprint
    for r in results:
        print(f"{r['no']}. {r['title']}")
        print(f"   Display Link: {r['display_link']}")
        print(f"   Link: {r['link']}")
        print(f"   Snippet: {r['snippet']}\n")

def main():
    target_keyword = "NYダウ　平均株価"
    api_response = get_search_response(target_keyword)
    print_raw_response(api_response)
    process_and_print_response(api_response)

if __name__ == '__main__':
    main()

# %%
