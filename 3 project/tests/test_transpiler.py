import unittest
import os
from src.transpiler import ConfigTranspiler


class TestConfigTranspiler(unittest.TestCase):
    def setUp(self):
        self.test_input = "test_input.toml"
        self.test_output = "test_output.txt"

    def tearDown(self):
        # Удаляем тестовые файлы после каждого теста
        for file in [self.test_input, self.test_output]:
            if os.path.exists(file):
                os.remove(file)

    def test_constant_resolution(self):
        # Создаем тестовый TOML файл
        with open(self.test_input, "w") as f:
            f.write('''
[constants]
const_def = "def MAX_VALUE := 100;"
value = "#(MAX_VALUE)"
            ''')

        transpiler = ConfigTranspiler(self.test_input, self.test_output)
        transpiler.transpile()

        with open(self.test_output, "r") as f:
            result = f.read()

        expected = '''table([
    constants = table([
        value = 100,
    ]),
])'''
        self.assertEqual(result.strip(), expected.strip())

    def test_nested_dictionaries(self):
        with open(self.test_input, "w") as f:
            f.write('''
[database]
host = "localhost"
port = 5432

[database.credentials]
username = "admin"
password = "secret"
            ''')

        transpiler = ConfigTranspiler(self.test_input, self.test_output)
        transpiler.transpile()

        with open(self.test_output, "r") as f:
            result = f.read()

        expected = '''table([
    database = table([
        host = "localhost",
        port = 5432,
        credentials = table([
            username = "admin",
            password = "secret",
        ]),
    ]),
])'''
        self.assertEqual(result.strip(), expected.strip())

    def test_invalid_name(self):
        with open(self.test_input, "w") as f:
            f.write('''
[test]
invalid-name = "value"
            ''')

        transpiler = ConfigTranspiler(self.test_input, self.test_output)
        with self.assertRaises(ValueError):
            transpiler.transpile()

    def test_undefined_constant(self):
        with open(self.test_input, "w") as f:
            f.write('''
[test]
value = "#(UNDEFINED_CONSTANT)"
            ''')

        transpiler = ConfigTranspiler(self.test_input, self.test_output)
        with self.assertRaises(ValueError):
            transpiler.transpile()

    def test_value_as_constant(self):
        with open(self.test_input, "w") as f:
            f.write('''
[example]
key1 = 42
key2 = "#(key1)"
            ''')

        transpiler = ConfigTranspiler(self.test_input, self.test_output)
        transpiler.transpile()

        with open(self.test_output, "r") as f:
            result = f.read()

        expected = '''table([
    example = table([
        key1 = 42,
        key2 = 42,
    ]),
])'''
        self.assertEqual(result.strip(), expected.strip())

    def test_constant_chain(self):
        with open(self.test_input, "w") as f:
            f.write('''
[example]
key1 = 42
key2 = "#(key1)"
key3 = "#(key2)"
            ''')

        transpiler = ConfigTranspiler(self.test_input, self.test_output)
        transpiler.transpile()

        with open(self.test_output, "r") as f:
            result = f.read()

        expected = '''table([
    example = table([
        key1 = 42,
        key2 = 42,
        key3 = 42,
    ]),
])'''
        self.assertEqual(result.strip(), expected.strip())

    def test_arrays(self):
        with open(self.test_input, "w") as f:
            f.write('''
[example]
numbers = [1, 2, 3]
mixed = ["text", 42, "#(key)"]

[example.nested]
key = 100
            ''')

        transpiler = ConfigTranspiler(self.test_input, self.test_output)
        transpiler.transpile()

        with open(self.test_output, "r") as f:
            result = f.read()

        expected = '''table([
    example = table([
        numbers = [1, 2, 3],
        mixed = ["text", 42, 100],
        nested = table([
            key = 100,
        ]),
    ]),
])'''
        self.assertEqual(result.strip(), expected.strip())


if __name__ == '__main__':
    unittest.main()
