import os
import sys

from dark_code.dark_lang import Parser, lex
from dark_code.dark_exceptions import translate_syntax_error_message
from dark_code.compiler.compile import translate_dark_in_python


def start_compilation(source_dark_file, working_dir, out_dir=None, nuitka=False, nuitka_args=None):
    """
    Основная функция, запускающая весь процесс компиляции.
    :param working_dir: Рабочая директория, откуда была запущена команда.
    """

    try:
        with open(source_dark_file, 'r', encoding='utf-8') as f:
            src = f.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден: {source_dark_file}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}", file=sys.stderr)
        return False

    tokens = lex(src)
    parser = Parser(tokens)
    ast = parser.parse()
    if parser.errors:
        for e in parser.errors:
            translated_message = translate_syntax_error_message(e.message)
            print(f"Синтаксическая ошибка: {os.path.abspath(source_dark_file)}:{e.line}:{e.column}: {translated_message}", file=sys.stderr)
        return False


    return translate_dark_in_python(ast, source_dark_file, working_dir, out_dir=out_dir, nuitka=nuitka, nuitka_args=nuitka_args)