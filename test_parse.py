import pytest
from extract import parse_json, validate

def test_validate_ok():
    data = {"name": "张三", "gender": "男", "birth_year": 1990, "email": "a@b.com"}
    validate(data)          # 不该抛异常

def test_validate_missing_key():
    data = {"name": "张三"}         # 缺字段
    with pytest.raises(ValueError):
        validate(data)

def test_validate_chinese_keys():
    data = {"姓名": "张三", "性别": "男", "出生年份": 1990, "邮箱": "a@b.com"}
    with pytest.raises(ValueError):
        validate(data)

def test_pure_json():
    # 情况1：纯 JSON，应该过
    reply = '{"name": "张三"}'
    assert parse_json(reply)["name"] == "张三"

def test_with_code_block():
    # 情况2：带代码块包裹
    reply = '```json\n{"name": "张三"}\n```'
    # TODO: 你期望它怎样？先让它跑，看报什么错
    assert parse_json(reply)["name"] == "张三"

def test_with_explanation():
    # 情况3：前后有说明文字
    reply = '好的，结果如下：{"name": "张三"}。以上。'
    assert parse_json(reply)["name"] == "张三"