import sys
import io
import os
import shutil # Добавляем для копирования файлов
import pickle
import re
import requests


try:
    import tkinter
    from tkinter import ttk
    import queue
    import threading
    import itertools
    import sqlite3
    import socket
    import ssl
    import json
    import xml.etree.ElementTree
    import multiprocessing
except ImportError:
    pass

from dark_code.dark_lang import Parser, lex, run, DarkRuntimeError, StaticAnalyzer

FROZEN_SCRIPT_CONTENT = None

def _translate_syntax_error_message(message: str) -> str:
    """
    Преобразует техническое сообщение об ошибке синтаксиса в более понятное для пользователя.
    Например, "Expected RPAR, got SEMI" -> "ожидалось ')'"
    """
    TOKEN_TRANSLATIONS = {
        'RPAR': "')'",
        'LPAR': "'('",
        'RBRACKET': "']'",
        'LBRACKET': "'['",
        'RBRACE': "'}'",
        'LBRACE': "'{'",
        'SEMI': "';' или новая строка",
        'COMMA': "','",
        'ASSIGN': "'='",
        'ID': 'идентификатор (имя переменной)',
        'NUMBER': 'число',
        'STRING': 'строка',
        'EOF': 'конец файла',
        'COLON': "':'",
        'DOT': "'.'",
        'THEN': "ключевое слово 'then'",
        'DO': "ключевое слово 'do'",
        'END': "ключевое слово 'end'",
        'IN': "ключевое слово 'in'",
        'RELOP': 'оператор сравнения (==, !=, <, > и т.д.)',
        'OP': 'арифметический оператор (+, -, *, /)',
    }

    MESSAGE_TEMPLATES = {
        "Invalid target for assignment": "недопустимая цель для присваивания. Присваивать значения можно только переменным, элементам списка или словаря.",
        "Unexpected token in factor": "неожиданный синтаксис. Возможно, вы пропустили оператор или использовали неверный символ.",
    }

    if message in MESSAGE_TEMPLATES:
        return MESSAGE_TEMPLATES[message]

    match = re.match(r"^Expected (\w+), got (\w+)$", message)
    if match:
        expected, got = match.groups()
        expected_str = TOKEN_TRANSLATIONS.get(expected, expected)
        got_str = TOKEN_TRANSLATIONS.get(got, f"'{got}'")
        return f"ожидалось {expected_str}, но было получено {got_str}"

    return message

def check_script(file_name):
    """
    Запускает скрипт в режиме проверки синтаксиса (линтера).
    Не исполняет код, а только ищет синтаксические ошибки.
    Выводит ошибки в stderr в формате, понятном для VS Code.
    """
    try:
        if not os.path.exists(file_name):
            print(f"Ошибка: Файл не найден: {os.path.abspath(file_name)}", file=sys.stderr)
            sys.exit(1)

        with open(file_name, 'r', encoding='utf-8') as f:
            src = f.read()
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

        use_with_python = False
        if src.lstrip().startswith('#!USE_WITH_PYTHON'):
            use_with_python = True

        tokens = lex(src)
        lex_errors_found = False
        for token in tokens:
            if token.type == 'ERROR':
                print(f"Лексическая ошибка в файле {os.path.abspath(file_name)}:{token.line}:{token.col}: {token.value}", file=sys.stderr)
                lex_errors_found = True

        if lex_errors_found:
            sys.exit(1)

        parser = Parser(tokens)
        ast = parser.parse()

        if parser.errors:
            for e in parser.errors:
                translated_message = _translate_syntax_error_message(e.message)
                print(f"Синтаксическая ошибка в файле {os.path.abspath(file_name)}:{e.line}:{e.column}: {translated_message}", file=sys.stderr)
            sys.exit(1)

        analyzer = StaticAnalyzer()
        semantic_errors = analyzer.analyze(ast, os.path.abspath(file_name), use_with_python=use_with_python)
        if semantic_errors:
            for e in semantic_errors:
                print(f"Семантическая ошибка в файле {os.path.abspath(e['file'])}:{e['line']}:1: {e['message']}", file=sys.stderr)
            sys.exit(1)

        sys.exit(0)
    except Exception as e:
        print(f"Неожиданная ошибка анализа в файле {os.path.abspath(file_name)}:1:1: {e}", file=sys.stderr)
        sys.exit(1)


# --- Начало изменений для изоляции интерпретатора ---

# Определяем, запущен ли скрипт как замороженный .exe (PyInstaller)
IS_FROZEN = getattr(sys, 'frozen', False)

# Определяем корневую директорию Dark, где лежит папка dark_code
if IS_FROZEN:
    # Если это .exe, PyInstaller кладет все в sys._MEIPASS
    # или основной исполняемый файл находится в sys.executable
    DARK_ROOT_DIR = os.path.dirname(sys.executable)
else:
    # Если это .py, то dark_code должен быть рядом с dark_start.py
    # или в sys.path. Мы предполагаем, что он в родительской директории.
    DARK_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Конец изменений для изоляции интерпретатора ---

