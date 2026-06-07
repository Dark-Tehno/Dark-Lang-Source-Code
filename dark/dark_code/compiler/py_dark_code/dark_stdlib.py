import json as python_json


def range(start, stop):
    """Возвращает список чисел в диапазоне [start, stop)."""
    if not isinstance(start, (int, float)) or not isinstance(stop, (int, float)):
        raise TypeError("Аргументами для stdlib.range() должны быть числа")
    return list(range(int(start), int(stop)))

def list_contains(haystack, needle):
    """Проверяет, есть ли элемент в списке."""
    if not isinstance(haystack, list):
        raise TypeError("Первым аргументом stdlib.list_contains() должен быть список")
    return needle in haystack

def list_join(items, separator):
    """Объединяет элементы списка в строку с помощью разделителя."""
    if not isinstance(items, list):
        raise TypeError("Первым аргументом stdlib.list_join() должен быть список")
    if not isinstance(separator, str):
        raise TypeError("Второй аргумент stdlib.list_join() должен быть строкой")
    return separator.join(map(str, items))

def dict_get(d, key, default_val):
    """Получает значение из словаря с значением по умолчанию."""
    if not isinstance(d, dict):
        raise TypeError("Первым аргументом stdlib.dict_get() должен быть словарь")
    return d.get(key, default_val)

def clamp(value, min_val, max_val):
    """Фиксирует значение между минимальным и максимальным."""
    if not isinstance(value, (int, float)) or not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        raise TypeError("Аргументами для stdlib.clamp() должны быть числа")
    return max(min_val, min(value, max_val))

def json_decode(json_string):
    """Преобразует строку JSON в словарь или список."""
    if not isinstance(json_string, str):
        raise TypeError("Аргумент для stdlib.json_decode() должен быть строкой")
    try:
        return python_json.loads(json_string)
    except python_json.JSONDecodeError as e:
        raise RuntimeError(f"неверный формат JSON: {e}")

def str_split(s, sep):
    """Разбивает строку на разделители."""
    if not isinstance(s, str) or not isinstance(sep, str):
        raise TypeError("Аргументы для stdlib.str_split() должны быть строками")
    if sep == "":
        return list(s)
    return s.split(sep)

def str_upper(s):
    """Преобразует строку в верхний регистр."""
    if not isinstance(s, str):
        raise TypeError("Аргумент для stdlib.str_upper() должен быть строкой")
    return s.upper()

def str_lower(s):
    """Преобразует строку в нижний регистр."""
    if not isinstance(s, str):
        raise TypeError("Аргумент для stdlib.str_lower() должен быть строкой")
    return s.lower()

def str_replace(s, old, new):
    """Заменяет все вхождения подстроки на другие."""
    if not isinstance(s, str) or not isinstance(old, str) or not isinstance(new, str):
        raise TypeError("Аргументы для stdlib.str_replace() должны быть строками")
    return s.replace(old, new)