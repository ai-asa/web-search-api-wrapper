import time
import requests
from bs4 import BeautifulSoup, Comment
import statistics

# テスト用のHTMLを取得する関数
def get_test_html():
    # 大きめのウェブページを取得
    urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
    ]
    
    html_contents = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                html_contents.append(response.text)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    return html_contents

# 元の実装
def original_remove_unwanted_elements(soup):
    # 開始時間を記録
    start_time = time.time()
    
    # 各ステップの時間を計測
    times = {}
    
    # 1. script, style, meta, link タグを削除
    step_start = time.time()
    for tag in soup.find_all(['script', 'style', 'meta', 'link', 'noscript']):
        tag.decompose()
    times["1_常に削除する要素"] = time.time() - step_start
    
    # 2. コメントを削除
    step_start = time.time()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    times["2_コメント削除"] = time.time() - step_start
    
    # 3. JSON-LDを含むscriptタグを削除
    step_start = time.time()
    for tag in soup.find_all('script', type='application/ld+json'):
        tag.decompose()
    times["3_JSON-LD削除"] = time.time() - step_start
    
    # 4. 空のdiv, span要素を削除
    step_start = time.time()
    for tag in soup.find_all(['div', 'span']):
        if not tag.get_text(strip=True):
            tag.decompose()
    times["4_空要素削除"] = time.time() - step_start
    
    # 5. データ属性を含む要素を削除
    step_start = time.time()
    for tag in soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs) if tag.attrs else False):
        if not any(child.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li'] for child in tag.find_all()):
            tag.decompose()
    times["5_データ属性要素削除"] = time.time() - step_start

    # 6. インラインスタイルを削除
    step_start = time.time()
    for tag in soup.find_all(style=True):
        del tag['style']
    times["6_インラインスタイル削除"] = time.time() - step_start
    
    # 終了時間を記録
    end_time = time.time()
    total_time = end_time - start_time
    times["total"] = total_time
    
    return times

# 現在の実装
def current_remove_unwanted_elements(soup):
    # 開始時間を記録
    start_time = time.time()
    
    # 各ステップの時間を計測
    times = {}
    
    # 1. 全ての要素を一度に取得
    step_start = time.time()
    all_elements = list(soup.find_all(True))
    times["1_全要素取得"] = time.time() - step_start
    
    # 2. 要素の処理
    step_start = time.time()
    for element in all_elements:
        # 要素が既に削除されている場合はスキップ
        if element.decomposed:
            continue
        
        # 常に削除する要素（script, style, meta, link, noscript）
        if element.name in ['script', 'style', 'meta', 'link', 'noscript']:
            element.decompose()
            continue
        
        # JSON-LDを含むscriptタグ
        if element.name == 'script' and element.get('type') == 'application/ld+json':
            element.decompose()
            continue
        
        # 空のdiv, span要素
        if element.name in ['div', 'span'] and not element.get_text(strip=True):
            element.decompose()
            continue
        
        # データ属性を含む要素（ただし、特定のタグを含む場合は保持）
        if element.attrs:  # 属性が存在する場合のみチェック
            has_data_attr = any(attr.startswith('data-') for attr in element.attrs)
            if has_data_attr:
                # 特定のタグを含むかチェック
                has_important_children = any(
                    child.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']
                    for child in element.find_all(recursive=True)
                )
                if not has_important_children:
                    element.decompose()
                    continue
            
        # インラインスタイルの削除（要素自体は保持）
        if element.attrs and 'style' in element.attrs:
            del element['style']
    times["2_要素処理"] = time.time() - step_start
    
    # 3. コメントの削除
    step_start = time.time()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    times["3_コメント削除"] = time.time() - step_start
    
    # 終了時間を記録
    end_time = time.time()
    total_time = end_time - start_time
    times["total"] = total_time
    
    return times

# 改善案: 直接の子要素のみをチェック（最も良い結果を示した方法）
def improved_direct_children(soup):
    # 開始時間を記録
    start_time = time.time()
    
    # 各ステップの時間を計測
    times = {}
    
    # 1. 全ての要素を一度に取得
    step_start = time.time()
    all_elements = list(soup.find_all(True))
    times["1_全要素取得"] = time.time() - step_start
    
    # 2. 要素の処理
    step_start = time.time()
    for element in all_elements:
        if element.decomposed:
            continue
        
        if element.name in ['script', 'style', 'meta', 'link', 'noscript']:
            element.decompose()
            continue
        
        if element.name == 'script' and element.get('type') == 'application/ld+json':
            element.decompose()
            continue
        
        if element.name in ['div', 'span'] and not element.get_text(strip=True):
            element.decompose()
            continue
        
        if element.attrs:
            has_data_attr = any(attr.startswith('data-') for attr in element.attrs)
            if has_data_attr:
                # 直接の子要素のみをチェック
                has_important_children = False
                for child in element.children:
                    if hasattr(child, 'name') and child.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']:
                        has_important_children = True
                        break
                
                if not has_important_children:
                    element.decompose()
                    continue
            
        if element.attrs and 'style' in element.attrs:
            del element['style']
    times["2_要素処理"] = time.time() - step_start
    
    # 3. コメントの削除
    step_start = time.time()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    times["3_コメント削除"] = time.time() - step_start
    
    # 終了時間を記録
    end_time = time.time()
    total_time = end_time - start_time
    times["total"] = total_time
    
    return times

# 元の実装の最適化版: 各ステップを最適化
def optimized_original(soup):
    # 開始時間を記録
    start_time = time.time()
    
    # 各ステップの時間を計測
    times = {}
    
    # 1. script, style, meta, link タグを削除
    step_start = time.time()
    for tag in soup.find_all(['script', 'style', 'meta', 'link', 'noscript']):
        tag.decompose()
    times["1_常に削除する要素"] = time.time() - step_start
    
    # 2. コメントを削除
    step_start = time.time()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    times["2_コメント削除"] = time.time() - step_start
    
    # 3. JSON-LDを含むscriptタグを削除
    step_start = time.time()
    for tag in soup.find_all('script', type='application/ld+json'):
        tag.decompose()
    times["3_JSON-LD削除"] = time.time() - step_start
    
    # 4. 空のdiv, span要素を削除
    step_start = time.time()
    for tag in soup.find_all(['div', 'span']):
        if not tag.get_text(strip=True):
            tag.decompose()
    times["4_空要素削除"] = time.time() - step_start
    
    # 5. データ属性を含む要素を削除 - 最適化版
    step_start = time.time()
    # データ属性を持つ要素を一度に取得
    data_attr_elements = soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs) if tag.attrs else False)
    for tag in data_attr_elements:
        # 直接の子要素のみをチェック（最適化）
        has_important_children = False
        for child in tag.children:
            if hasattr(child, 'name') and child.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']:
                has_important_children = True
                break
        
        if not has_important_children:
            tag.decompose()
    times["5_データ属性要素削除"] = time.time() - step_start

    # 6. インラインスタイルを削除
    step_start = time.time()
    for tag in soup.find_all(style=True):
        del tag['style']
    times["6_インラインスタイル削除"] = time.time() - step_start
    
    # 終了時間を記録
    end_time = time.time()
    total_time = end_time - start_time
    times["total"] = total_time
    
    return times

