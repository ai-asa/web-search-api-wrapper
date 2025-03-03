import time
import requests
from bs4 import BeautifulSoup, Comment
import statistics
import cProfile
import pstats
import io

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
    # script, style, meta, link タグを削除
    for tag in soup.find_all(['script', 'style', 'meta', 'link', 'noscript']):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
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

# 現在の実装
def current_remove_unwanted_elements(soup):
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
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

# 改善案1: select_oneを使用
def improved_select_one(soup):
    # 全ての要素を一度に取得し、ストリーム的に処理
    for element in soup.find_all(True):
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
                # select_oneを使用
                has_important_children = bool(element.select_one('p, h1, h2, h3, h4, h5, h6, ul, ol, li'))
                if not has_important_children:
                    element.decompose()
                    continue
            
        if element.attrs and 'style' in element.attrs:
            del element['style']
        
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

# 改善案2: 直接の子要素のみをチェック
def improved_direct_children(soup):
    # 全ての要素を一度に取得し、ストリーム的に処理
    for element in soup.find_all(True):
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
        
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

# 改善案3: データ属性の処理を最適化
def improved_data_attr_optimized(soup):
    # 全ての要素を一度に取得し、ストリーム的に処理
    for element in soup.find_all(True):
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
        
        # データ属性チェックを最適化
        if element.attrs:
            # 属性名のリストを一度だけ作成
            attr_names = list(element.attrs.keys())
            has_data_attr = any(attr.startswith('data-') for attr in attr_names)
            
            if has_data_attr:
                # 重要な子要素を探す - 最初に見つかったら即終了
                important_tags = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li'}
                has_important_children = False
                
                # 子要素を直接イテレート
                for child in element.find_all(important_tags, recursive=True, limit=1):
                    has_important_children = True
                    break
                    
                if not has_important_children:
                    element.decompose()
                    continue
            
        if element.attrs and 'style' in element.attrs:
            del element['style']
        
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

def profile_function(func_name, soup):
    # プロファイリング開始
    pr = cProfile.Profile()
    pr.enable()
    
    # 関数実行
    func_name(soup)
    
    # プロファイリング終了
    pr.disable()
    
    # 結果を文字列として取得
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # 上位20件の結果を表示
    
    return s.getvalue()

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
        "改善案1 (select_one)": improved_select_one,
        "改善案2 (直接の子要素)": improved_direct_children,
        "改善案3 (データ属性最適化)": improved_data_attr_optimized
    }
    
    results = {}
    
    for name, func in implementations.items():
        print(f"\n{name}のプロファイリング:")
        
        # 複数回実行して平均を取る
        times = []
        for i in range(5):
            soup = BeautifulSoup(html, 'html.parser')
            
            start_time = time.time()
            func(soup)
            end_time = time.time()
            
            times.append(end_time - start_time)
            print(f"  実行 {i+1}: {times[-1]:.4f}秒")
        
        avg_time = statistics.mean(times)
        results[name] = avg_time
        print(f"  平均実行時間: {avg_time:.4f}秒")
        
        # 詳細なプロファイリング（最後の実行のみ）
        soup = BeautifulSoup(html, 'html.parser')
        profile_result = profile_function(func, soup)
        print("\n詳細なプロファイリング結果:")
        print(profile_result[:500] + "...")  # 結果の一部のみ表示
    
    # 結果の比較
    print("\n===== 結果サマリー =====")
    for name, time_value in results.items():
        print(f"{name}: {time_value:.4f}秒")
    
    # 元の実装との比較
    original_time = results["元の実装"]
    for name, time_value in results.items():
        if name != "元の実装":
            improvement = (original_time - time_value) / original_time * 100
            print(f"元の実装からの改善率 ({name}): {improvement:.2f}%")

if __name__ == "__main__":
    main() 