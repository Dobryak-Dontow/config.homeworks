import argparse
import struct

class Assembler:
    def __init__(self, input_file, output_file, log_file):
        self.input_file = input_file
        self.output_file = output_file
        self.log_file = log_file
        self.opcodes = {
            "LOAD": 2,  # Загрузка данных
            "MIN": 6,   # Минимум двух значений
        }

    def assemble(self):
        binary_data = []
        log_entries = []

        # Считываем текстовый файл с программой
        with open(self.input_file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()

            # Пропускаем пустые строки и комментарии
            if not line or line.startswith(";"):
                continue

            # Разделяем команду и операнды
            parts = line.split()
            if len(parts) < 2:
                raise ValueError(f"Неправильный формат команды: {line}")

            command = parts[0].upper()
            operands = list(map(int, parts[1:]))

            # Проверяем, существует ли команда в таблице опкодов
            if command not in self.opcodes:
                raise ValueError(f"Неизвестная команда: {command}")

            opcode = self.opcodes[command]

            # Пакуем данные в бинарный формат
            if command == "LOAD":
                if len(operands) != 3:
                    raise ValueError(f"Команда LOAD ожидает 3 операнда: {line}")
                # Формат: 1 байт (opcode), 2 байта (operands[0]), 4 байта (operands[1]), 4 байта (operands[2])
                packed_data = struct.pack(">BHII", opcode, operands[0], operands[1], operands[2])
            elif command == "MIN":
                if len(operands) != 4:
                    raise ValueError(f"Команда MIN ожидает 4 операнда: {line}")
                # Формат: 1 байт (opcode), 2 байта (operands[0]), 4 байта (operands[1]), 4 байта (operands[2]), 4 байта (operands[3])
                packed_data = struct.pack(">BHIII", opcode, operands[0], operands[1], operands[2], operands[3])
            else:
                raise ValueError(f"Команда {command} не поддерживается: {line}")

            binary_data.append(packed_data)
            log_entries.append({"command": command, "opcode": opcode, "operands": operands})

            # Отладочный вывод
            print(f"Обработана команда: {command} {operands}")

        # Записываем бинарные данные в выходной файл
        with open(self.output_file, 'wb') as bin_file:
            for entry in binary_data:
                bin_file.write(entry)

        # Создаем лог-файл в формате CSV
        with open(self.log_file, 'w') as log_file:
            log_file.write("command,opcode,operands\n")
            for entry in log_entries:
                log_file.write(
                    f"{entry['command']},{entry['opcode']},{','.join(map(str, entry['operands']))}\n"
                )

        print(f"Сборка завершена. Бинарный файл: {self.output_file}, Лог-файл: {self.log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler for the educational virtual machine.")
    parser.add_argument('-i', '--input', required=True, help="Path to the input assembly file.")
    parser.add_argument('-o', '--output', required=True, help="Path to the output binary file.")
    parser.add_argument('-l', '--log', required=True, help="Path to the log file.")

    args = parser.parse_args()

    assembler = Assembler(args.input, args.output, args.log)
    assembler.assemble()
