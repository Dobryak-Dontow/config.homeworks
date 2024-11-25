# Транспилятор конфигурационных файлов

## Общее описание
Данный проект представляет собой транспилятор конфигурационных файлов из формата TOML в учебный конфигурационный язык. 

## Функциональность и настройки

### Поддерживаемые конструкции

1. **Таблицы (словари)**
   - Вложенные таблицы поддерживаются
   - Синтаксис: `table([key = value])`

2. **Константы**
   - Определение констант: `def CONST_NAME := value;`
   - Использование констант: `#(CONST_NAME)`
   - Поддерживается вычисление значений констант на этапе трансляции
   - Поддерживается использование ранее определенных значений как констант

3. **Типы данных**
   - Строки (в кавычках)
   - Целые числа
   - Числа с плавающей точкой

### Правила именования
- Ключи должны соответствовать регулярному выражению: `^[_a-zA-Z][_a-zA-Z0-9]*$`
- Имена констант следуют тем же правилам

### Примеры использования

#### Базовая конфигурация (TOML):
```toml
[database]
host = "localhost"
port = 5432

[database.credentials]
username = "admin"
password = "secret"
```

#### Результат трансляции:
```
table([
    database = table([
        host = "localhost",
        port = 5432,
        credentials = table([
            username = "admin",
            password = "secret",
        ]),
    ]),
])
```

#### Использование констант (TOML):
```toml
[constants]
const_def = "def MAX_VALUE := 100;"
value = "#(MAX_VALUE)"

[example]
key1 = 42
key2 = "#(key1)"
```

#### Результат трансляции:
```
table([
    constants = table([
        value = 100,
    ]),
    example = table([
        key1 = 42,
        key2 = 42,
    ]),
])
```

## Использование

### Установка
```bash
pip install -r requirements.txt
```

### Запуск транспилятора
```bash
python src/transpiler.py -i examples/example1.toml -o output.txt
python src/transpiler.py -i examples/example2.toml -o output.txt
python src/transpiler.py -i examples/example3.toml -o output.txt
```

### Параметры командной строки
- `-i`, `--input`: путь к входному TOML файлу
- `-o`, `--output`: путь к выходному файлу

## Тестирование
Проект содержит модульные тесты, покрывающие все основные конструкции языка:
```bash
python -m unittest tests/test_transpiler.py -v
