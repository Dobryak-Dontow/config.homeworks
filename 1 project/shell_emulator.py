import os
import json
import tarfile
import xml.etree.ElementTree as ET
import datetime

class ShellEmulator:
    def __init__(self, config_file):
        self.load_config(config_file)
        self.current_directory = "virtual_fs"  # Текущая директория внутри виртуальной файловой системы
        self.log_actions = []

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            self.fs_archive = config['fs_path']
            self.log_file_path = config['log_path']
            self.start_script_path = config['start_script_path']

    def create_virtual_fs(self):
        with tarfile.open(self.fs_archive, 'w') as tar:
            test_files = ['file1.txt', 'file2.txt', 'directory/file3.txt']
            for file in test_files:
                file_path = os.path.join('virtual_fs', file)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(f"Contents of {file}")
                tar.add(file_path, arcname=file)

    def load_virtual_fs(self):
        if not os.path.exists(self.fs_archive):
            print(f"Archive {self.fs_archive} not found. Creating a default one.")
            self.create_virtual_fs()

        with tarfile.open(self.fs_archive, 'r') as tar:
            tar.extractall(path='virtual_fs')

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
            return self.cmd_cp(parts[1], parts[2])
        else:
            return "Unknown command"


    def cmd_ls(self):
        try:
            return "\n".join(os.listdir(self.current_directory))
        except FileNotFoundError:
            return "Directory not found"

    def cmd_cd(self, path):
        new_path = os.path.join(self.current_directory, path)
        if os.path.isdir(new_path):
            self.current_directory = new_path
            return f"Changed directory to {self.current_directory}"
        else:
            return f"Directory {path} not found"

    def cmd_rev(self, filename):
        return f"Reversed {filename} (not implemented)"

    def cmd_cal(self):
        return "Calendar (not implemented)"

    def cmd_cp(self, src, dest):
        return f"Copied from {src} to {dest} (not implemented)"

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
