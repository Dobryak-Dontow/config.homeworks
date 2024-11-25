import argparse
import csv

MEMORY_SIZE = 2048  # Размер памяти в байтах

class Interpreter:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range
        self.memory = [0] * MEMORY_SIZE
        
    def check_address(self, addr, operation):
        if not (0 <= addr < MEMORY_SIZE):
            raise ValueError(f"Адрес {addr} выходит за пределы памяти при выполнении {operation}")
    
    def load_program(self):
        with open(self.binary_file, "rb") as file:
            self.program = file.read()

    def execute(self):
        pointer = 0
        while pointer < len(self.program):
            # Получаем opcode из первого байта
            first_byte = self.program[pointer]
            
            if first_byte == 0xA2:  # LOAD (6 байт)
                # Декодируем B (константа) и C (адрес) из следующих байтов
                B = (self.program[pointer + 1] << 8) | self.program[pointer + 2]
                C = (self.program[pointer + 3] << 16) | (self.program[pointer + 4] << 8) | self.program[pointer + 5]
                self.check_address(C, "LOAD")
                self.memory[C] = B
                print(f"LOAD: Записано значение {B} по адресу {C}")
                pointer += 6
            
            elif first_byte == 0x0F:  # READ (8 байт)
                # Декодируем B (смещение), C и D (адреса) из следующих байтов
                B = ((self.program[pointer + 1] << 2) | (self.program[pointer + 2] >> 6)) & 0x3FF
                C = ((self.program[pointer + 2] << 17) | (self.program[pointer + 3] << 9) | (self.program[pointer + 4] << 1) | (self.program[pointer + 5] >> 7)) & 0x7FFFFF
                D = ((self.program[pointer + 5] << 16) | (self.program[pointer + 6] << 8) | self.program[pointer + 7]) & 0x7FFFFF
                self.check_address(C, "READ source")
                value = self.memory[C] + B
                self.check_address(value, "READ computed")
                self.check_address(D, "READ destination")
                self.memory[D] = self.memory[value]
                pointer += 8

            elif first_byte == 0x53:  # WRITE (7 байт)
                # Декодируем B и C (адреса) из следующих байтов
                B = ((self.program[pointer + 1] << 15) | (self.program[pointer + 2] << 7) | (self.program[pointer + 3] >> 1)) & 0x7FFFFF
                C = ((self.program[pointer + 3] << 22) | (self.program[pointer + 4] << 14) | (self.program[pointer + 5] << 6) | (self.program[pointer + 6] >> 2)) & 0x7FFFFF
                self.check_address(B, "WRITE source")
                self.check_address(C, "WRITE pointer")
                dest_addr = self.memory[C]
                self.check_address(dest_addr, "WRITE destination")
                self.memory[dest_addr] = self.memory[B]
                pointer += 7

            elif first_byte == 0x36:  # MIN (10 байт)
                # Декодируем B, C и D (адреса) из следующих байтов
                B = (self.program[pointer + 1] << 16) | (self.program[pointer + 2] << 8) | self.program[pointer + 3]
                C = (self.program[pointer + 4] << 16) | (self.program[pointer + 5] << 8) | self.program[pointer + 6]
                D = (self.program[pointer + 7] << 16) | (self.program[pointer + 8] << 8) | self.program[pointer + 9]
                
                self.check_address(B, "MIN first operand")
                self.check_address(C, "MIN second operand")
                self.check_address(D, "MIN result")
                
                val1 = self.memory[B]
                val2 = self.memory[C]
                result = min(val1, val2)
                print(f"MIN: Сравниваем значения memory[{B}]={val1} и memory[{C}]={val2}, результат {result} записан по адресу {D}")
                self.memory[D] = result
                pointer += 10

            else:
                raise ValueError(f"Неизвестная команда: {hex(first_byte)}")

        self.save_results()

    def save_results(self):
        start, end = self.memory_range
        with open(self.result_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Address", "Value"])
            for addr in range(start, end + 1):
                writer.writerow([addr, self.memory[addr]])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Интерпретатор УВМ.")
    parser.add_argument("-i", "--input", required=True, help="Путь к бинарному файлу")
    parser.add_argument("-r", "--result", required=True, help="Путь к файлу результата")
    parser.add_argument("--range", required=True, type=int, nargs=2, help="Диапазон памяти (start end)")

    args = parser.parse_args()
    interpreter = Interpreter(args.input, args.result, args.range)
    interpreter.load_program()
    interpreter.execute()
