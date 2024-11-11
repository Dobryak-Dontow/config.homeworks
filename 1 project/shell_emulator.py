import os
import json
import tarfile
import xml.etree.ElementTree as ET
import datetime
import shutil
import calendar
from io import BytesIO

class ShellEmulator:
    def __init__(self, config_file):
        self.load_config(config_file)
        self.fs_structure = {}  # Хранит файлы и каталоги виртуальной файловой системы
        self.current_directory = ""  # Текущая директория внутри виртуальной файловой системы
        self.log_actions = []
        self.load_virtual_fs()  # Загружаем виртуальную файловую систему при инициализации

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            self.fs_archive = config['fs_path']
            self.log_file_path = config['log_path']
            self.start_script_path = config['start_script_path']


    def load_virtual_fs(self):
        if not os.path.exists(self.fs_archive):
            print(f"Archive {self.fs_archive} not found.")
            exit(1)

        # Загружаем файловую систему в память, используя tarfile
        with tarfile.open(self.fs_archive, 'r') as tar:
            for member in tar.getmembers():
                if member.isdir():
                    self.fs_structure[member.name] = set()
                elif member.isfile():
                    file_content = tar.extractfile(member).read().decode()
                    self.fs_structure[member.name] = file_content
        
        self.fs_structure[''] = set()
        for member in self.fs_structure:
            if member == '':
                continue

            if member.count('/') == 0:
                self.fs_structure[''].add(member)

            if type(self.fs_structure[member]) != set:
                continue

            for smember in self.fs_structure:
                if smember.startswith(member) and member.count('/')+1 == smember.count('/'):
                    self.fs_structure[member].add(os.path.basename(smember))
        
    def log_action(self, action):
        self.log_actions.append((datetime.datetime.now(), action))

    def execute_command(self, command):
        parts = command.split()
        if not parts:
            return "Unknown command"

        cmd = parts[0]
        self.log_action(command)  # Логируем команду

        if cmd == "ls":
            return self.cmd_ls()
        elif cmd == "cd":
            return self.cmd_cd(parts[1] if len(parts) > 1 else "")
        elif cmd == "exit":
            self.save_log()
            return "Exiting..."
        elif cmd == "rev":
            return self.cmd_rev(parts[1] if len(parts) > 1 else "")
        elif cmd == "cal":
            return self.cmd_cal()
        elif cmd == "cp":
            if len(parts) < 3:
                return "cp requires source and destination arguments"
            return self.cmd_cp(parts[1], parts[2])
        else:
            return "Unknown command"

    def cmd_ls(self):
        path = self.current_directory if self.current_directory in self.fs_structure else ""
        if path in self.fs_structure:
            if type(self.fs_structure[path]) == set:
                return "\n".join(self.fs_structure[path])
            else:
                return "Not a directory"
        else:
            return "Directory not found"

    def cmd_cd(self, path):
        if path == "..":
            new_path = os.path.dirname(self.current_directory)
        else:
            new_path = os.path.join(self.current_directory, path)

        if new_path in self.fs_structure and type(self.fs_structure[new_path]) == set:
            self.current_directory = new_path
            return f"Changed directory to {self.current_directory}"
        else:
            return f"Directory {path} not found"

    def cmd_rev(self, filename):
        file_path = os.path.join(self.current_directory, filename)
        if file_path in self.fs_structure and type(self.fs_structure[file_path]) == str:
            return self.fs_structure[file_path][::-1]
        else:
            return f"File {filename} not found"

    def cmd_cal(self):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        return calendar.month(year, month)
    
    def cmd_cp(self, src, dest):
        src_path = os.path.join(self.current_directory, src)
        dest_path = os.path.join(self.current_directory, dest)
        if src_path in self.fs_structure:
            self.fs_structure[self.current_directory].add(dest)
            self.fs_structure[dest_path] = self.fs_structure[src_path]
            return f"Copied from {src} to {dest}"
        else:
            return f"File {src} not found"

    def save_log(self):
        root = ET.Element("log")
        for timestamp, action in self.log_actions:
            entry = ET.SubElement(root, "entry")
            entry.set("time", timestamp.isoformat())
            entry.text = action
        tree = ET.ElementTree(root)
        tree.write(self.log_file_path)

if __name__ == "__main__":
    emulator = ShellEmulator('config.json')
    while True:
        command = input(f"{emulator.current_directory}> ")
        result = emulator.execute_command(command)
        print(result)
        if command.strip() == "exit":
            break
