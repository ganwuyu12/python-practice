from unittest.mock import patch, Mock

# 假设你有个函数，它会真的发请求
def real_call():
    import requests
    return requests.post("https://api.example.com").json()

# 测试它，但不真发请求
@patch("requests.post")
def test_real_call(mock_post):
    # 让 requests.post 返回一个假对象
    mock_post.return_value = Mock(json=lambda: {"result": "假的回复"})

    # 调用 real_call，它以为自己在发请求，其实用的是假对象
    result = real_call()
    print(result)      # {'result': '假的回复'}

test_real_call()