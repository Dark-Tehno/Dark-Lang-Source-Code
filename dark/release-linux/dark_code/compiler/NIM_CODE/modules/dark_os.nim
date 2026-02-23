# import os as python_os
# from dark_code.dark_exceptions import DarkRuntimeError

import os
from ../dark/exceptions import DarkRuntimeError, formatError


# def native_os_getcwd(args):
#     """Возвращает текущий рабочий каталог."""
#     if args: raise TypeError("os.getcwd() не принимает никаких аргументов")
#     return python_os.getcwd()
proc getcwd*(): string =
  return os.getCurrentDir()
  
# def native_os_path_exists(args):
#     """Проверяет, существует ли путь. Возвращает значение True для значения true и значение False для значения false."""
#     if len(args) != 1: raise TypeError("os.path_exists() принимает 1 аргумент")
#     return python_os.path.exists(args[0])
proc exists*(path: string): bool =
  # В Nim нет прямого аналога os.path.exists, но можно проверить fileExists или dirExists
  return os.fileExists(path) or os.dirExists(path)

# def native_os_mkdir(args):
#     """Создает каталог."""
#     if len(args) != 1: raise TypeError("os.mkdir() принимает 1 аргумент")
#     try:
#         python_os.mkdir(args[0])
#         return True
#     except OSError as e:
#         raise DarkRuntimeError(f"Не удалось создать каталог '{args[0]}': {e.strerror}")
proc mkdir*(path: string): bool =
  try:
    os.createDir(path)
    return true
  except OSError as exc:
    var message = "Не удалось создать каталог '" & path & "': " & exc.msg
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    return false

# def native_os_rmdir(args):
#     """Удаляет каталог."""
#     if len(args) != 1: raise TypeError("os.rmdir() принимает 1 аргумент")
#     try:
#         python_os.rmdir(args[0])
#         return True
#     except OSError as e:
#         raise DarkRuntimeError(f"Не удалось удалить каталог '{args[0]}': {e.strerror}")
proc rmdir*(path: string): bool =
  try:
    os.removeDir(path)
    return true
  except OSError as exc:
    var message = "Не удалось удалить каталог '" & path & "': " & exc.msg
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    return false

# def native_os_remove(args):
#     """Удаляет файл."""
#     if len(args) != 1: raise TypeError("os.remove() принимает 1 аргумент")
#     try:
#         python_os.remove(args[0])
#         return True
#     except OSError as e:
#         raise DarkRuntimeError(f"Не удалось удалить файл '{args[0]}': {e.strerror}")
proc remove*(path: string): bool =
  try:
    os.removeFile(path)
    return true
  except OSError as exc:
    var message = "Не удалось удалить файл '" & path & "': " & exc.msg
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    return false

# def native_os_rename(args):
#     """Переименовывает файл или каталог."""
#     if len(args) != 2: raise TypeError("os.rename() takes 2 arguments")
#     try:
#         python_os.rename(args[0], args[1])
#        return True
#     except OSError as e:
#         raise DarkRuntimeError(f"Не удалось переименовать '{args[0]}' в '{args[1]}': {e.strerror}")
proc rename*(src: string, dest: string): bool =
  try:
    os.moveFile(src, dest)
    return true
  except OSError as exc:
    var message = "Не удалось переименовать '" & src & "' в '" & dest & "': " & exc.msg
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    return false
    
# def native_os_listdir(args):
#     """Отображает содержимое каталога."""
#     if len(args) != 1: raise TypeError("os.listdir() принимает 1 аргумент")
#     path = args[0]
#     try:
#         return python_os.listdir(path)
#     except FileNotFoundError:
#         raise DarkRuntimeError(f"директория не найдена: '{path}'")
#     except NotADirectoryError:
#         raise DarkRuntimeError(f"путь не является директорией: '{path}'")
#     except OSError as e:
#         raise DarkRuntimeError(f"не удалось получить список файлов в директории '{path}': {e.strerror}")
proc listdir*(path: string): seq[string] =
  try:
    for kind, file in os.walkDir(path):
      result.add(os.extractFilename(file))
  except OSError as exc:
    var message = "не удалось получить список файлов в директории '" & path & "': " & exc.msg
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    return @[]

# def native_os_getsize(args):
#     """Возвращает размер файла."""
#     if len(args) != 1: raise TypeError("os.getsize() принимает 1 аргумент")
#     path = args[0]
#     try:
#         return python_os.path.getsize(path)
#     except FileNotFoundError:
#         raise DarkRuntimeError(f"файл не найден: '{path}'")
#     except OSError as e:
#         raise DarkRuntimeError(f"не удалось получить размер файла '{path}': {e.strerror}")
proc getsize*(path: string): int64 =
  try:
    return os.getFileSize(path)
  except OSError as exc:
    var message = "не удалось получить размер файла '" & path & "': " & exc.msg
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    return -1

# def native_os_isdir(args):
#     """Проверяет, является ли путь каталогом."""
#     if len(args) != 1: raise TypeError("os.isdir() принимает 1 аргумент")
#     return python_os.path.isdir(args[0])
proc isdir*(path: string): bool =
  return os.dirExists(path)

# def native_os_system(args):
#     """Выполняет системную команду."""
#     if len(args) != 1: raise TypeError("os.system() принимает 1 аргумент")
#     command = args[0]
#     if command == 'cls':
#         command = 'cls' if python_os.name == 'nt' else 'clear'
#         return python_os.system(command)
#     return python_os.system(args[0])
proc system*(command: string): int =
  var cmd = command
  if cmd == "cls":
    when defined(windows):
      cmd = "cls"
    else:
      cmd = "clear"
  try:
    return os.execShellCmd(cmd)
  except OSError as exc:
    var message = "не удалось выполнить команду '" & cmd & "': " & exc.msg
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    return -1