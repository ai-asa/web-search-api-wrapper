import pytest
from google_custom_search import GoogleCustomSearch

def test_google_search_missing_credentials():
    """認証情報が不足している場合にValueErrorが発生することを確認"""
    with pytest.raises(ValueError):
        GoogleCustomSearch(api_key=None, cse_id=None)

def test_google_search_with_credentials():
    """認証情報が正しく設定されることを確認"""
    api_key = "test_api_key"
    cse_id = "test_cse_id"
    search = GoogleCustomSearch(api_key=api_key, cse_id=cse_id)
    assert search.api_key == api_key
    assert search.cse_id == cse_id 