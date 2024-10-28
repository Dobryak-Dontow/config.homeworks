import unittest
import os
import json
import tarfile
from shell_emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        self.config = {
            "fs_path": "test_virtual_filesystem.tar",
            "log_path": "test_log.xml",
            "start_script_path": "start_script.sh"
        }
        
        # Сохранение конфигурации в JSON файл
        with open('test_config.json', 'w') as f:
            json.dump(self.config, f)

        # Создание тестового архива
        self.emulator = ShellEmulator('test_config.json')
        self.emulator.create_virtual_fs()  # Создаем виртуальную файловую систему

    def tearDown(self):
        # Удаляем созданные файлы после тестов
        if os.path.exists(self.config['fs_path']):
            os.remove(self.config['fs_path'])
        if os.path.exists(self.config['log_path']):
            os.remove(self.config['log_path'])
        if os.path.exists('test_config.json'):
            os.remove('test_config.json')

    def test_load_virtual_fs(self):
        self.emulator.load_virtual_fs()
        # Проверяем, что директория была создана
        self.assertTrue(os.path.exists('virtual_fs'))
        self.assertTrue(os.path.isdir('virtual_fs'))

    def test_ls_command(self):
        self.emulator.load_virtual_fs()
        result = self.emulator.execute_command('ls')
        expected_files = {'file1.txt', 'file2.txt', 'directory'}
        self.assertTrue(expected_files.issubset(set(result.split('\n'))))

    def test_cd_command(self):
        self.emulator.load_virtual_fs()
        self.emulator.execute_command('cd directory')
        self.assertEqual(self.emulator.current_directory, os.path.join('virtual_fs', 'directory'))

        # Проверка на переход в несуществующую директорию
        result = self.emulator.execute_command('cd non_existing_directory')
        self.assertEqual(result, "Directory non_existing_directory not found")

    def test_exit_command(self):
        result = self.emulator.execute_command('exit')
        self.assertEqual(result, "Exiting...")

    def test_cp_command_not_implemented(self):
        result = self.emulator.execute_command('cp file1.txt file2.txt')
        self.assertEqual(result, "Copied from file1.txt to file2.txt (not implemented)")

if __name__ == '__main__':
    unittest.main()
