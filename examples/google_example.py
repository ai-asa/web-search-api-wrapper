from google_custom_search import GoogleCustomSearch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    # GoogleCustomSearchクラスのインスタンスを作成
    google_search = GoogleCustomSearch()

    # 検索を実行
    results = google_search.search("python 初心者", num=5)

    # 結果を表示
    for item in results.get("items", []):
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Snippet: {item['snippet']}")
        print("-" * 50)

if __name__ == "__main__":
    main() 