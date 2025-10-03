import json as python_json
from dark_code.dark_exceptions import DarkRuntimeError


def native_stdlib_range(args):
    """Returns a list of numbers in the range [start, stop)."""
    if len(args) != 2: raise TypeError("stdlib.range() takes 2 arguments (start, stop)")
    start, stop = args
    if not isinstance(start, (int, float)) or not isinstance(stop, (int, float)):
        raise TypeError("Arguments for stdlib.range() must be numbers")
    return list(range(int(start), int(stop)))

def native_stdlib_list_contains(args):
    """Checks if an item is in a list."""
    if len(args) != 2: raise TypeError("stdlib.list_contains() takes 2 arguments (list, item)")
    haystack, needle = args
    if not isinstance(haystack, list):
        raise TypeError("First argument to stdlib.list_contains() must be a list")
    return needle in haystack

def native_stdlib_list_join(args):
    """Joins list elements into a string with a separator."""
    if len(args) != 2: raise TypeError("stdlib.list_join() takes 2 arguments (list, separator)")
    items, separator = args
    if not isinstance(items, list):
        raise TypeError("First argument to stdlib.list_join() must be a list")
    if not isinstance(separator, str):
        raise TypeError("Second argument to stdlib.list_join() must be a string")
    return separator.join(map(str, items))

def native_stdlib_dict_get(args):
    """Gets a value from a dictionary, with a default."""
    if len(args) != 3: raise TypeError("stdlib.dict_get() takes 3 arguments (dict, key, default)")
    d, key, default_val = args
    if not isinstance(d, dict):
        raise TypeError("First argument to stdlib.dict_get() must be a dictionary")
    return d.get(key, default_val)

def native_stdlib_clamp(args):
    """Clamps a value between a minimum and maximum."""
    if len(args) != 3: raise TypeError("stdlib.clamp() takes 3 arguments (value, min, max)")
    value, min_val, max_val = args
    if not isinstance(value, (int, float)) or not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        raise TypeError("Arguments for stdlib.clamp() must be numbers")
    return max(min_val, min(value, max_val))

def native_stdlib_json_decode(args):
    """Parses a JSON string into a dictionary or list."""
    if len(args) != 1:
        raise TypeError("stdlib.json_decode() takes 1 argument (json_string)")
    json_string = args[0]
    if not isinstance(json_string, str):
        raise TypeError("Argument to stdlib.json_decode() must be a string")
    try:
        return python_json.loads(json_string)
    except python_json.JSONDecodeError as e:
        raise DarkRuntimeError(f"неверный формат JSON: {e}")

def native_stdlib_str_split(args):
    """Splits a string by a separator."""
    if len(args) != 2: raise TypeError("stdlib.str_split() takes 2 arguments (string, separator)")
    s, sep = args
    if not isinstance(s, str) or not isinstance(sep, str):
        raise TypeError("Arguments for stdlib.str_split() must be strings")
    if sep == "":
        return list(s)
    return s.split(sep)

def native_stdlib_str_upper(args):
    """Converts a string to uppercase."""
    if len(args) != 1: raise TypeError("stdlib.str_upper() takes 1 argument (string)")
    s = args[0]
    if not isinstance(s, str):
        raise TypeError("Argument for stdlib.str_upper() must be a string")
    return s.upper()

def native_stdlib_str_lower(args):
    """Converts a string to lowercase."""
    if len(args) != 1: raise TypeError("stdlib.str_lower() takes 1 argument (string)")
    s = args[0]
    if not isinstance(s, str):
        raise TypeError("Argument for stdlib.str_lower() must be a string")
    return s.lower()

def native_stdlib_str_replace(args):
    """Replaces all occurrences of a substring with another."""
    if len(args) != 3: raise TypeError("stdlib.str_replace() takes 3 arguments (string, old, new)")
    s, old, new = args
    if not isinstance(s, str) or not isinstance(old, str) or not isinstance(new, str):
        raise TypeError("Arguments for stdlib.str_replace() must be strings")
    return s.replace(old, new)