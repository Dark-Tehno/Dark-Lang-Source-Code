import random as python_random
from dark_code.dark_extensions.gui import *
from dark_code.dark_extensions.dark_color import *
from dark_code.dark_extensions.dark_http import *
from dark_code.dark_extensions.dark_math import *
from dark_code.dark_extensions.dark_os import *
from dark_code.dark_extensions.dark_stdlib import *
from dark_code.dark_extensions.dark_time import *
from dark_code.dark_extensions.dark_vsp210 import *
from dark_code.dark_extensions.dark_file import *


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
