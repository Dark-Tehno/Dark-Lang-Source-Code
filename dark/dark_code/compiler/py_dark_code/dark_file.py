from dark_code.dark_exceptions import DarkRuntimeError


def open(file_name, mode, encoding='UTF-8'):
    try:
        file_obj = open(file_name, mode, encoding=encoding)
        return file_obj
    except FileNotFoundError:
        raise DarkRuntimeError(f"файл не найден: '{file_name}'")
    except PermissionError:
        raise DarkRuntimeError(f"нет прав для открытия файла: '{file_name}'")
    except Exception as e:
        raise DarkRuntimeError(f"не удалось открыть файл '{file_name}': {e}")

def read(file_obj):
    if not hasattr(file_obj, 'read'): raise TypeError("Аргумент не является файловым объектом")
    return file_obj.read()

def write(file_obj, content):
    if not hasattr(file_obj, 'write'): raise TypeError("Первый аргумент не является файловым объектом")
    if not isinstance(content, str): raise TypeError("Содержимое для записи должно быть строкой")
    file_obj.write(content)
    return None

def close(file_obj):
    if not hasattr(file_obj, 'close'): raise TypeError("Аргумент не является файловым объектом")
    file_obj.close()
    return None

def readline(file_obj):
    if not hasattr(file_obj, 'readline'): raise TypeError("Аргумент не является файловым объектом")
    return file_obj.readline()

def readlines(file_obj):
    if not hasattr(file_obj, 'readlines'): raise TypeError("Аргумент не является файловым объектом")
    return file_obj.readlines()

def seek(file_obj, offset):
    if not hasattr(file_obj, 'seek'): raise TypeError("Первый аргумент не является файловым объектом")
    if not isinstance(offset, int): raise TypeError("Смещение должно быть целым числом")
    file_obj.seek(offset)
    return None