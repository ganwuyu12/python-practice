from unittest.mock import patch, Mock
import pytest
import requests
from client import chat


def _fake_response(status_code=200, payload=None):
    resp = Mock()
    resp.status_code = status_code
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(f"{status_code}")
    else:
        resp.raise_for_status.return_value = None
        resp.json.return_value = payload or {
            "choices": [{"message": {"content": "你好呀"}}]
        }
    return resp


@patch("client.requests.post")
def test_chat_success(mock_post):
    mock_post.return_value = _fake_response()
    result = chat([{"role": "user", "content": "你好"}])
    assert result == "你好呀"


@patch("client.requests.post")
def test_chat_400_does_not_retry(mock_post):
    mock_post.return_value = _fake_response(status_code=400)
    chat([{"role": "user", "content": "x"}])
    assert mock_post.call_count == 1      # 4xx 不重试，只调一次


@patch("client.requests.post")
def test_chat_429_retries(mock_post):
    mock_post.return_value = _fake_response(status_code=429)
    chat([{"role": "user", "content": "x"}], max_retries=3)
    assert mock_post.call_count == 3      # 429 重试，调三次