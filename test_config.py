import os
import pytest
from config import API_KEY, API_URL


@pytest.mark.skipif(API_KEY is None, reason="没有 .env，跳过")
def test_api_key_loaded():
    assert API_KEY is not None


def test_api_url_correct():
    assert API_URL == "https://api.deepseek.com/chat/completions"