def create_denv(env_name):
    """
    Создает виртуальное окружение 'denv' для Dark.
    """
    if os.path.exists(env_name):
        print(f"Ошибка: Директория '{env_name}' уже существует.", file=sys.stderr)
        sys.exit(1)

    print(f"Создание виртуального окружения в '{os.path.abspath(env_name)}'...")

    try:
        bin_dir = os.path.join(env_name, 'bin')
        extensions_dir = os.path.join(env_name, 'dark_extensions')

        os.makedirs(bin_dir)
        os.makedirs(extensions_dir)

        if IS_FROZEN:
            # --- Логика для .exe ---
            source_executable = sys.executable
            # Назовем исполняемый файл в окружении просто 'dark' или 'dark.exe'
            target_executable_name = 'dark.exe' if sys.platform == 'win32' else 'dark'
            target_executable = os.path.join(bin_dir, target_executable_name)
            print(f"Копирование {source_executable} в {target_executable}...")
            shutil.copy(source_executable, target_executable)
        else:
            # --- Логика для .py ---
            source_script = os.path.abspath(__file__)
            target_script = os.path.join(bin_dir, 'dark_start.py')
            print(f"Копирование {source_script} в {target_script}...")
            shutil.copy(source_script, target_script)

            # Создаем исполняемый файл 'dark' для Linux/macOS
            dark_executable_content = f"""
#!/bin/sh
exec python "{os.path.join('$DARK_ENV', 'bin', 'dark_start.py')}" "$@"
"""
            with open(os.path.join(bin_dir, 'dark'), 'w', encoding='utf-8') as f:
                f.write(dark_executable_content.strip())
            os.chmod(os.path.join(bin_dir, 'dark'), 0o755)

            # Создаем исполняемый файл 'dark.bat' для Windows
            dark_bat_content = f"""
@echo off
python "%DARK_ENV%\\bin\\dark_start.py" %*
"""
            with open(os.path.join(bin_dir, 'dark.bat'), 'w', encoding='utf-8') as f:
                f.write(dark_bat_content.strip())

        # Создаем пустой файл denv.cfg для совместимости и будущих нужд
        with open(os.path.join(env_name, 'denv.cfg'), 'w') as f:
            pass

        # Создаем скрипт активации для bash/zsh
        activate_script_content = f"""
#!/bin/sh
export DARK_ENV="{os.path.abspath(env_name)}"

_OLD_PS1="$PS1"
export PS1="({os.path.basename(env_name)}) $PS1"

_OLD_PATH="$PATH"
export PATH="{os.path.abspath(bin_dir)}:$PATH"

deactivate() {{
    export PS1="$_OLD_PS1"
    unset _OLD_PS1
    export PATH="$_OLD_PATH"
    unset _OLD_PATH
    unset DARK_ENV
    unset -f deactivate
}}
"""
        with open(os.path.join(bin_dir, 'activate'), 'w', encoding='utf-8') as f:
            f.write(activate_script_content.strip())

        # Создаем скрипт активации для PowerShell
        activate_ps1_content = f"""
function global:deactivate {{
    $env:PS1 = $env:_OLD_PS1
    Remove-Item Env:_OLD_PS1
    $env:PATH = $env:_OLD_PATH
    Remove-Item Env:_OLD_PATH
    Remove-Item Env:DARK_ENV
    Remove-Item function:deactivate
}}

$env:_OLD_PS1 = $env:PS1
$env:DARK_ENV = "{os.path.abspath(env_name)}"
$env:PS1 = "({os.path.basename(env_name)}) " + $env:PS1
$env:_OLD_PATH = $env:PATH
$env:PATH = "{os.path.abspath(bin_dir)};" + $env:PATH
"""
        with open(os.path.join(bin_dir, 'activate.ps1'), 'w', encoding='utf-8') as f:
            f.write(activate_ps1_content.strip())

        print(f"Виртуальное окружение '{env_name}' успешно создано.")
        print("\nЧтобы активировать его, используйте:")
        if sys.platform == 'win32':
            print(f"  .\\{os.path.join(env_name, 'bin', 'activate.ps1')}")
        else:
            print(f"  source ./{os.path.join(env_name, 'bin', 'activate')}")

    except Exception as e:
        print(f"Произошла ошибка при создании окружения: {e}", file=sys.stderr)
        sys.exit(1)