def main():
    html_contents = get_test_html()
    if not html_contents:
        print("テスト用のHTMLを取得できませんでした。")
        return
    
    html = html_contents[0]  # 最初のHTMLを使用
    
    # 各実装の実行時間を測定
    implementations = {
        "元の実装": original_remove_unwanted_elements,
        "現在の実装": current_remove_unwanted_elements,
        "改善案 (直接の子要素)": improved_direct_children,
        "最適化版元実装": optimized_original
    }
    
    # 各実装の各ステップの平均時間を記録
    all_results = {}
    
    # 各実装を複数回テスト
    num_tests = 5
    for name, func in implementations.items():
        print(f"\n{name}のテスト:")
        
        # 各ステップの時間を集計
        step_times = {}
        total_times = []
        
        for i in range(num_tests):
            soup = BeautifulSoup(html, 'html.parser')
            times = func(soup)
            
            # 合計時間を記録
            total_times.append(times["total"])
            print(f"  実行 {i+1}: {times['total']:.4f}秒")
            
            # 各ステップの時間を集計
            for step, time_value in times.items():
                if step != "total":
                    if step not in step_times:
                        step_times[step] = []
                    step_times[step].append(time_value)
        
        # 平均時間を計算
        avg_total = statistics.mean(total_times)
        avg_steps = {step: statistics.mean(times) for step, times in step_times.items()}
        
        # 結果を保存
        all_results[name] = {
            "total": avg_total,
            "steps": avg_steps
        }
        
        # 各ステップの平均時間を表示
        print(f"  平均実行時間: {avg_total:.4f}秒")
        print("  各ステップの平均時間:")
        for step, avg_time in avg_steps.items():
            print(f"    {step}: {avg_time:.4f}秒 ({avg_time/avg_total*100:.1f}%)")
    
    # 結果の比較
    print("\n===== 結果サマリー =====")
    for name, results in all_results.items():
        print(f"{name}: {results['total']:.4f}秒")
    
    # 元の実装との比較
    original_time = all_results["元の実装"]["total"]
    for name, results in all_results.items():
        if name != "元の実装":
            improvement = (original_time - results["total"]) / original_time * 100
            print(f"元の実装からの改善率 ({name}): {improvement:.2f}%")
    
    # 最も時間がかかっているステップを特定
    print("\n===== 各実装の最も時間がかかっているステップ =====")
    for name, results in all_results.items():
        steps = results["steps"]
        if steps:
            slowest_step = max(steps.items(), key=lambda x: x[1])
            print(f"{name}: {slowest_step[0]} ({slowest_step[1]:.4f}秒, 全体の{slowest_step[1]/results['total']*100:.1f}%)")

if __name__ == "__main__":
    main() 