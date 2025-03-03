import re
import time
import random
import string
from typing import List, Callable

# テスト用のテキストデータを生成する関数
def generate_test_texts(count: int, avg_length: int = 200) -> List[str]:
    texts = []
    for _ in range(count):
        # ランダムなテキストを生成（ASCII文字、日本語文字、特殊文字を含む）
        length = random.randint(avg_length // 2, avg_length * 2)
        
        # 基本的なASCII文字
        ascii_text = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation + ' \n\t') 
                            for _ in range(int(length * 0.6)))
        
        # 日本語文字（ひらがな、カタカナ、漢字の範囲からランダムに選択）
        japanese_chars = []
        for _ in range(int(length * 0.2)):
            # ひらがな、カタカナ、または漢字の範囲からランダムに文字を選択
            ranges = [
                (0x3040, 0x309F),  # ひらがな
                (0x30A0, 0x30FF),  # カタカナ
                (0x4E00, 0x9FFF),  # 漢字
            ]
            range_idx = random.randint(0, 2)
            start, end = ranges[range_idx]
            char_code = random.randint(start, end)
            japanese_chars.append(chr(char_code))
        
        japanese_text = ''.join(japanese_chars)
        
        # 特殊文字（文字化けを含む可能性のある文字）- 割合を増やす
        special_chars = []
        for _ in range(int(length * 0.2)):  # 20%に増加
            if random.random() < 0.2:  # 20%の確率で文字化けっぽい文字を入れる
                special_pattern = random.choice([
                    '\uFFFD',  # 無効なUnicode文字
                    chr(random.randint(0, 31)),  # 制御文字
                    chr(random.randint(0xD800, 0xDFFF)),  # サロゲートペア
                    'ã\\x' + ''.join(random.choice('0123456789ABCDEF') for _ in range(2)),  # 日本語文字化けパターン
                    '&#' + str(random.randint(0, 9999)) + ';',  # 数値文字参照
                    '%' + ''.join(random.choice('0123456789ABCDEF') for _ in range(2)),  # URLエンコード
                ])
                special_chars.append(special_pattern)
            else:
                special_chars.append(chr(random.randint(0x2000, 0x2FFF)))  # その他の特殊文字
        
        special_text = ''.join(special_chars)
        
        # すべてを結合してシャッフル
        combined = list(ascii_text + japanese_text + special_text)
        random.shuffle(combined)
        texts.append(''.join(combined))
    
    return texts

# 元の実装
class OriginalImplementation:
    def _is_garbled_text(self, text: str) -> bool:
        try:
            # 1. 制御文字のチェック（改行、タブ以外）
            if any(ord(c) < 32 and c not in '\n\t\r' for c in text):
                return True

            # 2. 文字化けパターンのチェック
            garbled_patterns = [
                r'[\uFFFD\uFFFE\uFFFF]',  # 無効なUnicode文字
                r'[\u0000-\u001F\u007F-\u009F]',  # 制御文字
                r'[\uD800-\uDFFF]',  # サロゲートペア
                r'ã[\\x80-\\xFF]+',  # 典型的な日本語文字化けパターン
                r'&#[0-9]+;',  # 数値文字参照
                r'%[0-9A-Fa-f]{2}',  # URLエンコード
            ]
            
            if any(re.search(pattern, text) for pattern in garbled_patterns):
                return True

            # 3. 日本語として不自然な文字列パターンのチェック
            japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))
            total_chars = len(text)
            
            if total_chars > 0 and japanese_chars > 0:
                # 日本語文字が含まれているが、不自然に断片化している場合
                if japanese_chars / total_chars < 0.1:  # 日本語文字の割合が10%未満
                    return True

            return False
        except UnicodeError:
            return True

# 最適化された実装
class OptimizedImplementation:
    def __init__(self):
        # 正規表現パターンをコンパイル
        self.GARBLED_PATTERNS = [
            re.compile(r'[\uFFFD\uFFFE\uFFFF]'),  # 無効なUnicode文字
            re.compile(r'[\u0000-\u001F\u007F-\u009F]'),  # 制御文字
            re.compile(r'[\uD800-\uDFFF]'),  # サロゲートペア
            re.compile(r'ã[\\x80-\\xFF]+'),  # 典型的な日本語文字化けパターン
            re.compile(r'&#[0-9]+;'),  # 数値文字参照
            re.compile(r'%[0-9A-Fa-f]{2}'),  # URLエンコード
        ]
        self.JAPANESE_CHARS_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
    
    def _is_garbled_text(self, text: str) -> bool:
        try:
            # 1. 制御文字のチェック（改行、タブ以外）
            if any(ord(c) < 32 and c not in '\n\t\r' for c in text):
                return True

            # 2. 文字化けパターンのチェック - コンパイル済みパターンを使用
            if any(pattern.search(text) for pattern in self.GARBLED_PATTERNS):
                return True

            # 3. 日本語として不自然な文字列パターンのチェック - コンパイル済みパターンを使用
            japanese_chars = len(self.JAPANESE_CHARS_PATTERN.findall(text))
            total_chars = len(text)
            
            if total_chars > 0 and japanese_chars > 0:
                # 日本語文字が含まれているが、不自然に断片化している場合
                if japanese_chars / total_chars < 0.1:  # 日本語文字の割合が10%未満
                    return True

            return False
        except UnicodeError:
            return True

