import time
import cProfile
import pstats
import io
from src.web_scraping import WebScraper
from bs4 import BeautifulSoup, NavigableString, Comment
import re
from urllib.parse import urlparse
from datetime import datetime

# 変更前のクラス（リストをその場で定義）
class OriginalWebScraper(WebScraper):
    def __init__(self, verify_ssl=True):
        super().__init__(verify_ssl)
        
    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """
        不要なHTML要素を削除します。（変更前の実装）
        """
        # script, style, meta, link タグを削除
        for tag in soup.find_all(['script', 'style', 'meta', 'link', 'noscript']):
            tag.decompose()
            
        # コメントを削除
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
        for tag in soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs)):
            if not any(child.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li'] for child in tag.find_all()):
                tag.decompose()
                
        # インラインスタイルを削除
        for tag in soup.find_all(style=True):
            del tag['style']
            
    def _parse_node(self, node, current_depth=0, max_depth=10):
        # 最大深度に達した場合、Noneを返して要素を削除
        if current_depth >= max_depth:
            return None

        # テキストノードの場合
        if isinstance(node, NavigableString):
            if isinstance(node, Comment):
                return ""
                
            text = str(node).strip()
            
            # 技術的なコンテンツを含む文字列を除外
            if any(pattern in text.lower() for pattern in [
                'function', 'var ', 'const ', 'let ', '=>', 
                '{', '}', 'window.', 'document.',
                '<script', '<style', '@media', 
                'gtag', 'dataLayer', 'hbspt', 'hsVars'
            ]):
                return ""
                
            # URLやパスのみの文字列を除外
            if re.match(r'^https?://|^/[a-zA-Z0-9/]', text):
                return ""
                
            # 記号で始まり記号で終わる要素を除外
            if self.exclude_symbol_semicolon and re.match(r'^[^\w\s].*?[^\w\s]$', text):
                return ""
                
            # 文字化けした要素を除外
            if self.exclude_garbled and self._is_garbled_text(text):
                return ""
                
            return text

        # 要素ノードの場合
        # リンク除外オプションが有効で、aタグの場合はスキップ
        if self.exclude_links and node.name == "a":
            return ""
            
        # 不要なタグの場合はスキップ
        if node.name in ["script", "style", "meta", "link", "noscript"]:
            return ""
            
        # 以下は元のコードと同じなので省略
        return super()._parse_node(node, current_depth, max_depth)
        
    def json_to_markdown(self, json_data, level=0):
        # 文字列の場合はそのまま返す
        if isinstance(json_data, str):
            return json_data

        result = []
        tag = json_data["tag"]
        attrs = json_data["attributes"]
        children = json_data["children"]

        # 特定のタグに応じたMarkdown要素を生成
        if tag == "h1":
            prefix = "# "
        elif tag == "h2":
            prefix = "## "
        elif tag == "h3":
            prefix = "### "
        elif tag == "h4":
            prefix = "#### "
        elif tag == "h5":
            prefix = "##### "
        elif tag == "h6":
            prefix = "###### "
        elif tag == "p":
            prefix = ""
        elif tag == "a":
            href = attrs.get("href", "")
            # リンクの子要素を処理
            child_texts = [
                text for text in (self.json_to_markdown(child, level + 1) for child in children)
                if text.strip()
            ]
            child_text = " ".join(child_texts)
            return f"[{child_text}]({href})" if child_text else ""
        elif tag == "ul":
            prefix = ""
        elif tag == "ol":
            prefix = ""
        elif tag == "li":
            prefix = "- "
        elif tag == "strong" or tag == "b":
            child_texts = [
                text for text in (self.json_to_markdown(child, level) for child in children)
                if text.strip()
            ]
            child_text = " ".join(child_texts)
            return f"**{child_text}**" if child_text else ""
        elif tag == "em" or tag == "i":
            child_texts = [
                text for text in (self.json_to_markdown(child, level) for child in children)
                if text.strip()
            ]
            child_text = " ".join(child_texts)
            return f"*{child_text}*" if child_text else ""
        elif tag == "code":
            child_texts = [
                text for text in (self.json_to_markdown(child, level) for child in children)
                if text.strip()
            ]
            child_text = " ".join(child_texts)
            return f"`{child_text}`" if child_text else ""
        elif tag == "pre":
            child_texts = [
                text for text in (self.json_to_markdown(child, level) for child in children)
                if text.strip()
            ]
            child_text = " ".join(child_texts)
            return f"```\n{child_text}\n```" if child_text else ""
        elif tag == "br":
            return "\n"
        else:
            prefix = ""

        # 子要素を処理
        for child in children:
            child_text = self.json_to_markdown(child, level + 1)
            if child_text:
                if prefix and not child_text.startswith(prefix):
                    result.append(prefix + child_text)
                else:
                    result.append(child_text)

        # 結果を結合
        markdown = "\n".join(result)

        # リストアイテムの場合、インデントを追加
        if tag in ["li"]:
            markdown = "  " * level + markdown

        # 段落やヘッダーの後に空行を追加
        if tag in ["p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol"]:
            markdown += "\n"

        # 見出しの場合、内容が空でないことを確認
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            content = "".join(result).strip()
            if not content or content in ["#", "##", "###", "####", "#####", "######"]:
                return ""

        return markdown
        
    def _clean_markdown(self, markdown: str) -> str:
        """
        Markdownテキストを整形します。（変更前の実装）
        """
        # 連続する改行を1つの改行に置換
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # 行ごとに処理
        lines = markdown.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            # 連続する空白を4つまでに制限
            # 行頭のインデントは保持
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            content = line[len(indent):]
            
            # インデントは8スペースまで許可（タブ2個相当）
            if len(indent) > 4:
                indent = indent[:4]
                
            # 行の内容の連続空白を4つまでに制限
            content = re.sub(r' {4,}', '    ', content)
            line = indent + content
            
            # 空白のみの行をスキップ
            if not line.strip():
                # 前後の行をチェックして、必要な場合のみ空行を保持
                prev_line = cleaned_lines[-1] if cleaned_lines else ""
                next_line = lines[i+1] if i+1 < len(lines) else ""
                
                # 段落区切りとして必要な場合のみ空行を追加
                # 前の行が見出しや段落で、次の行にも内容がある場合
                if (prev_line.strip().startswith('#') or 
                    prev_line.strip()) and next_line.strip():
                    cleaned_lines.append("")
                continue
                
            # 見出し行の場合
            if re.match(r'^#{1,6}\s*$', line.strip()):
                # 次の非空行までチェック
                next_non_empty = None
                for next_line in lines[i+1:]:
                    if next_line.strip():
                        next_non_empty = next_line
                        break
                
                # 次の非空行が見出しの場合、現在の見出しをスキップ
                if next_non_empty and re.match(r'^#{1,6}', next_non_empty.strip()):
                    continue
            
            cleaned_lines.append(line)
        
        # 最後の空行を削除
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)
        
    def save_results(self, result: dict, url: str, output_dir: str, save_json: bool = True, save_markdown: bool = True) -> tuple:
        """
        スクレイピング結果を保存します。（変更前の実装）
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # URLを安全なファイル名に変換
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path.replace('/', '_')
        if path:
            safe_name = f"{domain}{path}"
        else:
            safe_name = domain
            
        # 不正な文字を除去
        safe_name = re.sub(r'[<>:"/\\|?*\s]', '_', safe_name)
        # 長すぎるファイル名を防ぐ
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
            
        # 以下は元のコードと同じなので省略
        return super().save_results(result, url, output_dir, save_json, save_markdown)

# テスト用のHTMLデータ
TEST_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>テストページ</title>
    <style>
        body { font-family: Arial, sans-serif; }
    </style>
    <script>
        function test() { console.log('test'); }
    </script>
</head>
<body>
    <header>
        <h1>テストウェブページ</h1>
        <nav>
            <ul>
                <li><a href="/">ホーム</a></li>
                <li><a href="/about">会社概要</a></li>
                <li><a href="/contact">お問い合わせ</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section>
            <h2>セクション1</h2>
            <p>これはテスト用の段落です。<strong>重要な部分</strong>と<em>強調部分</em>があります。</p>
            <div data-test="test">
                <p>データ属性を持つdiv内のテキスト</p>
            </div>
        </section>
        <section>
            <h2>セクション2</h2>
            <p>これは2つ目のセクションです。</p>
            <ul>
                <li>リストアイテム1</li>
                <li>リストアイテム2</li>
                <li>リストアイテム3</li>
            </ul>
        </section>
        <section>
            <h2>セクション3</h2>
            <p>これは3つ目のセクションです。</p>
            <pre><code>function example() {
  console.log('コードブロックの例');
}</code></pre>
        </section>
    </main>
    <footer>
        <p>&copy; 2023 テスト会社</p>
    </footer>
    <script>
        // コメント
        console.log('ページが読み込まれました');
    </script>
</body>
</html>
"""

