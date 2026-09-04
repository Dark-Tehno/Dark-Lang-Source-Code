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
def open(file_name, mode, encoding='UTF-8'):
    try:
        file_obj = open(file_name, mode, encoding=encoding)
        return file_obj
    except FileNotFoundError:
        raise RuntimeError(f"файл не найден: '{file_name}'")
    except PermissionError:
        raise RuntimeError(f"нет прав для открытия файла: '{file_name}'")
    except Exception as e:
        raise RuntimeError(f"не удалось открыть файл '{file_name}': {e}")

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