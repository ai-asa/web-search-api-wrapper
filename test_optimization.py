import time
import requests
from bs4 import BeautifulSoup, Comment
import statistics

# テスト用のHTMLを取得する関数
def get_test_html():
    # 大きめのウェブページを取得
    urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://www.bbc.com/news",
        "https://github.com/about"
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
    
    # script, style, meta, link タグを削除
    for tag in soup.find_all(['script', 'style', 'meta', 'link', 'noscript']):
        tag.decompose()
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
        
    # JSON-LDを含むscriptタグを削除
    for tag in soup.find_all('script', type='application/ld+json'):
        tag.decompose()
    # 空のdiv, span要素を削除
    for tag in soup.find_all(['div', 'span']):
        if not tag.get_text(strip=True):
            tag.decompose()
            
    # データ属性を含む要素を削除
    for tag in soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs) if tag.attrs else False):
        if not any(child.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li'] for child in tag.find_all()):
            tag.decompose()

    # インラインスタイルを削除
    for tag in soup.find_all(style=True):
        del tag['style']
    
    # 終了時間を記録
    end_time = time.time()
    return end_time - start_time

# 現在の実装
def current_remove_unwanted_elements(soup):
    # 開始時間を記録
    start_time = time.time()
    
    # 全ての要素を一度に取得し、ストリーム的に処理
    for element in soup.find_all(True):  # Trueを指定することで全てのタグを取得
        # 要素が既に削除されている場合はスキップ
        if element.decomposed:
            continue
        
        # 1. 常に削除する要素（script, style, meta, link, noscript）
        if element.name in ['script', 'style', 'meta', 'link', 'noscript']:
            element.decompose()
            continue
        
        # 2. JSON-LDを含むscriptタグ
        if element.name == 'script' and element.get('type') == 'application/ld+json':
            element.decompose()
            continue
        
        # 3. 空のdiv, span要素
        if element.name in ['div', 'span'] and not element.get_text(strip=True):
            element.decompose()
            continue
        
        # 4. データ属性を含む要素（ただし、特定のタグを含む場合は保持）
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
            
        # 5. インラインスタイルの削除（要素自体は保持）
        if element.attrs and 'style' in element.attrs:
            del element['style']
        
    # コメントの削除（コメントはタグではないため、別途処理）
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # 終了時間を記録
    end_time = time.time()
    return end_time - start_time

# 提案された改善実装
def improved_remove_unwanted_elements(soup):
    # 開始時間を記録
    start_time = time.time()
    
    # 全ての要素を一度に取得し、ストリーム的に処理
    for element in soup.find_all(True):  # Trueを指定することで全てのタグを取得
        # 要素が既に削除されている場合はスキップ
        if element.decomposed:
            continue
        
        # 1. 常に削除する要素（script, style, meta, link, noscript）
        if element.name in ['script', 'style', 'meta', 'link', 'noscript']:
            element.decompose()
            continue
        
        # 2. JSON-LDを含むscriptタグ
        if element.name == 'script' and element.get('type') == 'application/ld+json':
            element.decompose()
            continue
        
        # 3. 空のdiv, span要素
        if element.name in ['div', 'span'] and not element.get_text(strip=True):
            element.decompose()
            continue
        
        # 4. データ属性を含む要素（ただし、特定のタグを含む場合は保持）
        if element.attrs:  # 属性が存在する場合のみチェック
            has_data_attr = any(attr.startswith('data-') for attr in element.attrs)
            if has_data_attr:
                # 特定のタグを含むかチェック - 改善版: select_oneを使用
                has_important_children = bool(element.select_one('p, h1, h2, h3, h4, h5, h6, ul, ol, li'))
                if not has_important_children:
                    element.decompose()
                    continue
            
        # 5. インラインスタイルの削除（要素自体は保持）
        if element.attrs and 'style' in element.attrs:
            del element['style']
        
    # コメントの削除（コメントはタグではないため、別途処理）
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # 終了時間を記録
    end_time = time.time()
    return end_time - start_time

def main():
    html_contents = get_test_html()
    if not html_contents:
        print("テスト用のHTMLを取得できませんでした。")
        return
    
    print(f"テスト対象のHTMLファイル数: {len(html_contents)}")
    
    # 各実装の実行時間を記録
    original_times = []
    current_times = []
    improved_times = []
    
    # 各HTMLに対してテストを実行
    for i, html in enumerate(html_contents):
        print(f"\nHTMLファイル {i+1} のテスト:")
        
        # 各実装を複数回テストして平均を取る
        num_tests = 5
        for j in range(num_tests):
            # 元の実装
            soup = BeautifulSoup(html, 'html.parser')
            time_original = original_remove_unwanted_elements(soup)
            original_times.append(time_original)
            
            # 現在の実装
            soup = BeautifulSoup(html, 'html.parser')
            time_current = current_remove_unwanted_elements(soup)
            current_times.append(time_current)
            
            # 改善された実装
            soup = BeautifulSoup(html, 'html.parser')
            time_improved = improved_remove_unwanted_elements(soup)
            improved_times.append(time_improved)
            
            print(f"  テスト {j+1}: 元の実装: {time_original:.4f}秒, 現在の実装: {time_current:.4f}秒, 改善実装: {time_improved:.4f}秒")
    
    # 結果の集計
    avg_original = statistics.mean(original_times)
    avg_current = statistics.mean(current_times)
    avg_improved = statistics.mean(improved_times)
    
    print("\n===== 結果サマリー =====")
    print(f"元の実装の平均実行時間: {avg_original:.4f}秒")
    print(f"現在の実装の平均実行時間: {avg_current:.4f}秒")
    print(f"改善実装の平均実行時間: {avg_improved:.4f}秒")
    
    # 改善率の計算
    improvement_current = (avg_original - avg_current) / avg_original * 100
    improvement_improved = (avg_original - avg_improved) / avg_original * 100
    improvement_from_current = (avg_current - avg_improved) / avg_current * 100
    
    print(f"元の実装からの改善率 (現在の実装): {improvement_current:.2f}%")
    print(f"元の実装からの改善率 (改善実装): {improvement_improved:.2f}%")
    print(f"現在の実装からの改善率 (改善実装): {improvement_from_current:.2f}%")

if __name__ == "__main__":
    main() 