# 大きなHTMLを生成（パフォーマンス差を明確にするため）
def generate_large_html(base_html, repeat=50):
    soup = BeautifulSoup(base_html, 'html.parser')
    main = soup.find('main')
    
    # mainタグ内のコンテンツを複製
    original_content = main.decode_contents()
    main.clear()
    
    # 指定回数だけコンテンツを複製
    for i in range(repeat):
        main.append(BeautifulSoup(original_content, 'html.parser'))
    
    return str(soup)

def run_benchmark():
    print("WebScraperクラスのパフォーマンス比較テスト")
    print("=" * 50)
    
    # 大きなHTMLを生成
    large_html = generate_large_html(TEST_HTML)
    print(f"テストHTMLサイズ: {len(large_html)} バイト")
    
    # 変更前のクラスでテスト
    original_scraper = OriginalWebScraper()
    
    # 変更後のクラスでテスト
    optimized_scraper = WebScraper()
    
    # 実行時間を測定する関数
    def measure_execution_time(func, *args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    # プロファイリングを行う関数
    def profile_function(func, *args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # 上位20件の結果を表示
        return result, s.getvalue()
    
    print("\n1. HTML解析のパフォーマンス比較")
    print("-" * 50)
    
    # 変更前のクラスでHTML解析
    _, original_time = measure_execution_time(original_scraper.html_to_json, large_html)
    print(f"変更前: {original_time:.6f} 秒")
    
    # 変更後のクラスでHTML解析
    _, optimized_time = measure_execution_time(optimized_scraper.html_to_json, large_html)
    print(f"変更後: {optimized_time:.6f} 秒")
    
    # 改善率を計算
    improvement = (original_time - optimized_time) / original_time * 100
    print(f"改善率: {improvement:.2f}%")
    
    print("\n2. 正規表現処理のパフォーマンス比較")
    print("-" * 50)
    
    # テスト用のテキスト生成（正規表現処理の差を明確にするため）
    test_text = """
    これはテスト用のテキストです。
    
    
    
    連続した改行があります。
    
    URLやパスの例: https://example.com や /path/to/file
    
    記号で始まり記号で終わる例: [これは括弧で囲まれています]
    
    連続したスペースの例:    これは    スペースが    多いテキストです。
    
    # 見出し1
    ## 見出し2
    ### 見出し3
    
    不正なファイル名文字: test<>:"/\|?*
    """
    
    # 変更前の正規表現処理
    def original_regex_process(text):
        # URLパターンマッチ
        url_match = re.match(r'^https?://|^/[a-zA-Z0-9/]', text)
        
        # 記号パターンマッチ
        symbol_match = re.match(r'^[^\w\s].*?[^\w\s]$', text)
        
        # 連続改行の置換
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # インデントパターンマッチ
        indent_match = re.match(r'^(\s*)', text)
        
        # 連続スペースの置換
        text = re.sub(r' {4,}', '    ', text)
        
        # 見出しパターンマッチ
        heading_match = re.match(r'^#{1,6}\s*$', text)
        
        # 見出し開始パターンマッチ
        heading_start = re.match(r'^#{1,6}', text)
        
        # 不正ファイル名文字の置換
        text = re.sub(r'[<>:"/\\|?*\s]', '_', text)
        
        return text
    
    # 変更後の正規表現処理
    def optimized_regex_process(text):
        # URLパターンマッチ
        url_match = optimized_scraper.URL_PATH_PATTERN.match(text)
        
        # 記号パターンマッチ
        symbol_match = optimized_scraper.SYMBOL_SEMICOLON_PATTERN.match(text)
        
        # 連続改行の置換
        text = optimized_scraper.CONSECUTIVE_NEWLINES_PATTERN.sub('\n\n', text)
        
        # インデントパターンマッチ
        indent_match = optimized_scraper.INDENT_PATTERN.match(text)
        
        # 連続スペースの置換
        text = optimized_scraper.CONSECUTIVE_SPACES_PATTERN.sub('    ', text)
        
        # 見出しパターンマッチ
        heading_match = optimized_scraper.HEADING_ONLY_PATTERN.match(text)
        
        # 見出し開始パターンマッチ
        heading_start = optimized_scraper.HEADING_START_PATTERN.match(text)
        
        # 不正ファイル名文字の置換
        text = optimized_scraper.INVALID_FILENAME_CHARS_PATTERN.sub('_', text)
        
        return text
    
    # 正規表現処理の実行時間を測定（繰り返し実行して差を明確に）
    iterations = 10000
    
    # 変更前の正規表現処理
    start_time = time.time()
    for _ in range(iterations):
        original_regex_process(test_text)
    original_regex_time = time.time() - start_time
    print(f"変更前の正規表現処理 ({iterations}回): {original_regex_time:.6f} 秒")
    
    # 変更後の正規表現処理
    start_time = time.time()
    for _ in range(iterations):
        optimized_regex_process(test_text)
    optimized_regex_time = time.time() - start_time
    print(f"変更後の正規表現処理 ({iterations}回): {optimized_regex_time:.6f} 秒")
    
    # 正規表現処理の改善率
    regex_improvement = (original_regex_time - optimized_regex_time) / original_regex_time * 100
    print(f"正規表現処理の改善率: {regex_improvement:.2f}%")
    
    print("\n3. メモリ使用量の比較")
    print("-" * 50)
    
    # メモリ使用量を測定する関数（簡易版）
    def measure_memory_usage(func, *args, **kwargs):
        import tracemalloc
        
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return result, current / 1024, peak / 1024  # KB単位で返す
    
    # 変更前のクラスのメモリ使用量
    _, original_current, original_peak = measure_memory_usage(original_scraper.html_to_json, large_html)
    print(f"変更前: 現在のメモリ使用量 {original_current:.2f} KB, ピーク時 {original_peak:.2f} KB")
    
    # 変更後のクラスのメモリ使用量
    _, optimized_current, optimized_peak = measure_memory_usage(optimized_scraper.html_to_json, large_html)
    print(f"変更後: 現在のメモリ使用量 {optimized_current:.2f} KB, ピーク時 {optimized_peak:.2f} KB")
    
    # メモリ使用量の改善率
    memory_improvement = (original_peak - optimized_peak) / original_peak * 100
    print(f"メモリ使用量の改善率: {memory_improvement:.2f}%")
    
    print("\n4. 繰り返し実行時のパフォーマンス比較")
    print("-" * 50)
    
    # 繰り返し実行時の平均実行時間を測定
    iterations = 5
    original_times = []
    optimized_times = []
    
    for i in range(iterations):
        _, time_taken = measure_execution_time(original_scraper.html_to_json, large_html)
        original_times.append(time_taken)
    
    for i in range(iterations):
        _, time_taken = measure_execution_time(optimized_scraper.html_to_json, large_html)
        optimized_times.append(time_taken)
    
    avg_original = sum(original_times) / len(original_times)
    avg_optimized = sum(optimized_times) / len(optimized_times)
    
    print(f"変更前 (平均 {iterations}回): {avg_original:.6f} 秒")
    print(f"変更後 (平均 {iterations}回): {avg_optimized:.6f} 秒")
    
    avg_improvement = (avg_original - avg_optimized) / avg_original * 100
    print(f"平均改善率: {avg_improvement:.2f}%")
    
    print("\n5. 結論")
    print("-" * 50)
    
    if avg_improvement > 0 or regex_improvement > 0:
        print(f"最適化によるパフォーマンス向上が見られました：")
        print(f"- 全体処理: 平均 {avg_improvement:.2f}% の改善")
        print(f"- 正規表現処理: {regex_improvement:.2f}% の改善")
        print("これは主に以下の理由によるものです：")
        print("1. リストの再作成によるメモリ割り当てのオーバーヘッドの削減")
        print("2. 正規表現パターンの事前コンパイルによる処理速度の向上")
        print("3. ガベージコレクションの負荷の軽減")
    else:
        print("最適化による顕著なパフォーマンス向上は見られませんでした。")
        print("これは以下の理由が考えられます：")
        print("1. テストデータが小さすぎる可能性がある")
        print("2. Pythonの最適化により、オーバーヘッドが最小化されている")
    
    print("\n最終的な推奨事項:")
    if regex_improvement > 20:
        print("正規表現パターンの事前コンパイルは、特に繰り返し使用される場合に大きなパフォーマンス向上をもたらします。")
        print("これは必ず実装すべき最適化です。")
    elif regex_improvement > 0:
        print("正規表現パターンの事前コンパイルは、わずかなパフォーマンス向上をもたらします。")
        print("コードの可読性を損なわない範囲で実装することをお勧めします。")
    else:
        print("正規表現パターンの事前コンパイルによる顕著なパフォーマンス向上は見られませんでしたが、")
        print("大規模なデータセットや高頻度の処理では効果が現れる可能性があります。")

if __name__ == "__main__":
    run_benchmark() 