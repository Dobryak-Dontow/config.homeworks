import argparse
import csv
import struct

MEMORY_SIZE = 1024

class Interpreter:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range
        self.memory = [0] * MEMORY_SIZE

    def load_program(self):
        with open(self.binary_file, "rb") as file:
            self.program = file.read()

    def execute(self):
        pointer = 0
        while pointer < len(self.program):
            opcode = self.program[pointer]
            
            if opcode == 2:  # LOAD
                _, A, B, C = struct.unpack(">BHBI", self.program[pointer:pointer+6])
                self.memory[C] = B
                pointer += 6
            
            elif opcode == 7:  # READ
                _, B, C, D = struct.unpack(">BHII", self.program[pointer:pointer+8])
                value = self.memory[C] + B
                self.memory[D] = self.memory[value]
                pointer += 8

            elif opcode == 3:  # WRITE
                _, B, C = struct.unpack(">BHII", self.program[pointer:pointer+7])
                self.memory[self.memory[C]] = self.memory[B]
                pointer += 7

            elif opcode == 6:  # MIN
                _, B, C, D = struct.unpack(">BHIII", self.program[pointer:pointer+9])
                value1 = self.memory[self.memory[C]]
                value2 = self.memory[B]
                self.memory[D] = min(value1, value2)
                pointer += 9

            else:
                raise ValueError(f"Неизвестная команда: {opcode}")

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
