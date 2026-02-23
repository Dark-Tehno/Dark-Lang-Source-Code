import os
import shutil
import subprocess
import sys
import requests
import tarfile
import zipfile
import io

from dark_code.dark_lang import Parser, lex
from dark_code.dark_exceptions import translate_syntax_error_message
from dark_code.compiler.compiler import NIMTranspiler


def _print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """
    Выводит и обновляет прогресс-бар в консоли.
    """
    percent_str = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent_str}% {suffix}')
    sys.stdout.flush()


def get_shared_dark_dir():
    """Возвращает путь к общей директории для инструментов Dark."""
    return os.path.join(os.path.expanduser('~'), '.dark')

def find_or_download_nim():
    """
    Ищет компилятор Nim. Если не находит, скачивает портативную версию.
    """
    shared_dir = get_shared_dark_dir()
    nim_dir = os.path.join(shared_dir, 'nim_compiler')
    nim_exe_path = os.path.join(nim_dir, 'bin', 'nim.exe') if sys.platform == 'win32' else os.path.join(nim_dir, 'bin', 'nim')

    if os.path.exists(nim_exe_path):
        print("Найден компилятор Nim.", flush=True)
        return nim_exe_path

    print("Компилятор Nim не найден.", flush=True)
    while True:
        choice = input("Скачать и установить его автоматически? (y/n): ").lower()
        if choice in ['y', 'n']:
            break
        print("Пожалуйста, введите 'y' или 'n'.", flush=True)

    if choice == 'n':
        return None
    
    if sys.platform == 'win32':
        nim_url = "https://nim-lang.org/download/nim-2.2.6_x64.zip"
        nim_zip_root_folder = "nim-2.2.6" 
    elif sys.platform == 'linux':
        nim_url = "https://nim-lang.org/download/nim-2.2.6-linux_x64.tar.xz"
        nim_zip_root_folder = "nim-2.2.6"
    else:
        print(f"Автоматическое скачивание Nim для вашей ОС ({sys.platform}) пока не поддерживается.", file=sys.stderr)
        return None

    try:
        response = requests.get(nim_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 8192

        os.makedirs(nim_dir, exist_ok=True)
        
        with io.BytesIO() as archive_content:
            if total_size > 0:
                print(f"Скачивание Nim ({total_size / 1024 / 1024:.2f} MB) с {nim_url}...", flush=True)
                downloaded_size = 0
                _print_progress_bar(0, total_size, prefix='Прогресс:', suffix='Завершено', length=50)
                for chunk in response.iter_content(chunk_size=chunk_size):
                    archive_content.write(chunk)
                    downloaded_size += len(chunk)
                    _print_progress_bar(downloaded_size, total_size, prefix='Прогресс:', suffix='Завершено', length=50)
                print()
            else:
                print(f"Скачивание Nim с {nim_url} (размер неизвестен)...", flush=True)
                archive_content.write(response.content)
            
            archive_content.seek(0)

            if nim_url.endswith('.zip'):
                with zipfile.ZipFile(archive_content) as z:
                    print("Распаковка архива...", flush=True)
                    for member in z.infolist():
                        parts = member.filename.replace('\\', '/').split('/', 1)
                        if len(parts) > 1 and parts[0] == nim_zip_root_folder:
                            target_path = os.path.join(nim_dir, parts[1])
                            if not target_path: continue
                            if member.is_dir():
                                os.makedirs(target_path, exist_ok=True)
                            else:
                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                with z.open(member) as source, open(target_path, "wb") as target:
                                    shutil.copyfileobj(source, target)
            elif nim_url.endswith('.tar.xz'):
                with tarfile.open(fileobj=archive_content, mode='r:xz') as t:
                    print("Распаковка архива...", flush=True)
                    for member in t.getmembers():
                        parts = member.name.replace('\\', '/').split('/', 1)
                        if len(parts) > 1 and parts[0] == nim_zip_root_folder:
                            target_path = os.path.join(nim_dir, parts[1])
                            if not target_path: continue
                            if member.isdir():
                                os.makedirs(target_path, exist_ok=True)
                            else:
                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                source = t.extractfile(member)
                                if source:
                                    with open(target_path, "wb") as target:
                                        shutil.copyfileobj(source, target)
        
        if sys.platform != 'win32' and os.path.exists(nim_exe_path):
            os.chmod(nim_exe_path, 0o755)

        print("Компилятор Nim успешно скачан и распакован.", flush=True)
        return nim_exe_path

    except requests.RequestException as e:
        print(f"Ошибка сети при скачивании Nim: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Произошла ошибка при установке Nim: {e}", file=sys.stderr)
        return None

def _compile_nim_project(source_dark_file, nim_code, nim_compiler_path, working_dir):
    """
    Внутренняя функция для компиляции сгенерированного Nim-кода.
    """
    compile_dir = os.path.join(working_dir, "dark_build")

    print(f"Создание директории для сборки: {compile_dir}", flush=True)
    os.makedirs(compile_dir, exist_ok=True)

    # Определяем путь к библиотекам Nim. Nuitka сохранит структуру папок,
    # поэтому путь будет одинаковым и в разработке, и в скомпилированном приложении.
    nim_libs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'NIM_CODE')

    if not os.path.isdir(nim_libs_path):
        print(f"Ошибка: Директория с библиотеками Nim не найдена по пути: {nim_libs_path}", file=sys.stderr)
        return False

    nim_file_path = os.path.join(compile_dir, "output.nim")
    with open(nim_file_path, "w", encoding='utf-8') as f:
        f.write(nim_code)
    print(f"Сгенерированный Nim-код сохранен в {nim_file_path}", flush=True)
    
    output_filename = os.path.splitext(os.path.basename(source_dark_file))[0]
    if sys.platform == 'win32':
        output_filename += '.exe'
    output_path = os.path.join(working_dir, output_filename)

    if not nim_compiler_path:
        print("\nКомпилятор Nim не установлен. Сгенерирован только Nim-код.", flush=True)
        print(f"Промежуточные файлы сборки сохранены в '{compile_dir}'", flush=True)
        return True

    print("Запуск компилятора Nim...", flush=True)
    # Добавляем путь к нашим библиотекам в команду компилятора
    compile_command = [nim_compiler_path, 'c', '-d:release', '--verbosity:0', '--hints:off', f'--path:{nim_libs_path}', f'--out:{output_path}', nim_file_path]
    
    try:
        process = subprocess.Popen(compile_command, cwd=compile_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print(f"Компиляция успешно завершена. Исполняемый файл сохранен как '{output_path}'", flush=True)
            return True
        else:
            print("Ошибка компиляции Nim:", file=sys.stderr)
            if stderr:
                print(stderr, file=sys.stderr)
            if stdout:
                print(stdout, file=sys.stderr)
            return False
    except Exception as e:
        print(f"Произошла непредвиденная ошибка во время компиляции: {e}", file=sys.stderr)
        return False

def start_compilation(source_dark_file, working_dir):
    """
    Основная функция, запускающая весь процесс компиляции.
    :param working_dir: Рабочая директория, откуда была запущена команда.
    """
    nim_compiler_path = find_or_download_nim()

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

    transpiler = NIMTranspiler()
    nim_code = transpiler.transpile(ast)

    return _compile_nim_project(source_dark_file, nim_code, nim_compiler_path, working_dir)