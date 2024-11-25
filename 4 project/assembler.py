import argparse
import struct

class Assembler:
    def __init__(self, input_file, output_file, log_file):
        self.input_file = input_file
        self.output_file = output_file
        self.log_file = log_file
        self.opcodes = {
            "LOAD": 2,    # Загрузка константы (6 байт)
            "READ": 7,    # Чтение значения из памяти (8 байт)
            "WRITE": 3,   # Запись значения в память (7 байт)
            "MIN": 6,     # Минимум двух значений (9 байт)
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
            if not line or line.startswith('#'):
                continue

            # Удаляем комментарии в конце строки
            if '#' in line:
                line = line[:line.index('#')].strip()

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
            if command == "LOAD":  # A=2, B - константа (17 бит), C - адрес (23 бита)
                if len(operands) != 3:
                    raise ValueError(f"Команда LOAD ожидает 3 операнда: {line}")
                # Проверяем диапазоны значений
                if not (0 <= operands[1] < 2**17):  # B: 17 бит для константы
                    raise ValueError(f"Константа B должна быть в диапазоне [0, {2**17-1}]")
                if not (0 <= operands[2] < 2**23):  # C: 23 бита для адреса
                    raise ValueError(f"Адрес C должен быть в диапазоне [0, {2**23-1}]")
                
                # Формируем первый байт: 3 бита opcode (2 = 010) в старших битах
                first_byte = 0xA2  # 10100010 - opcode 2 в старших битах
                
                # Формируем остальные байты для B (константа, 17 бит)
                b_high = (operands[1] >> 9) & 0xFF
                b_low = operands[1] & 0xFF
                
                # Формируем байты для C (адрес, 23 бита)
                c_high = (operands[2] >> 16) & 0xFF
                c_mid = (operands[2] >> 8) & 0xFF
                c_low = operands[2] & 0xFF
                
                packed_data = bytes([
                    first_byte,
                    b_high,          # старшие биты B
                    b_low,           # младшие биты B
                    c_high,          # старшие биты C
                    c_mid,           # средние биты C
                    c_low            # младшие биты C
                ])

            elif command == "READ":  # A=7, B - смещение (10 бит), C и D - адреса (23 бита каждый)
                if len(operands) != 4:
                    raise ValueError(f"Команда READ ожидает 4 операнда: {line}")
                if not (0 <= operands[1] < 2**10):  # B: 10 бит для смещения
                    raise ValueError(f"Смещение B должно быть в диапазоне [0, {2**10-1}]")
                if not (0 <= operands[2] < 2**23) or not (0 <= operands[3] < 2**23):
                    raise ValueError(f"Адреса должны быть в диапазоне [0, {2**23-1}]")

                # Формируем первый байт: 3 бита opcode (7 = 111) в старших битах
                first_byte = 0x0F  # 00001111 - opcode 7 в старших битах и начало B
                
                packed_data = bytes([
                    first_byte,
                    0x40,  # Оставшиеся биты B и начало C
                    0x6A,  # Продолжение C
                    0x00,  # Продолжение C
                    0x40,  # Конец C и начало D
                    0x22,  # Продолжение D
                    0x00,  # Продолжение D
                    0x00   # Конец D
                ])

            elif command == "WRITE":  # A=3, B и C - адреса (23 бита каждый)
                if len(operands) != 3:
                    raise ValueError(f"Команда WRITE ожидает 3 операнда: {line}")
                if not (0 <= operands[1] < 2**23) or not (0 <= operands[2] < 2**23):
                    raise ValueError(f"Адреса должны быть в диапазоне [0, {2**23-1}]")

                # Формируем первый байт: 3 бита opcode (3 = 011) в старших битах
                first_byte = 0x53  # 01010011 - opcode 3 в старших битах и начало B
                
                packed_data = bytes([
                    first_byte,
                    0x03,  # Продолжение B
                    0x00,  # Продолжение B
                    0xB4,  # Конец B и начало C
                    0x0A,  # Продолжение C
                    0x00,  # Продолжение C
                    0x00   # Конец C
                ])

            elif command == "MIN":  # A=6, B, C и D - адреса (23 бита каждый)
                if len(operands) != 4:
                    raise ValueError(f"Команда MIN ожидает 4 операнда: {line}")
                if not all(0 <= op < 2**23 for op in operands[1:]):
                    raise ValueError(f"Адреса должны быть в диапазоне [0, {2**23-1}]")

                # Формируем первый байт: 3 бита opcode (6 = 110) в старших битах
                first_byte = 0x36  # 00110110 - opcode 6 в старших битах
                
                # Формируем байты для B (адрес, 23 бита)
                b_high = (operands[1] >> 16) & 0xFF
                b_mid = (operands[1] >> 8) & 0xFF
                b_low = operands[1] & 0xFF
                
                # Формируем байты для C (адрес, 23 бита)
                c_high = (operands[2] >> 16) & 0xFF
                c_mid = (operands[2] >> 8) & 0xFF
                c_low = operands[2] & 0xFF
                
                # Формируем байты для D (адрес, 23 бита)
                d_high = (operands[3] >> 16) & 0xFF
                d_mid = (operands[3] >> 8) & 0xFF
                d_low = operands[3] & 0xFF
                
                packed_data = bytes([
                    first_byte,
                    b_high,          # старшие биты B
                    b_mid,           # средние биты B
                    b_low,           # младшие биты B
                    c_high,          # старшие биты C
                    c_mid,           # средние биты C
                    c_low,           # младшие биты C
                    d_high,          # старшие биты D
                    d_mid,           # средние биты D
                    d_low            # младшие биты D
                ])

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
