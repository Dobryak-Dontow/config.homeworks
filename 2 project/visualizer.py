import os
import sys
import csv
import subprocess

def parse_config(config_path):
    """Читает и парсит файл конфигурации."""
    config = {}
    try:
        with open(config_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                config.update(row)
    except FileNotFoundError:
        print(f"Ошибка: файл конфигурации {config_path} не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении конфигурации: {e}")
        sys.exit(1)
    return config

def get_dependencies(package_name, max_depth):
    """Получает зависимости пакета с использованием команды apt-cache."""
    dependencies = {}
    visited = set()

    def fetch_deps(pkg, depth):
        if depth > max_depth or pkg in visited:
            return
        visited.add(pkg)
        # Удаляем угловые скобки из имени пакета
        clean_pkg = pkg.strip("<>")
        try:
            output = subprocess.check_output(["wsl", "apt-cache", "depends", clean_pkg], text=True)
            deps = []
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Depends:"):
                    dep = line.split("Depends:")[1].strip()
                    deps.append(dep)
            dependencies[pkg] = deps
            for dep in deps:
                fetch_deps(dep, depth + 1)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при вызове apt-cache: {e}")
        except Exception as e:
            print(f"Не удалось получить зависимости для {pkg}: {e}")

    fetch_deps(package_name, 0)
    return dependencies

def generate_mermaid_graph(dependencies):
    """Генерирует описание графа в формате Mermaid."""
    graph = ["graph TD"]
    for pkg, deps in dependencies.items():
        for dep in deps:
            graph.append(f"    {pkg} --> {dep}")
    return "\n".join(graph)

def main():
    # Укажите путь к конфигурационному файлу
    config_path = r"c:\Users\Slava\vsCODE\2 project\config.csv"

    # Проверяем наличие файла конфигурации
    if not os.path.exists(config_path):
        print(f"Ошибка: файл конфигурации {config_path} не найден.")
        sys.exit(1)

    # Парсим конфигурационный файл
    config = parse_config(config_path)

    # Получаем параметры из конфигурации
    visualizer_path = config.get('visualizer_path')
    package_name = config.get('package_name')
    output_file = config.get('output_file')
    max_depth = int(config.get('max_depth', 1))

    # Получаем зависимости
    dependencies = get_dependencies(package_name, max_depth)

    # Генерируем граф в формате Mermaid
    graph = generate_mermaid_graph(dependencies)

    # Записываем граф в файл
    if output_file:
        with open(output_file, mode='w', encoding='utf-8') as file:
            file.write(graph)
        print(f"Граф зависимостей записан в файл {output_file}.")
    else:
        print("Граф зависимостей:")
        print(graph)

if __name__ == "__main__":
    main()
