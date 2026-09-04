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
    if len(args) != 1: raise TypeError("file.read() принимает 1 аргумент (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'read'): raise TypeError("Аргумент не является файловым объектом")
    return file_obj.read()

def native_file_write(args):
    if len(args) != 2: raise TypeError("file.write() принимает 2 аргумента (file_object, content)")
    file_obj, content = args
    if not hasattr(file_obj, 'write'): raise TypeError("Первый аргумент не является файловым объектом")
    if not isinstance(content, str): raise TypeError("Содержимое для записи должно быть строкой")
    file_obj.write(content)
    return None

def native_file_close(args):
    if len(args) != 1: raise TypeError("file.close() принимает 1 аргумент (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'close'): raise TypeError("Аргумент не является файловым объектом")
    file_obj.close()
    return None

def native_file_readline(args):
    if len(args) != 1: raise TypeError("file.readline() принимает 1 аргумент (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'readline'): raise TypeError("Аргумент не является файловым объектом")
    return file_obj.readline()

def native_file_readlines(args):
    if len(args) != 1: raise TypeError("file.readlines() принимает 1 аргумент (file_object)")
    file_obj = args[0]
    if not hasattr(file_obj, 'readlines'): raise TypeError("Аргумент не является файловым объектом")
    return file_obj.readlines()

def native_file_seek(args):
    if len(args) != 2: raise TypeError("file.seek() принимает 2 аргумента (file_object, offset)")
    file_obj, offset = args
    if not hasattr(file_obj, 'seek'): raise TypeError("Первый аргумент не является файловым объектом")
    if not isinstance(offset, int): raise TypeError("Смещение должно быть целым числом")
    file_obj.seek(offset)
    return None