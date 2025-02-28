# %%
from src.web_search import WebSearch

def main(query):
    """WebSearchクラスの使用例"""
    
    try:
        # WebSearchインスタンスの作成
        web_search = WebSearch(default_engine="google")
        
        # 利用可能な検索エンジンの表示
        available_engines = web_search.available_engines()
        if available_engines:
            print(f"\n利用可能な検索エンジン: {available_engines}")
        else:
            print("\n利用可能な検索エンジンがありません。")
            return
        
        # パート1: search()メソッドと process_results()メソッドを別々に使用する例
        print("\n=== パート1: search()とprocess_results()を別々に使用 ===")
        
        # Google検索の実行（デフォルト）
        if "google" in available_engines:
            print("\n=== Google検索結果 ===")
            try:
                google_results = web_search.search(query)
                google_standardized = web_search.process_results(google_results)
                
                # 標準化された結果の表示
                for i, result in enumerate(google_standardized, 1):
                    print(f"{i}. {result['title']}")
                    print(f"   Link: {result['link']}")
                    print(f"   Snippet: {result['snippet']}\n")
            except Exception as e:
                print(f"エラー: {e}")
        
        # # Bing検索の実行
        # if "bing" in available_engines:
        #     print("\n=== Bing検索結果 ===")
        #     try:
        #         bing_results = web_search.search(query, engine="bing", count=4, mkt="ja-JP")
        #         bing_standardized = web_search.process_results(bing_results, engine="bing")
                
        #         # 標準化された結果の表示
        #         for i, result in enumerate(bing_standardized, 1):
        #             print(f"{i}. {result['title']}")
        #             print(f"   Link: {result['link']}")
        #             print(f"   Snippet: {result['snippet']}\n")
        #     except Exception as e:
        #         print(f"エラー: {e}")
        
        # パート2: search_and_standardize()メソッドを使用する例
        print("\n=== パート2: search_and_standardize()を使用 ===")
        
        # Google検索の実行（デフォルト）
        if "google" in available_engines:
            print("\n=== Google検索結果 (search_and_standardize) ===")
            try:
                results = web_search.search_and_standardize(query)
                
                # 標準化された結果の表示
                for i, result in enumerate(results["search_results"], 1):
                    print(f"{i}. {result['title']}")
                    print(f"   Link: {result['link']}")
                    print(f"   Snippet: {result['snippet']}\n")
            except Exception as e:
                print(f"エラー: {e}")
        
        # # Bing検索の実行
        # if "bing" in available_engines:
        #     print("\n=== Bing検索結果 (search_and_standardize) ===")
        #     try:
        #         bing_results = web_search.search_and_standardize(query, engine="bing", count=4, mkt="ja-JP")
                
        #         # 標準化された結果の表示
        #         for i, result in enumerate(bing_results, 1):
        #             print(f"{i}. {result['title']}")
        #             print(f"   Link: {result['link']}")
        #             print(f"   Snippet: {result['snippet']}\n")
        #     except Exception as e:
        #         print(f"エラー: {e}")
        
        # DuckDuckGo検索の実行
        if "duckduckgo" in available_engines:
            print("\n=== DuckDuckGo検索結果 (search_and_standardize) ===")
            try:
                results = web_search.search_and_standardize(query, engine="duckduckgo", max_results=4)
                
                # 標準化された結果の表示
                for i, result in enumerate(results["search_results"], 1):
                    print(f"{i}. {result['title']}")
                    print(f"   Link: {result['link']}")
                    print(f"   Snippet: {result['snippet']}\n")
            except Exception as e:
                print(f"エラー: {e}")
        
        # パート3: スクレイピング機能を使用する例
        print("\n=== パート3: スクレイピング機能を使用 ===")
        
        # スクレイピングオプションの設定（リンクを含む）
        scrape_options = {
            "output_dir": "scraped_results",
            "save_json": True,
            "save_markdown": True,
            "exclude_links": False  # リンクを含める
        }
        
        # Google検索結果のスクレイピング（リンクを含む）
        if "google" in available_engines:
            print("\n=== Google検索結果とスクレイピング（リンクを含む） ===")
            try:
                results = web_search.search_and_standardize(
                    query,
                    scrape_urls=True,
                    scrape_options=scrape_options
                )
                
                # 検索結果の表示
                print("\n検索結果:")
                for i, result in enumerate(results["search_results"], 1):
                    print(f"{i}. {result['title']}")
                    print(f"   Link: {result['link']}")
                    print(f"   Snippet: {result['snippet']}\n")
                
                # スクレイピング結果の表示
                if results["scraped_data"]:
                    print("\nスクレイピング結果:")
                    for url, data in results["scraped_data"].items():
                        print(f"\nURL: {url}")
                        if data["json_file"]:
                            print(f"JSONファイル: {data['json_file']}")
                        if data["markdown_file"]:
                            print(f"Markdownファイル: {data['markdown_file']}")
            except Exception as e:
                print(f"エラー: {e}")
        
        # DuckDuckGo検索結果のスクレイピング（カスタムオプション、リンクを除外）
        if "duckduckgo" in available_engines:
            print("\n=== DuckDuckGo検索結果とスクレイピング（JSONのみ保存、リンクを除外） ===")
            try:
                custom_options = {
                    "output_dir": "ddg_results",
                    "save_json": True,
                    "save_markdown": False,
                    "exclude_links": True  # リンクを除外
                }
                
                results = web_search.search_and_standardize(
                    query,
                    engine="duckduckgo",
                    max_results=4,
                    scrape_urls=True,
                    scrape_options=custom_options
                )
                
                # 検索結果の表示
                print("\n検索結果:")
                for i, result in enumerate(results["search_results"], 1):
                    print(f"{i}. {result['title']}")
                    print(f"   Link: {result['link']}")
                    print(f"   Snippet: {result['snippet']}\n")
                
                # スクレイピング結果の表示
                if results["scraped_data"]:
                    print("\nスクレイピング結果:")
                    for url, data in results["scraped_data"].items():
                        print(f"\nURL: {url}")
                        if data["json_file"]:
                            print(f"JSONファイル: {data['json_file']}")
            except Exception as e:
                print(f"エラー: {e}")

    except Exception as e:
        print(f"WebSearchクラスの初期化エラー: {e}")

if __name__ == "__main__":
    # 検索クエリ
    query = "人工知能 最新技術"
    main(query) 
# %%
