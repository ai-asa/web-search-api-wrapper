import pytest
from bing_web_search import BingWebSearch

def test_bing_search_missing_credentials():
    """APIキーが不足している場合にValueErrorが発生することを確認"""
    with pytest.raises(ValueError):
        BingWebSearch(api_key=None)

def test_bing_search_with_credentials():
    """APIキーが正しく設定されることを確認"""
    api_key = "test_api_key"
    search = BingWebSearch(api_key=api_key)
    assert search.api_key == api_key 