def execute_dark_code(code, source_name, use_cache=True):
    """
    Выполняет код Dark из строки, управляя кэшированием и ошибками.
    """
    ast = None
    cache_dir = "__darkcache__"
    nocache = not use_cache
    
    USE_WITH_PYTHON = False
    USE_TKINTER = True
    NOT_OUTPUT_DEVN = False

    first_line = code.split('\n', 1)[0]
    if first_line.startswith('#!'):
        if first_line.startswith('#!nocache'):
            nocache = True
        elif first_line.startswith('#!cachedir "'):
            cache_dir = first_line.split('"')[1]
        elif first_line.startswith('#!USE_WITH_PYTHON'):
            USE_WITH_PYTHON = True
        elif first_line.startswith('#!notkinter'):
            USE_TKINTER = False
        elif first_line.startswith('#!NOT_OUTPUT_DEVN'):
            NOT_OUTPUT_DEVN = True
            

    is_real_file = os.path.exists(source_name)
    if not nocache and is_real_file:
        base_name = os.path.basename(source_name)
        cache_file_path = os.path.join(os.path.dirname(source_name), cache_dir, base_name + 'c')
        if os.path.exists(cache_file_path) and os.path.getmtime(source_name) < os.path.getmtime(cache_file_path):
            try:
                with open(cache_file_path, 'rb') as f:
                    ast = pickle.load(f)
            except Exception:
                ast = None

    if ast is None:
        tokens = lex(code)
        parser = Parser(tokens)
        ast = parser.parse()
        if parser.errors:
            first_error = parser.errors[0]
            first_error.filename = os.path.abspath(source_name)
            first_error.message = _translate_syntax_error_message(first_error.message)
            print(first_error)
            sys.exit(1)

        if not nocache and is_real_file:
            full_cache_dir = os.path.join(os.path.dirname(source_name), cache_dir)
            os.makedirs(full_cache_dir, exist_ok=True)
            cache_file_path = os.path.join(full_cache_dir, os.path.basename(source_name) + 'c')
            with open(cache_file_path, 'wb') as f:
                pickle.dump(ast, f)

    script_dir = os.path.dirname(os.path.abspath(source_name)) if is_real_file else '.'
    
    # Проверяем, активно ли виртуальное окружение denv
    denv_path = os.environ.get('DARK_ENV')
    if denv_path:
        if not NOT_OUTPUT_DEVN:
            print(f"--- Запуск в окружении denv: {denv_path} ---")

    run(ast, source_name=source_name, script_dir=script_dir, use_with_python=USE_WITH_PYTHON, use_tkinter=USE_TKINTER, denv_path=denv_path)

def run_script(file_name):
    """
    Читает файл и запускает его выполнение.
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            code = f.read()
        execute_dark_code(code, file_name, use_cache=True)
    except FileNotFoundError as e:
        print(f"Ошибка выполнения: Файл '{file_name}' не найден.")
    except KeyboardInterrupt:
        print("Исполнение прервано пользователем.")
    except PermissionError as e:
        print(f"Ошибка выполнения: Недостаточно прав для доступа к файлу '{e.filename}'.")
    except DarkRuntimeError as e:
        e.filename = os.path.abspath(file_name)
        print(e)


def main():
    """
    Главная функция. Разбирает аргументы и вызывает нужный режим.
    """
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    base_dir = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) < 2:
        default_script = os.path.join(base_dir, "script.dark")
        if os.path.exists(default_script):
            run_script(default_script)
            sys.exit(0)
        else:
            print(f"Ошибка: Не указан файл для запуска или проверки.", file=sys.stderr)
            sys.exit(1)

    mode = 'run'
    file_arg_index = 1

    if sys.argv[1].startswith('--'):
        if sys.argv[1] == '--check':
            mode = 'check'
            file_arg_index = 2
        elif sys.argv[1] == '--parser':
            mode = 'parser'
            file_arg_index = 2
        elif sys.argv[1] == '--denv':
            mode = 'denv'
            file_arg_index = 2
        elif sys.argv[1] == '--version':
            from dark_code import __version__
            print(__version__.__version__)
            sys.exit(0)
        elif sys.argv[1] == '--dpm':
            from dark_code.dark_dpm import DarkPackageManager
            dpm = DarkPackageManager(sys.argv[2:])
            dpm.run()
            sys.exit(0)
        elif sys.argv[1] == '--help':
            print("Использование: dark [опции] [файл]")
            print("Опции:")
            print("  --check    Проверить синтаксис и семантику файла без выполнения.")
            print("  --denv     Создать виртуальное окружение 'denv'.")
            print("  --parser   Вывести токены и AST (для отладки парсера).")
            print("  --version  Показать версию Dark.")
            print("  --help     Показать это сообщение.")
            print("  --dpm      Запустить менеджер пакетов Dark.")
            sys.exit(0)
        else:
            print(f"Неизвестный флаг: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)

    if len(sys.argv) <= file_arg_index:
        default_script = os.path.join(base_dir, "script.dark")
        if os.path.exists(default_script):
            file_to_process = default_script
        else:
            print(f"Ошибка: Не указан файл для режима '{mode}'.", file=sys.stderr)
            sys.exit(1)
    else:
        file_to_process = sys.argv[file_arg_index]

    if not os.path.isabs(file_to_process):
        file_to_process = os.path.join(os.getcwd(), file_to_process)

    if mode == 'check':
        check_script(file_to_process)
    elif mode == 'denv':
        create_denv(file_to_process)
    elif mode == 'parser':
        with open(file_to_process, 'r', encoding='utf-8') as f:
            src = f.read()
        tokens = lex(src)

        processed_tokens = []
        KEYWORDS_AS_ID = {'TYPE'}
        for i, token in enumerate(tokens):
            if token.type in KEYWORDS_AS_ID and i > 0 and tokens[i-1].type == 'DOT':
                token.type = 'ID'
            processed_tokens.append(token)

        for token in processed_tokens:
            print(token)
    else:
        run_script(file_to_process)

if __name__ == "__main__":
    main()