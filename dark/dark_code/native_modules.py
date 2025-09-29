import os as python_os
import math as python_math
import random as python_random
import time as python_time
import json as python_json
import sys 
from urllib import request, error
import webbrowser

from dark_code.dark_extensions.gui import *
from dark_code.dark_exceptions import DarkRuntimeError, DarkSyntaxError


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
        # Make 'cls' cross-platform
        command = 'cls' if python_os.name == 'nt' else 'clear'
        return python_os.system(command)
    return python_os.system(args[0])


def native_math_sqrt(args):
    """Calculates the square root of a number."""
    if len(args) != 1: raise TypeError("math.sqrt() takes 1 argument")
    return python_math.sqrt(args[0])

def native_math_pow(args):
    """Calculates base to the power of exp."""
    if len(args) != 2: raise TypeError("math.pow() takes 2 arguments")
    return python_math.pow(args[0], args[1])

def native_math_floor(args):
    """Returns the floor of a number."""
    if len(args) != 1: raise TypeError("math.floor() takes 1 argument")
    return python_math.floor(args[0])

def native_math_ceil(args):
    """Returns the ceiling of a number."""
    if len(args) != 1: raise TypeError("math.ceil() takes 1 argument")
    return python_math.ceil(args[0])

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

def native_time_time(args):
    """Returns the current time in seconds since the Epoch."""
    if args: raise TypeError("time.time() takes no arguments")
    return python_time.time()

def native_time_sleep(args):
    """Sleeps for a specified number of seconds."""
    if len(args) != 1: raise TypeError("time.sleep() takes 1 argument (seconds)")
    seconds = args[0]
    if not isinstance(seconds, (int, float)):
        raise TypeError("Argument for time.sleep() must be a number")
    sys.stdout.flush()
    python_time.sleep(seconds)
    return None

def native_http_get(args):
    """Performs an HTTP GET request and returns a dictionary with status_code, headers, and body."""
    if len(args) != 1:
        raise TypeError("http.get() takes exactly 1 argument (url)")
    
    url = args[0]
    if not isinstance(url, str):
        raise TypeError("Argument to http.get() must be a string")

    try:
        with request.urlopen(url, timeout=10) as response:
            headers = {key: value for key, value in response.getheaders()}
            return {
                "status_code": response.status,
                "headers": headers,
                "body": response.read().decode('utf-8', errors='ignore')
            }
    except error.HTTPError as e:
        headers = {key: value for key, value in e.headers.items()}
        return {
            "status_code": e.code,
            "headers": headers,
            "body": e.read().decode('utf-8', errors='ignore')
        }
    except error.URLError as e:
        return {
            "status_code": -1, 
            "headers": {},
            "body": str(e.reason)
        }
    
def native_http_post(args):
    """Performs an HTTP POST request and returns a dictionary with status_code, headers, and body."""
    if len(args) not in [2, 3]:
        raise TypeError("http.post() takes 2 or 3 arguments (url, data, headers_dict_optional)")
    
    url = args[0]
    data = args[1]
    headers = {}
    if len(args) == 3:
        if not isinstance(args[2], dict):
            raise TypeError("Optional third argument to http.post() must be a dictionary of headers")
        headers = args[2]

    if not isinstance(url, str):
        raise TypeError("First argument to http.post() (url) must be a string")
    if not isinstance(data, str):
        raise TypeError("Second argument to http.post() (data) must be a string")

    try:
        req = request.Request(url, data=data.encode('utf-8'), headers=headers, method='POST')
        with request.urlopen(req, timeout=10) as response:
            response_headers = {key: value for key, value in response.getheaders()}
            return {
                "status_code": response.status,
                "headers": response_headers,
                "body": response.read().decode('utf-8', errors='ignore')
            }
    except error.HTTPError as e:
        headers = {key: value for key, value in e.headers.items()}
        return {
            "status_code": e.code,
            "headers": headers,
            "body": e.read().decode('utf-8', errors='ignore')
        }
    except error.URLError as e:
        return {
            "status_code": -1, 
            "headers": {},
            "body": str(e.reason)
        }

def native_math_pi(args):
    """Returns the value of PI."""
    if args: raise TypeError("math.pi() takes no arguments")
    return python_math.pi

def native_math_random(args):
    """Returns a random float between 0.0 and 1.0."""
    if args: raise TypeError("math.random() takes no arguments")
    return python_random.random()

