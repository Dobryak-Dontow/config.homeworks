import argparse
import toml
import re


class ConfigTranspiler:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.constants = {}

    def transpile(self):
        """Транспилирует TOML в целевой формат."""
        try:
            with open(self.input_file, "r") as f:
                toml_data = toml.load(f)
            
            # Сначала собираем все константы из всего файла
            self.extract_constants(toml_data)
            
            # Разрешаем все константы до обработки данных
            self.resolve_all_constants()
            
            # Затем обрабатываем данные
            result = self.process_data(toml_data)
            
            with open(self.output_file, "w") as f:
                f.write(result)
            print("Трансляция завершена. Результат записан в", self.output_file)
        except toml.TomlDecodeError as e:
            raise ValueError(f"Ошибка синтаксиса TOML: {e}")
        except Exception as e:
            raise

    def extract_constants(self, data, path=""):
        """Извлекает все константы из данных, включая значения, которые можно использовать как константы."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Сохраняем числовые значения как константы
                if isinstance(value, (int, float)):
                    self.constants[current_path] = str(value)
                    self.constants[key] = str(value)  # Также сохраняем по короткому имени
                # Обрабатываем определения констант
                elif isinstance(value, str) and value.startswith("def ") and ":=" in value:
                    const_name = value.split(":=")[0].replace("def ", "").strip()
                    const_value = value.split(":=")[1].strip().rstrip(";").strip()
                    try:
                        # Пробуем преобразовать в число, если возможно
                        if '.' in const_value:
                            const_value = float(const_value)
                        else:
                            const_value = int(const_value)
                    except ValueError:
                        # Если не получилось, оставляем как строку
                        const_value = const_value.strip('"')
                    self.constants[const_name] = str(const_value)
                # Сохраняем ссылки на константы как есть
                elif isinstance(value, str) and value.startswith("#(") and value.endswith(")"):
                    self.constants[current_path] = value
                    self.constants[key] = value
                
                # Рекурсивно обрабатываем вложенные структуры
                self.extract_constants(value, current_path)
        elif isinstance(data, list):
            # Обрабатываем каждый элемент списка
            for item in data:
                self.extract_constants(item, path)

    def resolve_all_constants(self):
        """Разрешает все константы перед обработкой данных."""
        print("Initial constants:", self.constants)  # Debug
        
        # Повторяем процесс разрешения, пока есть изменения
        changes = True
        while changes:
            changes = False
            resolved = {}
            
            for name, value in self.constants.items():
                if isinstance(value, str) and value.startswith("#("):
                    try:
                        resolved_value = str(self.resolve_constant(value))
                        if resolved_value != value:
                            resolved[name] = resolved_value
                            changes = True
                            print(f"Resolved {name}: {value} -> {resolved_value}")  # Debug
                    except ValueError:
                        # Пропускаем неразрешенные константы, попробуем позже
                        continue
            
            # Обновляем словарь констант разрешенными значениями
            self.constants.update(resolved)
            print("Current constants:", self.constants)  # Debug
        
        # Проверяем, остались ли неразрешенные константы
        for name, value in self.constants.items():
            if isinstance(value, str) and value.startswith("#("):
                raise ValueError(f"Не удалось разрешить константу {name}: {value}")

    def resolve_constant(self, value, path="", visited=None):
        """Разрешает значение константы, если это ссылка на константу."""
        if visited is None:
            visited = set()

        if isinstance(value, str) and value.startswith("#(") and value.endswith(")"):
            const_name = value[2:-1].strip()
            
            # Проверяем циклические зависимости
            if const_name in visited:
                raise ValueError(f"Обнаружена циклическая зависимость: {const_name}")
            visited.add(const_name)
            
            # Пробуем найти константу по полному пути или короткому имени
            if const_name in self.constants:
                const_value = self.constants[const_name]
            else:
                full_path = f"{path}.{const_name}" if path else const_name
                if full_path in self.constants:
                    const_value = self.constants[full_path]
                else:
                    raise ValueError(f"Неопределенная константа: {const_name}")
            
            # Если значение само является ссылкой на константу, разрешаем рекурсивно
            if isinstance(const_value, str) and const_value.startswith("#("):
                return self.resolve_constant(const_value, path, visited)
            
            # Преобразуем строковое представление в соответствующий тип
            try:
                if '.' in const_value:
                    return float(const_value)
                return int(const_value)
            except ValueError:
                return const_value
        return value

    def process_data(self, data, level=0, path=""):
        """Обрабатывает данные и возвращает результат в целевом формате."""
        output = []
        indent = '    ' * level

        if isinstance(data, dict):
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
                processed_value = self.process_data(resolved_value, level + 1, current_path).lstrip()
                output.append(f"{indent}    {key} = {processed_value},")
            
            output.append(f"{indent}])")
        elif isinstance(data, list):
            items = []
            for item in data:
                resolved_item = self.resolve_constant(item, path)
                processed_item = self.process_data(resolved_item, 0, path).lstrip()
                items.append(processed_item)
            return f"[{', '.join(items)}]"
        elif isinstance(data, (int, float)):
            output.append(str(data))
        elif isinstance(data, str):
            # Проверяем, не является ли строка определением константы
            if not (data.startswith("def ") and ":=" in data):
                output.append(f'"{data}"')
        else:
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
