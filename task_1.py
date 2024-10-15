import os
import json
import tarfile
import argparse
import tkinter as tk
from tkinter import messagebox, simpledialog

# Глобальные переменные
current_directory = ""
permissions = {}
log_data = []

# Функция для парсинга аргументов командной строки
def parse_arguments():
    parser = argparse.ArgumentParser(description="Эмулятор терминала")
    parser.add_argument("user_name", type=str, help="Имя пользователя")
    parser.add_argument("pc_name", type=str, help="Имя компьютера")
    parser.add_argument("tar_path", type=str, help="Путь к архиву виртуальной файловой системы")
    parser.add_argument("log_path", type=str, help="Путь к лог-файлу")
    return parser.parse_args()

# Функция для логирования действий
def log_action(user, command, result):
    global log_data
    action = {
        "user": user,
        "command": command,
        "result": result
    }
    log_data.append(action)

# Функция для записи лога в файл
def write_log_to_file():
    with open(args.log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)

# Функция для вывода содержимого директории
def ls(tar):
    with tarfile.open(args.tar_path, "r") as mytar:
        return [member.name for member in mytar.getmembers() if member.path.startswith(current_directory)]

# Функция для смены директории
def cd(path):
    global current_directory
    if path == "..":
        # Переход к родительской директории
        current_directory = os.path.dirname(current_directory) or "/"
    else:
        new_path = os.path.join(current_directory, path)
        # Проверка существования директории в tar
        with tarfile.open(args.tar_path, "r") as mytar:
            if any(member.name == new_path for member in mytar.getmembers()):
                current_directory = new_path
            else:
                return f"Ошибка: директория '{path}' не найдена."
    return f"Текущая директория: {current_directory}"

# Функция для изменения владельца файла
def chown(user, file):
    # Здесь должна быть реализация изменения владельца
    return f"Владелец файла '{file}' изменен на '{user}'."

# Функция для получения информации о системе
def uname():
    return os.uname()

# Функция для создания директории
def mkdir(directory_name):
    # Здесь должна быть реализация создания директории
    return f"Директория '{directory_name}' создана."

# Функция для выполнения команды
def command(cmd=None):
    global current_directory
    if cmd:
        command = cmd
    else:
        command = input_area.get("1.0", tk.END)[:-1]

    with tarfile.open(args.tar_path, "r") as mytar:
        if command == "ls":
            result = ls(mytar)
            log_action(args.user_name, "ls", result)  # Логируем команду ls
            write(result)
            return result

        elif command == "exit":
            log_action(args.user_name, "exit", "Exiting the shell")
            write_log_to_file()  # Сохраняем логи перед выходом
            exit()

        elif command.startswith("cd"):
            path = command.split()[1]
            result = cd(path)
            log_action(args.user_name, "cd " + path, result)  # Логируем команду cd
            write(result)
            return result

        elif command.startswith("chown"):
            parts = command.split()
            if len(parts) == 3:
                user, file = parts[1], parts[2]
                result = chown(user, file)
                log_action(args.user_name, "chown " + command, result)  # Логируем команду chown
                write(result)
                return result
            else:
                return "Ошибка: некорректный формат команды chown."

        elif command == "uname":
            result = uname()
            log_action(args.user_name, "uname", result)  # Логируем команду uname
            write(result)
            return result

        elif command.startswith("mkdir"):
            directory_name = command.split()[1]
            result = mkdir(directory_name)
            log_action(args.user_name, "mkdir " + directory_name, result)  # Логируем команду mkdir
            write(result)
            return result

        else:
            return "Ошибка: команда не распознана."

# Функция для обновления метки
def updateLabel():
    label.config(text=current_directory)

# Функция для вывода текста в текстовое поле
def write(text=""):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, text + "\n")
    text_area.config(state=tk.DISABLED)

# Функция для очистки текстового поля
def clear():
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.config(state=tk.DISABLED)

# Инициализация GUI
args = parse_arguments()
current_directory = "/"

root = tk.Tk()
root.title(f"{args.user_name}@{args.pc_name} - Эмулятор терминала")

frame = tk.Frame(root)
frame.pack()

label = tk.Label(frame, text=current_directory)
label.pack()

input_area = tk.Text(frame, height=1, width=50)
input_area.pack()

text_area = tk.Text(frame, height=15, width=50, state=tk.DISABLED)
text_area.pack()

button = tk.Button(frame, text="Выполнить", command=lambda: command())
button.pack()

root.mainloop()