def _run_internal_script(script_name):
    """Helper to run internal .dark scripts."""
    from dark_code.dark_lang import Parser, lex, run 

    if getattr(sys, 'frozen', False):
        base_dir = python_os.path.dirname(sys.executable)
        file_path = python_os.path.join(base_dir, "code", f"{script_name}.dark") # Используем os.path.join
    else:
        base_dir = python_os.path.dirname(python_os.path.abspath(__file__))
        file_path = python_os.path.join(base_dir, '..', "code", f"{script_name}.dark") # Используем os.path.join

    if not python_os.path.exists(file_path):
        raise DarkRuntimeError(f"внутренний скрипт '{script_name}.dark' не найден.")

    script_dir_for_run = python_os.path.dirname(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        src = f.read()

    tokens = lex(src)
    parser = Parser(tokens)
    ast = parser.parse()
    if parser.errors:
        raise parser.errors[0]
        
    run(ast, script_dir=script_dir_for_run)

def philosophy(args):
    """Запуск секретного файла dark о философии языка."""
    if args: raise TypeError("vsp210.philosophy() не принимает аргументов")
    _run_internal_script("philosophy")

def history(args):
    """Запуск секретного файла dark об истории языка."""
    if args: raise TypeError("vsp210.history() не принимает аргументов")
    _run_internal_script("history")

def calculator(args):
    """Запуск калькулятора, написанного на Dark."""
    if args: raise TypeError("vsp210.calculator() не принимает аргументов")
    _run_internal_script("calculator")

def version(args):
    return "0.3.2"

def docs(args):
    if args: raise TypeError("docs() takes no arguments")
    webbrowser.open("https://vsp210.ru/dark-lang/")
    return "Докментация по языку Dark"

def telegram(args):
    if args: raise TypeError("telegram() takes no arguments")
    webbrowser.open("https://t.me/vsp210_official/")
    return "Телеграм канал создателя языка Dark"

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

# 0.3.1:
def native_python_exec(args, env):
    """
    Выполняет строку кода Python.
    Принимает 1 аргумент: строку с кодом.
    Возвращает словарь с локальными переменными после выполнения.
    """
    if len(args) != 1:
        raise TypeError("python_exec() takes exactly 1 argument (string)")
    code = args[0]
    if not isinstance(code, str):
        raise TypeError("Argument to python_exec() must be a string")
    
    exec_globals = dict(env)
    exec(code, exec_globals)
    for k, v in exec_globals.items():
        if k == '__builtins__': 
            continue
        if k.startswith('__') and k != '__current_self__':
            continue
        env[k] = v
    return exec_globals

def color(args, color_name):
    if len(args) >= 1: 
        text = args[0]
    else:
        text = ""
    # color to anci
    COLOR_CODES = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'white': '\033[97m',
        'black': '\033[30m',
        'orange': '\033[38;5;208m',
        'purple': '\033[38;5;93m',
        'pink': '\033[38;5;206m',
        'brown': '\033[38;5;94m',
        'gray': '\033[90m',
        'light_gray': '\033[37m',
        'dark_gray': '\033[38;5;240m',
        'light_blue': '\033[38;5;111m',
        'light_green': '\033[38;5;151m',
        'light_cyan': '\033[38;5;159m',
        'light_red': '\033[38;5;204m',
        'light_magenta': '\033[38;5;201m',
        'dark_red': '\033[38;5;88m',
        'dark_green': '\033[38;5;22m',
        'dark_blue': '\033[38;5;20m',
        'dark_yellow': '\033[38;5;178m',
        'dark_cyan': '\033[38;5;30m',
        'dark_magenta': '\033[38;5;53m',
    }
    RESET_CODE = '\033[0m'
    
    if color_name in COLOR_CODES:
        return COLOR_CODES[color_name] + text + RESET_CODE
    else:
        raise DarkRuntimeError(f"Unsupported color: {color_name}")

def rgb_color(args):
    if len(args) != 4: raise TypeError("rgb() takes 3 arguments (r, g, b, text)")
    r, g, b, text = args
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise TypeError("RGB components must be integers")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
        raise TypeError("RGB components must be integers between 0 and 255")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def rgba_color(args):
    if len(args) != 5: raise TypeError("rgba() takes 4 arguments (r, g, b, a, text)")
    r, g, b, a, text = args
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
        raise TypeError("RGB components must be integers between 0 and 255")
    if not isinstance(a, (int, float)) or not (0 <= a <= 1):
        raise TypeError("Alpha component must be a number between 0 and 1")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    # ANSI escape codes do not directly support alpha for foreground colors in most terminals.
    # We'll just use the RGB color.
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def hex_color(args):
    if len(args) != 2: raise TypeError("hex() takes 2 arguments (hex_code, text)")
    hex_code, text = args
    if not isinstance(hex_code, str):
        raise TypeError("Hex code must be a string")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    hex_code = hex_code.lstrip('#')
    if hex_code.lower().startswith('0x'):
        hex_code = hex_code[2:]

    if len(hex_code) == 3:
        hex_code = ''.join([c*2 for c in hex_code])
    if len(hex_code) != 6:
        raise DarkRuntimeError("Invalid hex code format. Expected 3 or 6 characters.")
    
    try:
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
    except ValueError:
        raise DarkRuntimeError("Invalid hex code value.")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def hsl_color(args):
    if len(args) != 4: raise TypeError("hsl() takes 3 arguments (h, s, l, text)")
    h, s, l, text = args
    if not all(isinstance(c, (int, float)) for c in [h, s, l]):
        raise TypeError("HSL components must be numbers")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    if not (0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100):
        raise DarkRuntimeError("HSL values out of range: h (0-360), s (0-100), l (0-100)")

    s /= 100
    l /= 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    
    r, g, b = 0, 0, 0
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x

    r = round((r + m) * 255)
    g = round((g + m) * 255)
    b = round((b + m) * 255)

    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

