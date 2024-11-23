import argparse
import toml
import re


class ConfigTranspiler:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.constants = {}

    def transpile(self):
        try:
            # Читаем входной файл TOML
            with open(self.input_file, 'r') as file:
                toml_data = toml.load(file)
            
            # Преобразуем данные
            result = self.process_data(toml_data)
            
            # Записываем результат в выходной файл
            with open(self.output_file, 'w') as file:
                file.write(result)
            
            print(f"Трансляция завершена. Результат записан в {self.output_file}")
        except toml.TomlDecodeError as e:
            print(f"Ошибка синтаксиса TOML: {e}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def process_data(self, data, level=0):
        output = []
        indent = '    ' * level

        if isinstance(data, dict):  # Если это словарь
            output.append(f"{indent}table([")
            for key, value in data.items():
                if not self.is_valid_name(key):
                    raise ValueError(f"Некорректное имя ключа: {key}")
                processed_value = self.process_data(value, level + 1)
                output.append(f"{indent}    {key} = {processed_value},")
            output.append(f"{indent}])")
        elif isinstance(data, int):  # Если это число
            output.append(str(data))
        elif isinstance(data, str):  # Если это строка
            output.append(f'"{data}"')  # Добавляем кавычки вокруг строки
        else:  # Необработанный тип данных
            raise ValueError(f"Необработанный тип данных: {type(data)}")

        return '\n'.join(output)


    def is_valid_name(self, name):
        """Проверяем имя на соответствие правилам."""
        return re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', name) is not None


def main():
    parser = argparse.ArgumentParser(description="TOML в учебный конфигурационный язык")
    parser.add_argument("-i", "--input", required=True, help="Путь к входному TOML-файлу")
    parser.add_argument("-o", "--output", required=True, help="Путь к выходному файлу")
    args = parser.parse_args()

    transpiler = ConfigTranspiler(args.input, args.output)
    transpiler.transpile()


if __name__ == "__main__":
    main()
