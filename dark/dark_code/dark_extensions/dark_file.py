from dark_code.dark_exceptions import DarkRuntimeError


def native_file_open(args):
    if len(args) < 2: raise TypeError("file.open() принимает как минимум 2 аргумента (имя_файла, режим) и необязательный аргумент кодировки.")
    if len(args) == 2:
        file_name = args[0]
        mode = args[1]
        encoding = None
    elif len(args) == 3:
        file_name = args[0]
        mode = args[1]
        encoding = args[2]
    else:
        raise TypeError("file.open() принимает 2 или 3 аргумента.")

    try:
        file_obj = open(file_name, mode, encoding=encoding)
        return file_obj
    except FileNotFoundError:
        raise DarkRuntimeError(f"файл не найден: '{file_name}'")
    except PermissionError:
        raise DarkRuntimeError(f"нет прав для открытия файла: '{file_name}'")
    except Exception as e:
        raise DarkRuntimeError(f"не удалось открыть файл '{file_name}': {e}")

def native_file_read(args):
    if len(args) != 1: raise TypeError("file.read() takes 1 argument (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'read'): raise TypeError("Argument is not a file object")
    return file_obj.read()

def native_file_write(args):
    if len(args) != 2: raise TypeError("file.write() takes 2 arguments (file_object, content)")
    file_obj, content = args
    if not hasattr(file_obj, 'write'): raise TypeError("First argument is not a file object")
    if not isinstance(content, str): raise TypeError("Content to write must be a string")
    file_obj.write(content)
    return None

def native_file_close(args):
    if len(args) != 1: raise TypeError("file.close() takes 1 argument (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'close'): raise TypeError("Argument is not a file object")
    file_obj.close()
    return None

def native_file_readline(args):
    if len(args) != 1: raise TypeError("file.readline() takes 1 argument (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'readline'): raise TypeError("Argument is not a file object")
    return file_obj.readline()

def native_file_readlines(args):
    if len(args) != 1: raise TypeError("file.readlines() takes 1 argument (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'readlines'): raise TypeError("Argument is not a file object")
    return file_obj.readlines()

def native_file_seek(args):
    if len(args) != 2: raise TypeError("file.seek() takes 2 arguments (file_object, offset)")
    file_obj, offset = args
    if not hasattr(file_obj, 'seek'): raise TypeError("First argument is not a file object")
    if not isinstance(offset, int): raise TypeError("Offset must be an integer")
    file_obj.seek(offset)
    return None