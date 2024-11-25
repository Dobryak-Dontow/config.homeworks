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
            
            # Ищем и обрабатываем константы
            self.extract_constants(toml_data)
            
            # Преобразуем данные
            result = self.process_data(toml_data)
            
            # Записываем результат в выходной файл
            with open(self.output_file, 'w') as file:
                file.write(result)
            
            print(f"Трансляция завершена. Результат записан в {self.output_file}")
            return result
        except toml.TomlDecodeError as e:
            raise ValueError(f"Ошибка синтаксиса TOML: {e}")
        except Exception as e:
            raise

    def extract_constants(self, data, path=""):
        """Извлекает константы из данных."""
        if isinstance(data, dict):
            # Сначала обрабатываем все числовые значения в текущем словаре
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, (int, float)):
                    self.constants[current_path] = str(value)

            # Затем обрабатываем определения констант
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str) and value.startswith("def ") and ":=" in value:
                    try:
                        const_name = value.split(" ")[1]
                        const_value = value.split(":=")[1].strip().rstrip(";")
                        self.constants[const_name] = const_value
                    except IndexError:
                        raise ValueError(f"Некорректное определение константы: {value}")

            # В конце рекурсивно обрабатываем вложенные словари
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, dict):
                    self.extract_constants(value, current_path)

    def resolve_constant(self, value, path=""):
        """Разрешает значение константы."""
        if isinstance(value, str) and value.startswith("#(") and value.endswith(")"):
            const_name = value[2:-1]  # Убираем #( и )
            
            # Сначала пробуем найти константу по полному пути
            full_path = f"{path}.{const_name}" if path else const_name
            if full_path in self.constants:
                const_value = self.constants[full_path]
            # Затем пробуем найти по имени
            elif const_name in self.constants:
                const_value = self.constants[const_name]
            else:
                raise ValueError(f"Неопределенная константа: {const_name}")

            # Если значение само является ссылкой на константу, разрешаем рекурсивно
            if isinstance(const_value, str) and const_value.startswith("#("):
                return self.resolve_constant(const_value, path)
            
            # Пробуем преобразовать в число
            try:
                return int(const_value)
            except ValueError:
                try:
                    return float(const_value)
                except ValueError:
                    return const_value
        return value

    def process_data(self, data, level=0, path=""):
        output = []
        indent = '    ' * level

        if isinstance(data, dict):  # Если это словарь
            output.append(f"{indent}table([")
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if not self.is_valid_name(key):
                    raise ValueError(f"Некорректное имя ключа: {key}")
                
                # Пропускаем определения констант
                if isinstance(value, str) and value.startswith("def ") and ":=" in value:
                    continue
                
                # Разрешаем константы
                resolved_value = self.resolve_constant(value, path)
                # Сохраняем разрешенное значение как константу
                if isinstance(resolved_value, (int, float)):
                    self.constants[current_path] = str(resolved_value)
                
                processed_value = self.process_data(resolved_value, level + 1, current_path).lstrip()
                output.append(f"{indent}    {key} = {processed_value},")
            output.append(f"{indent}])")
        elif isinstance(data, list):  # Если это список
            items = []
            for item in data:
                # Разрешаем константы в элементах списка
                resolved_item = self.resolve_constant(item, path)
                processed_item = self.process_data(resolved_item, 0, path).lstrip()
                items.append(processed_item)
            return f"[{', '.join(items)}]"
        elif isinstance(data, (int, float)):  # Если это число
            output.append(str(data))
        elif isinstance(data, str):  # Если это строка
            # Проверяем, не является ли строка определением константы
            if not (data.startswith("def ") and ":=" in data):
                output.append(f'"{data}"')  # Добавляем кавычки вокруг строки
        else:  # Необработанный тип данных
            raise ValueError(f"Необработанный тип данных: {type(data)}")

        return '\n'.join(output) if len(output) > 1 else output[0] if output else ""

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
