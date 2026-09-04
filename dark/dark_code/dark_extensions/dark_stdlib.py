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
import json as python_json
from dark_code.dark_exceptions import DarkRuntimeError


def native_stdlib_range(args):
    """Возвращает список чисел в диапазоне [start, stop)."""
    if len(args) != 2: raise TypeError("stdlib.range() принимает 2 аргумента (start, stop)")
    start, stop = args
    if not isinstance(start, (int, float)) or not isinstance(stop, (int, float)):
        raise TypeError("Аргументами для stdlib.range() должны быть числа")
    return list(range(int(start), int(stop)))

def native_stdlib_list_contains(args):
    """Проверяет, есть ли элемент в списке."""
    if len(args) != 2: raise TypeError("stdlib.list_contains() принимает 2 аргумента (list, item)")
    haystack, needle = args
    if not isinstance(haystack, list):
        raise TypeError("Первым аргументом stdlib.list_contains() должен быть список")
    return needle in haystack

def native_stdlib_list_join(args):
    """Объединяет элементы списка в строку с помощью разделителя."""
    if len(args) != 2: raise TypeError("stdlib.list_join() принимает 2 аргумента (list, separator)")
    items, separator = args
    if not isinstance(items, list):
        raise TypeError("Первым аргументом stdlib.list_join() должен быть список")
    if not isinstance(separator, str):
        raise TypeError("Второй аргумент stdlib.list_join() должен быть строкой")
    return separator.join(map(str, items))

def native_stdlib_dict_get(args):
    """Получает значение из словаря с значением по умолчанию."""
    if len(args) != 3: raise TypeError("stdlib.dict_get() принимает 3 аргумента (dict, key, default)")
    d, key, default_val = args
    if not isinstance(d, dict):
        raise TypeError("Первым аргументом stdlib.dict_get() должен быть словарь")
    return d.get(key, default_val)

def native_stdlib_clamp(args):
    """Фиксирует значение между минимальным и максимальным."""
    if len(args) != 3: raise TypeError("stdlib.clamp() принимает 3 аргумента (value, min, max)")
    value, min_val, max_val = args
    if not isinstance(value, (int, float)) or not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        raise TypeError("Аргументами для stdlib.clamp() должны быть числа")
    return max(min_val, min(value, max_val))

def native_stdlib_json_decode(args):
    """Преобразует строку JSON в словарь или список."""
    if len(args) != 1:
        raise TypeError("stdlib.json_decode() принимает 1 аргумент (json_string)")
    json_string = args[0]
    if not isinstance(json_string, str):
        raise TypeError("Аргумент для stdlib.json_decode() должен быть строкой")
    try:
        return python_json.loads(json_string)
    except python_json.JSONDecodeError as e:
        raise DarkRuntimeError(f"неверный формат JSON: {e}")

def native_stdlib_str_split(args):
    """Разбивает строку на разделители."""
    if len(args) != 2: raise TypeError("stdlib.str_split() принимает 2 аргумента (string, separator)")
    s, sep = args
    if not isinstance(s, str) or not isinstance(sep, str):
        raise TypeError("Аргументы для stdlib.str_split() должны быть строками")
    if sep == "":
        return list(s)
    return s.split(sep)

def native_stdlib_str_upper(args):
    """Преобразует строку в верхний регистр."""
    if len(args) != 1: raise TypeError("stdlib.str_upper() принимает 1 аргумент (string)")
    s = args[0]
    if not isinstance(s, str):
        raise TypeError("Аргумент для stdlib.str_upper() должен быть строкой")
    return s.upper()

def native_stdlib_str_lower(args):
    """Преобразует строку в нижний регистр."""
    if len(args) != 1: raise TypeError("stdlib.str_lower() принимает 1 аргумент (string)")
    s = args[0]
    if not isinstance(s, str):
        raise TypeError("Аргумент для stdlib.str_lower() должен быть строкой")
    return s.lower()

def native_stdlib_str_replace(args):
    """Заменяет все вхождения подстроки на другие."""
    if len(args) != 3: raise TypeError("stdlib.str_replace() принимает 3 аргумента (string, old, new)")
    s, old, new = args
    if not isinstance(s, str) or not isinstance(old, str) or not isinstance(new, str):
        raise TypeError("Аргументы для stdlib.str_replace() должны быть строками")
    return s.replace(old, new)