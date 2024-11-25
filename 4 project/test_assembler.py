import unittest
from assembler import Assembler
import os
import tempfile

class TestAssembler(unittest.TestCase):
    def setUp(self):
        # Создаем временные файлы для тестов
        self.temp_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.temp_dir, "test.asm")
        self.output_file = os.path.join(self.temp_dir, "test.bin")
        self.log_file = os.path.join(self.temp_dir, "test.log")

    def tearDown(self):
        # Удаляем временные файлы
        for file in [self.input_file, self.output_file, self.log_file]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)

    def test_load_command(self):
        # Тест команды LOAD с параметрами A=2, B=20, C=869
        # Ожидаемый результат: 0xA2, 0x00, 0x50, 0x36, 0x00, 0x00
        with open(self.input_file, 'w') as f:
            f.write("LOAD 2 20 869")

        assembler = Assembler(self.input_file, self.output_file, self.log_file)
        assembler.assemble()

        with open(self.output_file, 'rb') as f:
            binary_data = f.read()

        expected = bytes([
            0xA2,           # A=2 (старшие 3 бита), начало B
            0x00,           # продолжение B
            0x50,           # конец B и начало C
            0x36,           # продолжение C
            0x00,           # продолжение C
            0x00            # конец C
        ])
        self.assertEqual(binary_data, expected)

    def test_read_command(self):
        # Тест команды READ с параметрами A=7, B=1, C=850, D=548
        # Ожидаемый результат: 0x0F, 0x40, 0x6A, 0x00, 0x40, 0x22, 0x00, 0x00
        with open(self.input_file, 'w') as f:
            f.write("READ 7 1 850 548")

        assembler = Assembler(self.input_file, self.output_file, self.log_file)
        assembler.assemble()

        with open(self.output_file, 'rb') as f:
            binary_data = f.read()

        expected = bytes([
            0x0F,           # A=7 (старшие 3 бита), начало B
            0x40,           # конец B и начало C
            0x6A,           # продолжение C
            0x00,           # продолжение C
            0x40,           # конец C и начало D
            0x22,           # продолжение D
            0x00,           # продолжение D
            0x00            # конец D
        ])
        self.assertEqual(binary_data, expected)

    def test_write_command(self):
        # Тест команды WRITE с параметрами A=3, B=106, C=685
        # Ожидаемый результат: 0x53, 0x03, 0x00, 0xB4, 0x0A, 0x00, 0x00
        with open(self.input_file, 'w') as f:
            f.write("WRITE 3 106 685")

        assembler = Assembler(self.input_file, self.output_file, self.log_file)
        assembler.assemble()

        with open(self.output_file, 'rb') as f:
            binary_data = f.read()

        expected = bytes([
            0x53,           # A=3 (старшие 3 бита), начало B
            0x03,           # продолжение B
            0x00,           # продолжение B
            0xB4,           # конец B и начало C
            0x0A,           # продолжение C
            0x00,           # продолжение C
            0x00            # конец C
        ])
        self.assertEqual(binary_data, expected)

    def test_min_command(self):
        # Тест команды MIN с параметрами A=6, B=326, C=197, D=834
        # Ожидаемый результат: 0x36, 0x0A, 0x00, 0x14, 0x03, 0x00, 0x84, 0x06, 0x00
        with open(self.input_file, 'w') as f:
            f.write("MIN 6 326 197 834")

        assembler = Assembler(self.input_file, self.output_file, self.log_file)
        assembler.assemble()

        with open(self.output_file, 'rb') as f:
            binary_data = f.read()

        expected = bytes([
            0x36,           # A=6 (старшие 3 бита), начало B
            0x0A,           # продолжение B
            0x00,           # продолжение B
            0x14,           # конец B и начало C
            0x03,           # продолжение C
            0x00,           # продолжение C
            0x84,           # конец C и начало D
            0x06,           # продолжение D
            0x00            # конец D
        ])
        self.assertEqual(binary_data, expected)

    def test_invalid_command(self):
        # Тест на неправильную команду
        with open(self.input_file, 'w') as f:
            f.write("INVALID 1 2 3")

        assembler = Assembler(self.input_file, self.output_file, self.log_file)
        with self.assertRaises(ValueError):
            assembler.assemble()

    def test_invalid_operands_count(self):
        # Тест на неправильное количество операндов
        with open(self.input_file, 'w') as f:
            f.write("LOAD 1 2")  # LOAD требует 3 операнда

        assembler = Assembler(self.input_file, self.output_file, self.log_file)
        with self.assertRaises(ValueError):
            assembler.assemble()

if __name__ == '__main__':
    unittest.main()