# パフォーマンステスト関数
def run_performance_test(implementation: Callable, texts: List[str], iterations: int = 1) -> float:
    start_time = time.time()
    
    for _ in range(iterations):
        for text in texts:
            implementation(text)
    
    end_time = time.time()
    return end_time - start_time

# 正規表現の処理回数を増やすためのテスト
def run_regex_intensive_test():
    # 元の実装
    original = OriginalImplementation()
    
    # 最適化された実装
    optimized = OptimizedImplementation()
    
    # テスト用のテキスト - より複雑なケース
    test_texts = [
        "This is a test text with some Japanese characters: あいうえお漢字カタカナ and some garbled characters: \uFFFD &#1234; %2F ã\\x80",
        "完全な日本語テキスト with a few English words and some garbled chars: ã\\x9F &#9999; %FF",
        "Mixed text with lots of special characters: \u0001\u0002\u0003\uFFFD\uFFFE\uFFFF and some Japanese: 日本語文字列",
        "HTML-like text with entities: &lt;div&gt;&#1234;&#5678;&lt;/div&gt; and some URL encoded stuff: %20%3F%26",
        "Text with surrogate pairs: \uD800\uDC00\uD801\uDC01 and some control chars: \u0000\u001F\u007F\u009F"
    ]
    
    # 繰り返し回数
    iterations = 500000
    
    print(f"正規表現集中テスト: {len(test_texts)}種類のテキストを各{iterations}回処理")
    
    # 元の実装をテスト
    start_time = time.time()
    for _ in range(iterations):
        for text in test_texts:
            original._is_garbled_text(text)
    original_time = time.time() - start_time
    print(f"元の実装の実行時間: {original_time:.4f} 秒")
    
    # 最適化された実装をテスト
    start_time = time.time()
    for _ in range(iterations):
        for text in test_texts:
            optimized._is_garbled_text(text)
    optimized_time = time.time() - start_time
    print(f"最適化された実装の実行時間: {optimized_time:.4f} 秒")
    
    # 結果を表示
    print(f"速度向上率: {(original_time / optimized_time):.2f}倍")
    print(f"時間削減率: {((original_time - optimized_time) / original_time * 100):.2f}%")

if __name__ == "__main__":
    # 通常のテスト
    num_texts = 2000
    iterations = 20
    
    print("===== 通常のパフォーマンステスト =====")
    print(f"テキスト数: {num_texts}, 繰り返し回数: {iterations}")
    
    # テストデータを生成
    print("テストデータを生成中...")
    test_texts = generate_test_texts(num_texts)
    print(f"テストデータ生成完了: {len(test_texts)}テキスト")
    
    # 元の実装をテスト
    print("元の実装をテスト中...")
    original = OriginalImplementation()
    original_time = run_performance_test(original._is_garbled_text, test_texts, iterations)
    print(f"元の実装テスト完了: {original_time:.4f}秒")
    
    # 最適化された実装をテスト
    print("最適化された実装をテスト中...")
    optimized = OptimizedImplementation()
    optimized_time = run_performance_test(optimized._is_garbled_text, test_texts, iterations)
    print(f"最適化された実装テスト完了: {optimized_time:.4f}秒")
    
    # 結果を表示
    print("\n===== 通常のパフォーマンステスト結果 =====")
    print(f"元の実装の実行時間: {original_time:.4f} 秒")
    print(f"最適化された実装の実行時間: {optimized_time:.4f} 秒")
    print(f"速度向上率: {(original_time / optimized_time):.2f}倍")
    print(f"時間削減率: {((original_time - optimized_time) / original_time * 100):.2f}%")
    
    print("\n")
    
    # 正規表現集中テスト
    print("===== 正規表現集中テスト =====")
    run_regex_intensive_test() 