#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import time
import statistics
import glob

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web_scraping import WebScraper
import logging

# テスト用のURL
# TEST_URLS = [
#     "https://example.com",
#     "https://httpbin.org",
#     "https://python.org",
#     "https://developer.mozilla.org",
#     "https://github.com",
#     "https://stackoverflow.com",
#     "https://en.wikipedia.org/wiki/Main_Page",
#     "https://news.ycombinator.com",
#     "https://reddit.com",
#     "https://medium.com"
# ]
TEST_URLS = [
    "https://www.meijiyasuda.co.jp/find/list/beststyle/",
    "https://www.meijiyasuda.co.jp/find/list/medical/",
    "https://www.meijiyasuda.co.jp/find/list/yorisou_shushin/",
    "https://www.meijiyasuda.co.jp/find/point/column/06/",
    "https://www.hokende.com/life-insurance/assembly/item-my14",
    "https://www.meijiyasuda.co.jp/find/list/simple_shushin/",
    "https://www.meijiyasuda.co.jp/find2/light/knowledge/list/18.html",
    "https://www.mykenpo.or.jp/member/outline/",
    "https://www.mykenpo.or.jp/member/outline/benefit.html",
    "https://www.meijiyasuda-sonpo.co.jp/product/welfare/"
]

def calculate_directory_size(directory):
    """指定されたディレクトリ内のMarkdownファイルの合計サイズを計算"""
    total_size = 0
    file_count = 0
    for filepath in glob.glob(os.path.join(directory, "*.md")):
        if os.path.isfile(filepath):
            total_size += os.path.getsize(filepath)
            file_count += 1
    return total_size, file_count

def run_sync_test(scraper, urls):
    """同期処理のテストを実行"""
    start_time = time.time()
    
    results = scraper.scrape_multiple_urls(
        urls,
        output_dir="perf_test_sync",
        save_json=False,
        save_markdown=True,
        exclude_links=True,
        max_depth=20
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    success_count = sum(1 for data in results.values() if data["raw_html"] is not None)
    total_size, file_count = calculate_directory_size("perf_test_sync")
    
    return elapsed_time, success_count, results, total_size, file_count

async def run_async_test(scraper, urls):
    """非同期処理のテストを実行"""
    start_time = time.time()
    
    results = await scraper.scrape_multiple_urls_async(
        urls,
        output_dir="perf_test_async",
        save_json=False,
        save_markdown=True,
        exclude_links=True,
        max_depth=20
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    success_count = sum(1 for data in results.values() if data["raw_html"] is not None)
    total_size, file_count = calculate_directory_size("perf_test_async")
    
    return elapsed_time, success_count, results, total_size, file_count

async def main():
    # ログの設定
    logging.basicConfig(level=logging.INFO)
    
    # WebScraperのインスタンス化
    scraper = WebScraper()
    
    print("=== パフォーマンス比較テスト開始 ===")
    print(f"テスト対象URL数: {len(TEST_URLS)}")
    
    # 各テストの実行回数
    num_tests = 1
    
    # 同期処理のテスト結果
    sync_times = []
    sync_success_counts = []
    sync_sizes = []
    sync_file_counts = []
    
    # 非同期処理のテスト結果
    async_times = []
    async_success_counts = []
    async_sizes = []
    async_file_counts = []
    
    # 複数回テストを実行して平均を取る
    for i in range(num_tests):
        print(f"\nテスト {i+1}/{num_tests}")
        
        # 同期処理のテスト
        print("同期処理テスト実行中...")
        sync_time, sync_success, _, sync_size, sync_count = run_sync_test(scraper, TEST_URLS)
        sync_times.append(sync_time)
        sync_success_counts.append(sync_success)
        sync_sizes.append(sync_size)
        sync_file_counts.append(sync_count)
        print(f"同期処理完了: {sync_time:.2f}秒, 成功数: {sync_success}/{len(TEST_URLS)}")
        print(f"保存されたファイル: {sync_count}個, 合計サイズ: {sync_size/1024:.2f}KB")
        
        # 非同期処理のテスト
        print("非同期処理テスト実行中...")
        async_time, async_success, _, async_size, async_count = await run_async_test(scraper, TEST_URLS)
        async_times.append(async_time)
        async_success_counts.append(async_success)
        async_sizes.append(async_size)
        async_file_counts.append(async_count)
        print(f"非同期処理完了: {async_time:.2f}秒, 成功数: {async_success}/{len(TEST_URLS)}")
        print(f"保存されたファイル: {async_count}個, 合計サイズ: {async_size/1024:.2f}KB")
        
        # 少し待機して次のテストを実行
        await asyncio.sleep(1)
    
    # 結果の集計
    avg_sync_time = statistics.mean(sync_times)
    avg_async_time = statistics.mean(async_times)
    avg_sync_success = statistics.mean(sync_success_counts)
    avg_async_success = statistics.mean(async_success_counts)
    avg_sync_size = statistics.mean(sync_sizes)
    avg_async_size = statistics.mean(async_sizes)
    avg_sync_file_count = statistics.mean(sync_file_counts)
    avg_async_file_count = statistics.mean(async_file_counts)
    
    # 速度向上率の計算
    speedup = (avg_sync_time - avg_async_time) / avg_sync_time * 100
    
    print("\n=== テスト結果サマリー ===")
    print(f"同期処理の平均時間: {avg_sync_time:.2f}秒, 平均成功数: {avg_sync_success:.1f}/{len(TEST_URLS)}")
    print(f"同期処理の平均ファイル数: {avg_sync_file_count:.1f}, 平均合計サイズ: {avg_sync_size/1024:.2f}KB")
    print(f"非同期処理の平均時間: {avg_async_time:.2f}秒, 平均成功数: {avg_async_success:.1f}/{len(TEST_URLS)}")
    print(f"非同期処理の平均ファイル数: {avg_async_file_count:.1f}, 平均合計サイズ: {avg_async_size/1024:.2f}KB")
    print(f"速度向上率: {speedup:.2f}%")
    
    if speedup > 0:
        print(f"非同期処理は同期処理より約 {speedup:.2f}% 高速です")
    else:
        print(f"非同期処理は同期処理より約 {-speedup:.2f}% 低速です")
    
    print("\n=== 詳細結果 ===")
    print("同期処理時間:", [f"{t:.2f}秒" for t in sync_times])
    print("非同期処理時間:", [f"{t:.2f}秒" for t in async_times])
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    # 非同期メインループを実行
    asyncio.run(main()) 