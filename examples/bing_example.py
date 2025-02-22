from bing_web_search import BingWebSearch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    # BingWebSearchクラスのインスタンスを作成
    bing_search = BingWebSearch()

    # 検索を実行
    results = bing_search.search("python 初心者", count=5)

    # 結果を表示
    for item in results.get("webPages", {}).get("value", []):
        print(f"Title: {item['name']}")
        print(f"Link: {item['url']}")
        print(f"Snippet: {item['snippet']}")
        print("-" * 50)

if __name__ == "__main__":
    main() 