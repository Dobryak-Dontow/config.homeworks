import os
import pytest
from src.transpiler import ConfigTranspiler

def test_transpiler_valid_input(tmp_path):
    input_file = tmp_path / "input.toml"
    output_file = tmp_path / "output.txt"

    # Пример TOML-файла
    input_file.write_text("""
    [example]
    key1 = 42
    key2 = 7
    """)

    # Ожидаемый результат
    expected_output = """table([
        example = table([
            key1 = 42,
            key2 = 7,
        ]),
    ])
    """

    transpiler = ConfigTranspiler(str(input_file), str(output_file))
    transpiler.transpile()

    # Сравниваем выходной результат с ожидаемым
    assert output_file.read_text().strip() == expected_output.strip()

def test_transpiler_invalid_name(tmp_path):
    input_file = tmp_path / "input.toml"
    output_file = tmp_path / "output.txt"

    # Пример неправильного TOML-файла
    input_file.write_text("""
    [example]
    123key = 42
    """)

    transpiler = ConfigTranspiler(str(input_file), str(output_file))
    with pytest.raises(ValueError, match="Некорректное имя ключа: 123key"):
        transpiler.transpile()
