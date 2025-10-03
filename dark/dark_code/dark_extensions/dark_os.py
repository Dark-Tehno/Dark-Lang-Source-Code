import os as python_os
from dark_code.dark_exceptions import DarkRuntimeError


def native_os_getcwd(args):
    """Returns the current working directory."""
    if args: raise TypeError("os.getcwd() takes no arguments")
    return python_os.getcwd()

def native_os_path_exists(args):
    """Checks if a path exists. Returns True for true, False for false."""
    if len(args) != 1: raise TypeError("os.path_exists() takes 1 argument")
    return python_os.path.exists(args[0])

def native_os_mkdir(args):
    """Creates a directory."""
    if len(args) != 1: raise TypeError("os.mkdir() takes 1 argument")
    try:
        python_os.mkdir(args[0])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Could not create directory '{args[0]}': {e.strerror}")

def native_os_rmdir(args):
    """Removes a directory."""
    if len(args) != 1: raise TypeError("os.rmdir() takes 1 argument")
    try:
        python_os.rmdir(args[0])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Could not remove directory '{args[0]}': {e.strerror}")

def native_os_remove(args):
    """Removes a file."""
    if len(args) != 1: raise TypeError("os.remove() takes 1 argument")
    try:
        python_os.remove(args[0])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Could not remove file '{args[0]}': {e.strerror}")

def native_os_rename(args):
    """Renames a file or directory."""
    if len(args) != 2: raise TypeError("os.rename() takes 2 arguments")
    try:
        python_os.rename(args[0], args[1])
        return True
    except OSError as e:
        raise DarkRuntimeError(f"Could not rename '{args[0]}' to '{args[1]}': {e.strerror}")
def native_os_listdir(args):
    """Lists contents of a directory."""
    if len(args) != 1: raise TypeError("os.listdir() takes 1 argument")
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
    """Returns the size of a file."""
    if len(args) != 1: raise TypeError("os.getsize() takes 1 argument")
    path = args[0]
    try:
        return python_os.path.getsize(path)
    except FileNotFoundError:
        raise DarkRuntimeError(f"файл не найден: '{path}'")
    except OSError as e:
        raise DarkRuntimeError(f"не удалось получить размер файла '{path}': {e.strerror}")

def native_os_isdir(args):
    """Checks if a path is a directory."""
    if len(args) != 1: raise TypeError("os.isdir() takes 1 argument")
    return python_os.path.isdir(args[0])

def native_os_system(args):
    """Executes a system command."""
    if len(args) != 1: raise TypeError("os.system() takes 1 argument")
    command = args[0]
    if command == 'cls':
        command = 'cls' if python_os.name == 'nt' else 'clear'
        return python_os.system(command)
    return python_os.system(args[0])