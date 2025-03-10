# %%
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import time

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web_scraping import WebScraper
import logging

async def main():
    # ログの設定
    logging.basicConfig(level=logging.INFO)
    
    # WebScraperのインスタンス化
    scraper = WebScraper()
    
    # オプション設定
    exclude_links = True  # リンクを除外する
    save_json = True      # JSON形式で保存する
    save_markdown = True  # Markdown形式で保存する
    
    # テスト用のURL
    test_urls = [
        "https://example.com",  # シンプルな構造のサイト
        "https://httpbin.org",  # APIテスト用サイト
        "https://ins.minkabu.jp/medical/sbi_life-4006"
    ]
    
    print(f"\n=== 非同期スクレイピング開始 ===")
    print(f"オプション: リンク除外={exclude_links}, JSON保存={save_json}, Markdown保存={save_markdown}")
    
    # 処理時間計測開始
    start_time = time.time()
    
    # 非同期で複数URLのスクレイピングを実行
    results = await scraper.scrape_multiple_urls_async(
        test_urls,
        output_dir="scraped_data_async",
        save_json=save_json,
        save_markdown=save_markdown,
        exclude_links=exclude_links,
        max_depth=20
    )
    
    # 処理時間計測終了
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 結果の表示と利用
    for url, data in results.items():
        print(f"\n処理結果 - {url}")
        
        if data["raw_html"]:
            print("- スクレイピング成功")
            print(f"  - 生HTMLデータのサイズ: {len(data['raw_html'])} 文字")
            print(f"  - JSONデータのサイズ: {len(str(data['json_data']))} 文字")
            print(f"  - Markdownデータのサイズ: {len(data['markdown_data'])} 文字")
            
            if data["json_file"]:
                print(f"  - JSON保存先: {data['json_file']}")
            if data["markdown_file"]:
                print(f"  - Markdown保存先: {data['markdown_file']}")
                
            # データの利用例
            # 例1: 最初の子要素のタグを表示
            if data["json_data"]["children"]:
                first_child = data["json_data"]["children"][0]
                if isinstance(first_child, dict):
                    print(f"  - 最初の子要素のタグ: {first_child.get('tag', 'unknown')}")
            
            # 例2: HTMLのタイトルを抽出（簡易的な方法）
            title_start = data["raw_html"].find("<title>")
            title_end = data["raw_html"].find("</title>")
            if title_start != -1 and title_end != -1:
                title = data["raw_html"][title_start + 7:title_end].strip()
                print(f"  - ページタイトル: {title}")
        else:
            print("- スクレイピングに失敗しました")
    
    print(f"\n=== 処理完了 ===")
    print(f"処理時間: {elapsed_time:.2f}秒")

if __name__ == "__main__":
    # 非同期メインループを実行
    asyncio.run(main()) 
# %%
