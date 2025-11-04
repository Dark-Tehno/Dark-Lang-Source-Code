import os as python_os
from dark_code.dark_exceptions import DarkRuntimeError


def native_os_getcwd(args):
    """Возвращает текущий рабочий каталог."""
    if args: raise TypeError("os.getcwd() не принимает никаких аргументов")
    return python_os.getcwd()

def native_os_path_exists(args):
    """Проверяет, существует ли путь. Возвращает значение True для значения true и значение False для значения false."""
    if len(args) != 1: raise TypeError("os.path_exists() принимает 1 аргумент")
    return python_os.path.exists(args[0])

def native_os_mkdir(args):
    """Создает каталог."""
    if len(args) != 1: raise TypeError("os.mkdir() принимает 1 аргумент")
    try:
        python_os.mkdir(args[0])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Не удалось создать каталог '{args[0]}': {e.strerror}")

def native_os_rmdir(args):
    """Удаляет каталог."""
    if len(args) != 1: raise TypeError("os.rmdir() принимает 1 аргумент")
    try:
        python_os.rmdir(args[0])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Не удалось удалить каталог '{args[0]}': {e.strerror}")

def native_os_remove(args):
    """Удаляет файл."""
    if len(args) != 1: raise TypeError("os.remove() принимает 1 аргумент")
    try:
        python_os.remove(args[0])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Не удалось удалить файл '{args[0]}': {e.strerror}")

def native_os_rename(args):
    """Переименовывает файл или каталог."""
    if len(args) != 2: raise TypeError("os.rename() takes 2 arguments")
    try:
        python_os.rename(args[0], args[1])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Не удалось переименовать '{args[0]}' в '{args[1]}': {e.strerror}")
    
def native_os_listdir(args):
    """Отображает содержимое каталога."""
    if len(args) != 1: raise TypeError("os.listdir() принимает 1 аргумент")
    path = args[0]
    try:
        return python_os.listdir(path)
    except FileNotFoundError:
        raise DarkRuntimeError(f"директория не найдена: '{path}'")
    except NotADirectoryError:
        raise DarkRuntimeError(f"путь не является директорией: '{path}'")
    except OSError as e:
        raise DarkRuntimeError(f"не удалось получить список файлов в директории '{path}': {e.strerror}")

def native_os_getsize(args):
    """Возвращает размер файла."""
    if len(args) != 1: raise TypeError("os.getsize() принимает 1 аргумент")
    path = args[0]
    try:
        return python_os.path.getsize(path)
    except FileNotFoundError:
        raise DarkRuntimeError(f"файл не найден: '{path}'")
    except OSError as e:
        raise DarkRuntimeError(f"не удалось получить размер файла '{path}': {e.strerror}")

def native_os_isdir(args):
    """Проверяет, является ли путь каталогом."""
    if len(args) != 1: raise TypeError("os.isdir() принимает 1 аргумент")
    return python_os.path.isdir(args[0])

def native_os_system(args):
    """Выполняет системную команду."""
    if len(args) != 1: raise TypeError("os.system() принимает 1 аргумент")
    command = args[0]
    if command == 'cls':
        command = 'cls' if python_os.name == 'nt' else 'clear'
        return python_os.system(command)
    return python_os.system(args[0])