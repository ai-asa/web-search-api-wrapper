# %%
from src.web_search import WebSearch
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def main(query, max_results=10, custom_search_engine_id=GOOGLE_CSE_ID):
    """Google Custom Search APIを使用した検索のテスト
    
    Args:
        query (str): 検索クエリ
        max_results (int, optional): 取得する検索結果の最大数。デフォルトは10
        custom_search_engine_id (str, optional): カスタム検索エンジンID。指定がない場合は環境変数の値を使用
    """
    
    try:
        # WebSearchインスタンスの作成（Googleをデフォルトエンジンとして設定）
        web_search = WebSearch(default_engine="google")
        
        # スクレイピングオプションの設定
        scrape_options = {
            "output_dir": "google_results",
            "save_json": False,
            "save_markdown": True,
            "exclude_links": True,  # リンクを除外
            "max_depth": 20
        }
        
        # 検索の実行とスクレイピング
        print(f"\n=== 検索クエリ: {query} (max_results: {max_results}) ===")
        results = web_search.search_and_standardize(
            query,
            scrape_urls=True,
            scrape_options=scrape_options,
            max_results=max_results,
            custom_search_engine_id=custom_search_engine_id
        )
        
        # 検索結果の表示
        print("\n検索結果:")
        for i, result in enumerate(results["search_results"], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Link: {result['link']}")
            print(f"   Snippet: {result['snippet']}")
        
        # スクレイピング結果の表示
        # if results["scraped_data"]:
        #     print("\nスクレイピング結果:")
        #     for url, data in results["scraped_data"].items():
        #         print(f"\nURL: {url}")
        #         if data["json_data"]:
        #             print(f"JSONデータ: {data['json_data']}")
        #         if data["markdown_data"]:
        #             print(f"Markdownデータ: {data['markdown_data']}")
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    # 検索クエリ
    query = "明治安田生命 医療保険 特徴 メリット"
    # カスタム検索エンジンIDを指定する場合は以下のようにします
    # main(query, max_results=10, custom_search_engine_id="your_custom_id")
    main(query, max_results=10)

# %% 