NATIVE_MODULES = {
    'os': {
        'getcwd': native_os_getcwd,
        'path_exists': native_os_path_exists,
        'mkdir': native_os_mkdir,
        'rmdir': native_os_rmdir,
        'remove': native_os_remove,
        'rename': native_os_rename,
        'listdir': native_os_listdir,
        'getsize': native_os_getsize,
        'isdir': native_os_isdir,
        'exit': lambda args: sys.exit(),
        'system': native_os_system
    },
    'math': {
        'sqrt': native_math_sqrt,
        'pow': native_math_pow,
        'floor': native_math_floor,
        'ceil': native_math_ceil,
        'pi': native_math_pi,
        'random': native_math_random,
        'randint': lambda args: python_random.randint(*args),
    },
    'stdlib': {
        'range': native_stdlib_range,
        'list_contains': native_stdlib_list_contains,
        'list_join': native_stdlib_list_join,
        'dict_get': native_stdlib_dict_get,
        'clamp': native_stdlib_clamp,
        'json_decode': native_stdlib_json_decode,        
        'str_split': native_stdlib_str_split,
        'str_upper': native_stdlib_str_upper,
        'str_lower': native_stdlib_str_lower,
        'str_replace': native_stdlib_str_replace,
    },
    'http': {
        'get': native_http_get,
        'post': native_http_post,
    },
    'time': {
        'time': native_time_time,
        'sleep': native_time_sleep,
    },
    'vsp210': {
        'philosophy': philosophy,
        'history': history,
        'calculator': calculator,
        'version': version,
        'docs': docs,
        'telegram': telegram,
    },
    'file': {
        'open': native_file_open,
        'read': native_file_read,
        'write': native_file_write,
        'close': native_file_close,
        'readline': native_file_readline,
        'readlines': native_file_readlines,
        'seek': native_file_seek,
    },
    'gui': {
        'create_window': native_gui_create_window, 'create_label': native_gui_create_label,
        'create_button': native_gui_create_button, 'create_entry': native_gui_create_entry,
        'set_text': native_gui_set_text, 'get_text': native_gui_get_text,
        'check_events': native_gui_check_events, 'stop': native_gui_stop,
    },
    # 0.3.1:
    'color': {
        'rgb': rgb_color,
        'rgba': rgba_color,
        'hex': hex_color,
        'hsl': hsl_color,

        'red': lambda args: color(args, 'red'),
        'green': lambda args: color(args, 'green'),
        'blue': lambda args: color(args, 'blue'),
        'yellow': lambda args: color(args, 'yellow'),
        'cyan': lambda args: color(args, 'cyan'),
        'magenta': lambda args: color(args, 'magenta'),
        'white': lambda args: color(args, 'white'),
        'black': lambda args: color(args, 'black'),
        'orange': lambda args: color(args, 'orange'),
        'purple': lambda args: color(args, 'purple'),
        'pink': lambda args: color(args, 'pink'),
        'brown': lambda args: color(args, 'brown'),
        'gray': lambda args: color(args, 'gray'),
        'light_gray': lambda args: color(args, 'light_gray'),
        'dark_gray': lambda args: color(args, 'dark_gray'),
        'light_blue': lambda args: color(args, 'light_blue'),
        'light_green': lambda args: color(args, 'light_green'),
        'light_cyan': lambda args: color(args, 'light_cyan'),
        'light_red': lambda args: color(args, 'light_red'),
        'light_magenta': lambda args: color(args, 'light_magenta'),
        'dark_red': lambda args: color(args, 'dark_red'),
        'dark_green': lambda args: color(args, 'dark_green'),
        'dark_blue': lambda args: color(args, 'dark_blue'),
        'dark_yellow': lambda args: color(args, 'dark_yellow'),
        'dark_cyan': lambda args: color(args, 'dark_cyan'),
        'dark_magenta': lambda args: color(args, 'dark_magenta'),
    }
}
