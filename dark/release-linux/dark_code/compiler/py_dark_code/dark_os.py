# Copyright 2026 Dark.Tehno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os as python_os
import sys

def getcwd():
    """Возвращает текущий рабочий каталог."""
    return python_os.getcwd()

def path_exists(path):
    """Проверяет, существует ли путь. Возвращает значение True для значения true и значение False для значения false."""
    return python_os.path.exists(path)

def mkdir(path):
    """Создает каталог."""
    try:
        python_os.mkdir(path)
        return True
    except OSError as e:
        raise RuntimeError(f"Не удалось создать каталог '{path}': {e.strerror}")

def rmdir(path):
    """Удаляет каталог."""
    try:
        python_os.rmdir(path)
        return True
    except OSError as e:
        raise RuntimeError(f"Не удалось удалить каталог '{path}': {e.strerror}")

def remove(file):
    """Удаляет файл."""
    try:
        python_os.remove(file)
        return True
    except OSError as e:
        raise RuntimeError(f"Не удалось удалить файл '{file}': {e.strerror}")

def rename(old_name, new_name):
    """Переименовывает файл или каталог."""
    try:
        python_os.rename(old_name, new_name)
        return True
    except OSError as e:
        raise RuntimeError(f"Не удалось переименовать '{old_name}' в '{new_name}': {e.strerror}")
    
def listdir(path):
    """Отображает содержимое каталога."""
    try:
        return python_os.listdir(path)
    except FileNotFoundError:
        raise RuntimeError(f"директория не найдена: '{path}'")
    except NotADirectoryError:
        raise RuntimeError(f"путь не является директорией: '{path}'")
    except OSError as e:
        raise RuntimeError(f"не удалось получить список файлов в директории '{path}': {e.strerror}")

def getsize(file):
    """Возвращает размер файла."""
    try:
        return python_os.path.getsize(file)
    except FileNotFoundError:
        raise RuntimeError(f"файл не найден: '{file}'")
    except OSError as e:
        raise RuntimeError(f"не удалось получить размер файла '{file}': {e.strerror}")

def isdir(path):
    """Проверяет, является ли путь каталогом."""
    return python_os.path.isdir(path)

def system(command):
    """Выполняет системную команду."""
    command = command
    if command == 'cls':
        command = 'cls' if python_os.name == 'nt' else 'clear'
        return python_os.system(command)
    return python_os.system(command)

def exit():
    """Выход из программы."""
    sys.exit()