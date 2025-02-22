import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from duckduckgo_instant_answer import DuckDuckGoInstantAnswer

def main():
    # DuckDuckGoInstantAnswerクラスのインスタンスを作成
    ddg_search = DuckDuckGoInstantAnswer()

    # 検索種別の選択（"text", "images", "news", "maps", "proxies", "suggestions", "translate", "videos"）
    search_type = "text"  # ここを "images" などに変更可能

    # クエリを指定して検索を実行
    results = ddg_search.search("Apple", search_type=search_type)# , timelimit="2025-02-20..2025-02-21"
    # 結果をtextファイルに保存
    # with open("results.txt", "w", encoding="utf-8") as f:
    #     f.write(str(results))

    print(f"--- {search_type.upper()} Search Results ---")
    for i, result in enumerate(results, start=1):
        if search_type == "text":
            print(f"Result {i}:")
            print(f"Title: {result.get('title', 'No title available')}")
            print(f"URL: {result.get('href', 'No URL available')}")
            print(f"Snippet: {result.get('body', 'No snippet available')}")
        elif search_type == "images":
            print(f"Result {i}:")
            print(f"Title: {result.get('title', 'No title available')}")
            print(f"Image URL: {result.get('image', 'No image URL available')}")
        elif search_type == "news":
            print(f"Result {i}:")
            print(f"Title: {result.get('title', 'No title available')}")
            print(f"URL: {result.get('url', 'No URL available')}")
            print(f"Date: {result.get('date', 'No date available')}")
        elif search_type == "videos":
            print(f"Result {i}:")
            print(result)
        print("-" * 50)

if __name__ == "__main__":
    main()


