from config import API_KEY, API_URL

def test_api_key_loaded():
    assert API_KEY is not None,"API_KEY 没有加载成功，请检查 .env 文件"

def test_api_url_correct():
    assert API_URL == "https://api.deepseek.com/chat/completions"