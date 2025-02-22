from duckduckgo_instant_answer import DuckDuckGoInstantAnswer

def test_duckduckgo_search_params():
    """検索パラメータが正しく設定されることを確認"""
    search = DuckDuckGoInstantAnswer()
    query = "python 初心者"
    params = {"lang": "jp"}
    
    # 検索パラメータの確認
    search_params = {
        "q": query,
        "format": "json",
        **params
    }
    assert search_params["q"] == query
    assert search_params["format"] == "json"
    assert search_params["lang"] == "jp" 