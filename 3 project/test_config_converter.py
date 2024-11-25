import pytest
from config_converter import ConfigConverter

def test_validate_name():
    converter = ConfigConverter()
    assert converter.validate_name("valid_name") == True
    assert converter.validate_name("Valid_Name123") == True
    assert converter.validate_name("_name") == True
    assert converter.validate_name("123name") == False
    assert converter.validate_name("invalid-name") == False
    assert converter.validate_name("") == False

def test_process_value():
    converter = ConfigConverter()
    assert converter.process_value(42) == "42"
    assert converter.process_value(3.14) == "3.14"
    with pytest.raises(ValueError):
        converter.process_value("string")

def test_convert_dict():
    converter = ConfigConverter()
    input_data = {
        "name": 42,
        "nested": {"inner": 123}
    }
    expected = """table([
    name = 42,
    nested = table([
    inner = 123,
]),
])"""
    assert converter.convert_dict(input_data).replace(" ", "") == expected.replace(" ", "")

def test_process_constants():
    converter = ConfigConverter()
    input_data = {
        "__constants__": {
            "MAX_VALUE": 100,
            "SETTINGS": {"timeout": 30}
        },
        "other_data": 42
    }
    expected = """def MAX_VALUE := 100;
def SETTINGS := table([
    timeout = 30,
]);
"""
    result = converter.process_constants(input_data)
    assert result.replace(" ", "") == expected.replace(" ", "")
    assert "other_data" in input_data
    assert "__constants__" not in input_data

def test_invalid_name():
    converter = ConfigConverter()
    with pytest.raises(ValueError):
        converter.convert_dict({"123invalid": 42})

def test_nested_structures():
    converter = ConfigConverter()
    input_data = {
        "level1": {
            "level2": {
                "level3": 42
            }
        }
    }
    result = converter.convert(input_data)
    assert "level1" in result
    assert "level2" in result
    assert "level3" in result
    assert "42" in result

def test_full_conversion():
    converter = ConfigConverter()
    input_data = {
        "__constants__": {
            "MAX_RETRY": 3
        },
        "server": {
            "port": 8080,
            "settings": {
                "timeout": 30
            }
        }
    }
    result = converter.convert(input_data)
    assert "def MAX_RETRY := 3;" in result
    assert "server" in result
    assert "port = 8080" in result
    assert "timeout = 30" in result
