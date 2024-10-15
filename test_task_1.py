import sys
import task_1  # Импортируем вашу основную программу
from task_1 import *
import tarfile
import os
import json
import pytest
from datetime import datetime

# Независимые тестовые данные
tar_path = "test_archive.tar"
user_name = "test_user"
pc_name = "test_pc"
log_file = "test_log.json"


# Фикстура для создания временного tar архива
@pytest.fixture(scope="module")
def setup_tarfile(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("data")
    tar_path = os.path.join(temp_dir, "test_archive.tar")

    # Создаем tar архив с несколькими файлами и директориями
    with tarfile.open(tar_path, "w") as tar:
        for i in range(3):
            filename = os.path.join(temp_dir, f"file{i}.txt")
            with open(filename, "w") as f:
                f.write(f"test file {i}")
            tar.add(filename, arcname=f"file{i}.txt")

        os.mkdir(os.path.join(temp_dir, "dir1"))
        tar.add(os.path.join(temp_dir, "dir1"), arcname="dir1/")

    return tar_path


# Тестирование parse_arguments
def test_parse_arguments():
    sys.argv = ["task_1.py", user_name, pc_name, tar_path, log_file]
    task_1.args = task_1.parse_arguments()
    assert task_1.args.user_name == "test_user"
    assert task_1.args.pc_name == "test_pc"
    assert task_1.args.tar_path == tar_path
    assert task_1.args.log_path == log_file


# Тестирование команды ls
def test_ls(setup_tarfile):
    task_1.current_directory = "/"
    result = task_1.ls()
    assert "file0.txt" in result
    assert "file1.txt" in result
    assert "dir1/" in result


def test_ls_empty_directory():
    with tarfile.open(setup_tarfile, "a") as tar:
        tar.addfile(tarfile.TarInfo("empty_dir/"))
    task_1.current_directory = "/empty_dir"
    result = task_1.ls()
    assert "No files or directories found" in result


# Тестирование команды cd
def test_cd_valid_path(setup_tarfile):
    task_1.current_directory = "/"
    result = task_1.cd("dir1/")
    assert task_1.current_directory == "/dir1/"
    assert "Текущая директория: /dir1/" in result


def test_cd_invalid_path():
    task_1.current_directory = "/"
    result = task_1.cd("non_existing_dir")
    assert "Directory non_existing_dir not found" in result


# Тестирование команды chown
def test_chown(setup_tarfile):
    task_1.current_directory = "/"
    result = task_1.chown("new_user", "file0.txt")
    assert result == "Владелец файла 'file0.txt' изменен на 'new_user'."
    assert task_1.permissions["file0.txt"]["owner"] == "new_user"


def test_chown_invalid_file():
    result = task_1.chown("new_user", "non_existing_file.txt")
    assert "File 'non_existing_file.txt' not found" in result


# Тестирование команды uname
def test_uname():
    result = task_1.uname()
    assert os.uname().sysname in result


# Тестирование команды mkdir
def test_mkdir():
    result = task_1.mkdir("new_dir")
    assert result == "Директория 'new_dir' создана."
    assert "new_dir/" in task_1.ls()


def test_mkdir_existing_dir():
    result = task_1.mkdir("dir1")
    assert "Directory 'dir1' already exists" in result


# Тестирование команды exit
def test_exit():
    with pytest.raises(SystemExit):
        task_1.command("exit")


# Тестирование команды find
def test_find(setup_tarfile):
    result = task_1.find("file1")
    assert "file1.txt" in result


def test_find_no_results():
    result = task_1.find("non_existing_file")
    assert "No results found" in result


# Тестирование команды ls через команду
def test_command_ls(setup_tarfile):
    task_1.current_directory = "/"
    result = task_1.command("ls")
    assert "file0.txt" in result
    assert "dir1/" in result


# Тестирование команды cd через команду
def test_command_cd_valid():
    task_1.current_directory = "/"
    result = task_1.command("cd dir1/")
    assert task_1.current_directory == "/dir1/"
    assert "Текущая директория: /dir1/" in result


def test_command_cd_invalid():
    result = task_1.command("cd non_existing_dir")
    assert "Directory non_existing_dir not found" in result


# Тестирование команды chown через команду
def test_command_chown(setup_tarfile):
    result = task_1.command("chown new_user file0.txt")
    assert "Владелец файла 'file0.txt' изменен на 'new_user'" in result
    assert task_1.permissions["file0.txt"]["owner"] == "new_user"


# Тестирование команды mkdir через команду
def test_command_mkdir():
    result = task_1.command("mkdir test_dir")
    assert "Директория 'test_dir' создана." in result
    assert "test_dir/" in task_1.ls()


def test_command_mkdir_existing():
    result = task_1.command("mkdir dir1")
    assert "Directory 'dir1' already exists" in result


# Тестирование логирования действий
def test_log_action(setup_tarfile, tmp_path):
    log_path = tmp_path / "test_log.json"
    task_1.args = argparse.Namespace(user_name="test_user", log_path=log_path, tar_path=setup_tarfile)

    task_1.log_action("test_user", "ls", "test_result")
    task_1.write_log_to_file()

    # Проверяем, что лог файл был создан и содержит запись
    with open(log_path, 'r') as log_file:
        log_data = json.load(log_file)

    assert len(log_data) == 1
    assert log_data[0]["user"] == "test_user"
    assert log_data[0]["command"] == "ls"
    assert log_data[0]["result"] == "test_result"
