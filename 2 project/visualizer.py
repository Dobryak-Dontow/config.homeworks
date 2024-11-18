import os
import sys
import gzip
import requests
from collections import defaultdict

def download_packages_gz(base_url, distro, component, arch):
    """
    Загружает и распаковывает файл Packages.gz.
    """
    url = f"{base_url}/dists/{distro}/{component}/binary-{arch}/Packages.gz"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with gzip.open(response.raw, 'rt', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        sys.exit(1)

def parse_packages(packages_data):
    """
    Парсит содержимое файла Packages.gz и возвращает зависимости пакетов.
    """
    dependencies = defaultdict(list)
    current_package = None

    for line in packages_data.splitlines():
        line = line.strip()
        if line.startswith("Package:"):
            current_package = line.split(":", 1)[1].strip()
        elif line.startswith("Depends:") and current_package:
            dep_line = line.split(":", 1)[1].strip()
            deps = [dep.split()[0] for dep in dep_line.split(",")]
            dependencies[current_package].extend(deps)
        elif not line:  # Пустая строка — конец блока текущего пакета
            current_package = None

    return dependencies

def build_dependency_graph(package_name, dependencies, max_depth):
    """
    Построение графа зависимостей до указанной глубины.
    """
    graph = defaultdict(list)
    visited = set()

    def fetch_deps(pkg, depth):
        if depth > max_depth or pkg in visited:
            return
        visited.add(pkg)
        for dep in dependencies.get(pkg, []):
            graph[pkg].append(dep)
            fetch_deps(dep, depth + 1)

    fetch_deps(package_name, 0)
    return graph

def generate_mermaid_graph(graph):
    """
    Генерирует граф в формате Mermaid.
    """
    mermaid = ["graph TD"]
    for pkg, deps in graph.items():
        for dep in deps:
            mermaid.append(f"    {pkg} --> {dep}")
    return "\n".join(mermaid)

def main():
    # Настройки
    config_path = r"c:\Users\Slava\vsCODE\2 project\config.csv"
    base_url = "http://archive.ubuntu.com/ubuntu"
    distro = "focal"
    component = "main"
    arch = "amd64"

    # Проверка конфигурации
    if not os.path.exists(config_path):
        print(f"Ошибка: файл конфигурации {config_path} не найден.")
        sys.exit(1)

    # Чтение конфигурации
    with open(config_path, 'r', encoding='utf-8') as file:
        visualizer_path, package_name, output_file, max_depth = map(str.strip, file.readlines()[1].split(','))

    max_depth = int(max_depth)

    # Загрузка и парсинг файла Packages.gz
    print("Загрузка Packages.gz...")
    packages_data = download_packages_gz(base_url, distro, component, arch)
    print("Парсинг Packages.gz...")
    dependencies = parse_packages(packages_data)

    # Построение графа зависимостей
    print("Построение графа зависимостей...")
    graph = build_dependency_graph(package_name, dependencies, max_depth)

    # Генерация Mermaid-графа
    print("Генерация Mermaid-графа...")
    mermaid_graph = generate_mermaid_graph(graph)

    # Запись в файл
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(mermaid_graph)
        print(f"Граф зависимостей записан в файл {output_file}.")
    else:
        print("Граф зависимостей:")
        print(mermaid_graph)

if __name__ == "__main__":
    main()
