import os as python_os
import sys
import webbrowser
from dark_code.dark_exceptions import DarkRuntimeError


def _run_internal_script(script_name, dark_root_dir):
    """Помощник для запуска внутренних скриптов .dark."""
    from dark_code.dark_lang import Parser, lex, run 

    # Надежный способ определить, что код скомпилирован Nuitka.
    # 'in globals()' проверяет, существует ли переменная __compiled__ в текущем модуле.
    IS_COMPILED = "__compiled__" in globals()
    if IS_COMPILED:
        # Для скомпилированного приложения корень - это папка с .exe
        base_dir = python_os.path.dirname(sys.executable)
        file_path = python_os.path.join(base_dir, "code", f"{script_name}.dark")
    else:
        # Для запуска из исходников, поднимаемся на уровень выше от папки dark_extensions
        base_dir = python_os.path.dirname(python_os.path.abspath(__file__))
        file_path = python_os.path.join(base_dir, '..', '..', "code", f"{script_name}.dark")

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
        
    run(ast, script_dir=script_dir_for_run, dark_root_dir=dark_root_dir)

def philosophy(args, dark_root_dir):
    """Запуск секретного файла dark о философии языка."""
    if args: raise TypeError("vsp210.philosophy() не принимает аргументов")
    _run_internal_script("philosophy", dark_root_dir)

def history(args, dark_root_dir):
    """Запуск секретного файла dark об истории языка."""
    if args: raise TypeError("vsp210.history() не принимает аргументов")
    _run_internal_script("history", dark_root_dir)

def calculator(args, dark_root_dir):
    """Запуск калькулятора, написанного на Dark."""
    if args: raise TypeError("vsp210.calculator() не принимает аргументов")
    _run_internal_script("calculator", dark_root_dir)

def version(args, dark_root_dir):
    from dark_code.__version__ import __version__
    return __version__

def docs(args, dark_root_dir):
    if args: raise TypeError("docs() не принимает аргументов")
    webbrowser.open("https://vsp210.ru/dark-lang/")
    return "Докментация по языку Dark"

def telegram(args, dark_root_dir):
    if args: raise TypeError("telegram() не принимает аргументов")
    webbrowser.open("https://t.me/vsp210_official/")
    return "Телеграм канал создателя языка Dark"