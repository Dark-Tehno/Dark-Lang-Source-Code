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
from dark_code.dark_lang import lex, Parser
from dark_code.dark_exceptions import translate_syntax_error_message
import os
import sys
import time
from . import templates
from DarkCustom.DarkCustom import DarkProgressBar
import shutil


NATIVE_MODULES = {"os": "py_dark_code.dark_os", 
                  "math": "py_dark_code.dark_math", 
                  "stdlib": "py_dark_code.dark_stdlib", 
                  "http": "py_dark_code.dark_http", 
                  "time": "py_dark_code.dark_time", 
                  "vsp210": "py_dark_code.dark_vsp210", 
                  "file": "py_dark_code.dark_file", 
                  "color": "py_dark_code.dark_color", 
                  "weather": "py_dark_code.dark_weather",
                  }
var_types = ["var", "num", "str", "float", "func_call", "bool", "list", "dict"]
binop_templates = {
    "+": templates.code_binop_plus,
    "-": templates.code_binop_minus,
    "*": templates.code_binop_mul,
    "/": templates.code_binop_div,
    ">": templates.code_binop_more,
    "<": templates.code_binop_less,
    ">=": templates.code_binop_more_eq,
    "<=": templates.code_binop_less_eq,
    "==": templates.code_binop_eq,
    "!=": templates.code_binop_not_eq,
}

logicalop_templates = {
    "and": templates.code_logical_op_and,
    "or": templates.code_logical_op_or,
}

files = {}

def _interpolated_str_to_code(raw, imported_native_modules=None):
    """
    Транспилирует backtick-строку Dark с подстановками '{expr}' в Python-выражение
    вида ("литерал" + str(выражение) + "литерал" + ...). '{{' и '}}' — экранированные
    литеральные скобки, как и в интерпретаторе.
    """
    if imported_native_modules is None:
        imported_native_modules = {}
    parts = []
    literal = []
    i, n = 0, len(raw)

    def flush_literal():
        if literal:
            parts.append(repr(''.join(literal)))
            literal.clear()

    while i < n:
        ch = raw[i]
        if ch == '{' and i + 1 < n and raw[i + 1] == '{':
            literal.append('{'); i += 2; continue
        if ch == '}' and i + 1 < n and raw[i + 1] == '}':
            literal.append('}'); i += 2; continue
        if ch == '{':
            depth = 1
            j = i + 1
            in_quote = None
            while j < n and depth > 0:
                c = raw[j]
                if in_quote:
                    if c == '\\' and j + 1 < n:
                        j += 2
                        continue
                    if c == in_quote:
                        in_quote = None
                elif c in ('"', "'"):
                    in_quote = c
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth != 0:
                raise SyntaxError("незакрытая '{' в строке с подстановкой")
            expr_text = raw[i + 1:j]
            if not expr_text.strip():
                raise SyntaxError("пустые фигурные скобки '{}' в строке с подстановкой")
            flush_literal()
            expr_ast = Parser(lex(expr_text)).expr()
            expr_code = _expression_to_code(expr_ast, imported_native_modules)
            parts.append(f"str({expr_code})")
            i = j + 1
            continue
        if ch == '}':
            raise SyntaxError("одиночная '}' без пары в строке с подстановкой")
        literal.append(ch)
        i += 1
    flush_literal()
    if not parts:
        return '""'
    return "(" + " + ".join(parts) + ")"


def _expression_to_code(node, imported_native_modules=None):
    """
    Рекурсивно преобразует узел AST выражения в строку Python кода.
    """
    if imported_native_modules is None:
        imported_native_modules = {}

    node_type = node[0]

    if node_type in ['var', 'num', 'float']:
        if node_type == 'var' and node[1] in imported_native_modules:
            return imported_native_modules[node[1]]
        return str(node[1])
    elif node_type == 'func_call':
        callee = node[1]
        args = node[2]
        if isinstance(callee, tuple) and callee[0] == 'member_access':
            obj_node = callee[1]
            member_name = callee[2]
            if member_name == 'len' and (not args or len(args) == 0):
                obj_code = _expression_to_code(obj_node, imported_native_modules)
                return f"len({obj_code})"

            try:
                if member_name == 'exec' and isinstance(obj_node, tuple) and obj_node[0] == 'var' and obj_node[1] == 'python':
                    if args and len(args) >= 1:
                        first = args[0]
                        arg_code = _expression_to_code(first, imported_native_modules)
                    else:
                        arg_code = '""'
                    return f"exec({arg_code}, globals())"
            except Exception:
                pass

        callee_code = _expression_to_code(callee, imported_native_modules)
        args_code = _params_to_var(args, imported_native_modules)
        return f"{callee_code}({args_code})"
    elif node_type == "str":
        raw_val = node[1]
        quote = node[2] if len(node) > 2 else '"'
        if quote == '`' and '{' in raw_val:
            return _interpolated_str_to_code(raw_val, imported_native_modules)
        processed_string = raw_val.replace("\n", "\\n")
        return f'"{processed_string}"'
    elif node_type == "bool":
        return str(node[1])
    elif node_type == "list":
        list_items = node[1]
        return f'[{_params_to_var(list_items, imported_native_modules)}]'
    elif node_type == "dict":
        dict_items = node[1]
        items_code = []
        for key_val_pair in dict_items:
            key_node, value_node = key_val_pair
            key_code = _expression_to_code(key_node, imported_native_modules)
            value_code = _expression_to_code(value_node, imported_native_modules)
            items_code.append(f"{key_code}: {value_code}")
        return f'{{{", ".join(items_code)}}}'
    elif node_type == "binop":
        op, left_node, right_node = node[1], node[2], node[3]
        left_code = _expression_to_code(left_node, imported_native_modules)
        right_code = _expression_to_code(right_node, imported_native_modules)
        if op in binop_templates:
            return f"({binop_templates[op].format(left=left_code, right=right_code)})"
    elif node_type == "logical_op":
        op, left_node, right_node = node[1], node[2], node[3]
        left_code = _expression_to_code(left_node, imported_native_modules)
        right_code = _expression_to_code(right_node, imported_native_modules)
        if op in logicalop_templates:
            return f"({logicalop_templates[op].format(left=left_code, right=right_code)})"
    elif node_type == "unary":
        op, operand_node = node[1], node[2]
        operand_code = _expression_to_code(operand_node, imported_native_modules)
        if op == "not":
            return f"({templates.code_unary_not.format(var=operand_code)})"
        if op in ('+', '-'):
            return f"({op}{operand_code})"
    elif node_type == "input":
        return templates.code_input
    elif node_type == "to_str":
        return templates.code_to_str.format(var=_expression_to_code(node[1], imported_native_modules))
    elif node_type == "to_int":
        return templates.code_to_int.format(var=_expression_to_code(node[1], imported_native_modules))
    elif node_type == "to_float":
        return templates.code_to_float.format(var=_expression_to_code(node[1], imported_native_modules))
    elif node_type == "type":
        return templates.code_type.format(var=_expression_to_code(node[1], imported_native_modules))
    elif node_type == "member_access":
        obj_code = _expression_to_code(node[1], imported_native_modules)
        member_name = node[2]
        return f"{obj_code}.{member_name}"
    elif node_type == 'index_access':
        obj_code = _expression_to_code(node[1], imported_native_modules)
        index_code = _expression_to_code(node[2], imported_native_modules)
        return f"{obj_code}[{index_code}]"
    elif node_type == 'enumerate':
        return f"enumerate({_expression_to_code(node[1], imported_native_modules)})"

    print(f"Предупреждение: Неизвестный тип узла выражения '{node_type}'", file=sys.stderr)
    return str(node)



def _params_to_var(params, imported_native_modules=None):
    params_code = ""
    for param in params:
        if isinstance(param, tuple) and len(param) > 0 and isinstance(param[0], str):
             params_code += f"{_expression_to_code(param, imported_native_modules)}, "
        
    return params_code.rstrip(', ')


def _translate_statement_block(block, indent_level, imported_native_modules):
    """
    Рекурсивно преобразует блок инструкций AST в строку Python кода с правильными отступами.
    """
    code = ""
    indent = "    " * indent_level

    for statement in block:
        stmt_token = statement[0]
        stmt_params = statement[1:]

        if stmt_token == "assign":
            var_name = stmt_params[0]
            var_expression = stmt_params[1]
            code += f"{indent}{templates.code_var.format(var_name=var_name, var_data=_expression_to_code(var_expression, imported_native_modules))}\n"
        elif stmt_token == "expr":
            expression_code = _expression_to_code(stmt_params[0], imported_native_modules)
            if expression_code:
                code += f"{indent}{expression_code}\n"
        elif stmt_token == "print":
            code += f"{indent}{templates.code_print.format(var=_params_to_var(stmt_params[0], imported_native_modules))}\n"
        elif stmt_token == "println":
            code += f"{indent}{templates.code_println.format(var=_params_to_var(stmt_params[0], imported_native_modules))}\n"
        elif stmt_token == "if":
                branches = stmt_params[0]
                else_body = stmt_params[1] if len(stmt_params) > 1 else None

                for idx, branch in enumerate(branches):
                    cond_node = branch[0]
                    body_block = branch[1]
                    if idx == 0:
                        code += f"{indent}if {_expression_to_code(cond_node, imported_native_modules)}:\n"
                    else:
                        code += f"{indent}elif {_expression_to_code(cond_node, imported_native_modules)}:\n"
                    code += _translate_statement_block(body_block, indent_level + 1, imported_native_modules)

                if else_body:
                    code += f"{indent}else:\n"
                    code += _translate_statement_block(else_body, indent_level + 1, imported_native_modules)
        elif stmt_token == "while":
            condition = _expression_to_code(stmt_params[0], imported_native_modules)
            body = stmt_params[1]
            code += f"{indent}while {condition}:\n"
            code += _translate_statement_block(body, indent_level + 1, imported_native_modules)
        elif stmt_token == "for":
            var_name = stmt_params[0]
            iterable = _expression_to_code(stmt_params[1], imported_native_modules)
            body = stmt_params[2]
            code += f"{indent}for {var_name} in {iterable}:\n"
            code += _translate_statement_block(body, indent_level + 1, imported_native_modules)
        elif stmt_token == "try_except":
            try_body = stmt_params[0]
            exception_var = stmt_params[1]
            except_body = stmt_params[2]

            code += f"{indent}try:\n"
            code += _translate_statement_block(try_body, indent_level + 1, imported_native_modules)
            code += f"{indent}except Exception as {exception_var}:\n"
            code += _translate_statement_block(except_body, indent_level + 1, imported_native_modules)
        elif stmt_token == "func_def":
            func_name = stmt_params[0]
            args = stmt_params[1]
            body = stmt_params[2]
            code += f"{indent}def {func_name}({', '.join(args)}):\n"
            if not body:
                code += f"{indent}    pass\n"
            else:
                code += _translate_statement_block(body, indent_level + 1, imported_native_modules)
        elif stmt_token == 'multi_assign':
            targets, values, line_no = stmt_params[0], stmt_params[1], stmt_params[2]
            left = ', '.join([_expression_to_code(t, imported_native_modules) for t in targets])
            if len(values) == 1:
                right = _expression_to_code(values[0], imported_native_modules)
            else:
                right_parts = [_expression_to_code(v, imported_native_modules) for v in values]
                right = f"({', '.join(right_parts)})"
            code += f"{indent}{left} = {right}\n"
        elif stmt_token == 'index_assign':
            collection, index_node, rhs, line_no = stmt_params[0], stmt_params[1], stmt_params[2], stmt_params[3]
            coll_code = _expression_to_code(collection, imported_native_modules)
            idx_code = _expression_to_code(index_node, imported_native_modules)
            rhs_code = _expression_to_code(rhs, imported_native_modules)
            code += f"{indent}{coll_code}[{idx_code}] = {rhs_code}\n"
        elif stmt_token == 'member_assign':
            obj, member, rhs, line_no = stmt_params[0], stmt_params[1], stmt_params[2], stmt_params[3]
            obj_code = _expression_to_code(obj, imported_native_modules)
            rhs_code = _expression_to_code(rhs, imported_native_modules)
            code += f"{indent}{obj_code}.{member} = {rhs_code}\n"
        elif stmt_token == 'assert':
            condition = _expression_to_code(stmt_params[0], imported_native_modules)
            message = _expression_to_code(stmt_params[1], imported_native_modules)
            code += f"{indent}assert {condition}, {message}\n"
        elif stmt_token == 'class_def':
            class_name = stmt_params[0]
            base_class = stmt_params[1] or ''
            methods = stmt_params[2]
            base_decl = f"({base_class})" if base_class else ''
            code += f"{indent}class {class_name}{base_decl}:\n"
            if not methods:
                code += f"{indent}    pass\n"
            else:
                for m in methods:
                    if m[0] == 'func_def':
                        m_name = m[1]
                        m_args = m[2]
                        m_body = m[3]
                        args_with_self = ['self'] + m_args
                        code += f"{indent}    def {m_name}({', '.join(args_with_self)}):\n"
                        if not m_body:
                            code += f"{indent}        pass\n"
                        else:
                            code += _translate_statement_block(m_body, indent_level + 2, imported_native_modules)
        elif stmt_token == "return":
            if stmt_params and stmt_params[0] is not None:
                return_expression = _expression_to_code(stmt_params[0], imported_native_modules)
                code += f"{indent}return {return_expression}\n"
            else:
                code += f"{indent}return\n"
        else:
            if stmt_token not in ["import", "from_import"]:
                 print(f"\nПредупреждение: неизвестный токен в блоке '{stmt_token}'", file=sys.stderr)

    return code


def translate_dark_in_python(ast, source_dark_file, working_dir, is_main=True, progress_bar=False, out_dir=None, nuitka=False, nuitka_args=None):
    dark_code = ""
    imported_native_modules = {}
    ast = ast[1]
    
    total_lines = len(ast)
    if progress_bar:
        if total_lines == 0:
            DarkProgressBar(1, 1, rgb_bar=(255,255,255), rgb_empty=(255,255,255))
            return True 

    for i, line in enumerate(ast):
        if not is_main:
            time.sleep(0.001)
        sys.stdout.flush()

        token = line[0]
        params = line[1:]

        if token == "from_import" or token == "import":
            module_name = params[0][0]
            module_path = os.path.join(working_dir, f"{module_name}.dark")

            if module_name in files:
                continue

            if os.path.exists(module_path):
                try:
                    with open(module_path, 'r', encoding='utf-8') as f:
                        src = f.read()
                except Exception as e:
                    print(f"\nОшибка компиляции: не удалось прочитать модуль '{module_name}': {e}", file=sys.stderr)
                    return False

                tokens = lex(src)
                parser = Parser(tokens)
                module_ast = parser.parse()
                if parser.errors:
                    for e in parser.errors:
                        translated_message = translate_syntax_error_message(e.message)
                        print(f"Синтаксическая ошибка в модуле '{module_name}': {os.path.abspath(module_path)}:{e.line}:{e.column}: {translated_message}", file=sys.stderr)
                    return False
                
                module_code = translate_dark_in_python(module_ast, module_path, working_dir, is_main=False)
                if module_code is False:
                    return False
                files[module_name] = module_code

                if token == "from_import":
                    imports = params[1]
                    dark_code += f"from {module_name} import {', '.join(imports)}\n"
                elif token == "import":
                    dark_code += f"import {module_name}\n"
            else:
                if token == "import":
                    if module_name == 'python':
                        imported_native_modules[module_name] = module_name
                        continue
                    if module_name in NATIVE_MODULES:
                        py_module_name = NATIVE_MODULES[module_name]
                        dark_code += f"import {py_module_name}\n"
                        imported_native_modules[module_name] = py_module_name
                        continue
                print(f"\nОшибка компиляции: модуль '{module_name}' не найден по пути {module_path}", file=sys.stderr)
                return False

        if progress_bar:
            DarkProgressBar(i + 1, total_lines, rgb_bar=(255,255,255), rgb_empty=(255,255,255))

    helper = '''
def _dark_type(x):
    if isinstance(x, dict):
        return 'dict'
    if isinstance(x, list):
        return 'list'
    if isinstance(x, (int, float)):
        return 'num'
    if isinstance(x, str):
        return 'str'
    if isinstance(x, bool):
        return 'bool'
    return type(x).__name__

'''
    dark_code += helper
    dark_code += _translate_statement_block(ast, 0, imported_native_modules)

    if is_main:
        files[os.path.splitext(os.path.basename(source_dark_file))[0]] = dark_code

        try:
            # Определяем путь к стандартной библиотеке py_dark_code
            # В режиме разработки ищем относительно текущего файла
            base_path = os.path.dirname(__file__) # compiler/ — здесь реально лежит py_dark_code
            
            # Если приложение "заморожено" (скомпилировано в exe),
            # стандартная библиотека должна быть вложена Nuitka.
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS

            src_py_dir = os.path.join(base_path, 'py_dark_code')
            output_root = out_dir if out_dir else os.path.join(working_dir, 'dark_py_build')
            dest_py_dir = os.path.join(output_root, 'py_dark_code')

            if os.path.exists(output_root):
                shutil.rmtree(output_root)
            os.makedirs(output_root, exist_ok=True)

            if os.path.exists(src_py_dir):
                shutil.copytree(src_py_dir, dest_py_dir, dirs_exist_ok=True)
            else:
                os.makedirs(dest_py_dir, exist_ok=True)

            total = len(files)
            cur = 0
            for filename, code in files.items():
                out_path = os.path.join(output_root, f"{filename}.py")
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                cur += 1
                DarkProgressBar(cur, total, rgb_bar=(0,200,120), rgb_empty=(255,255,255))

            print("\n--- Результаты компиляции ---", flush=True)
            print(f"Сборка создана: {os.path.abspath(output_root)}", flush=True)

            if nuitka:
                # Импортируем Nuitka напрямую. Убедитесь, что Nuitka включена
                # в зависимости при сборке вашего dark_start.exe.                
                nuitka_out = os.path.join(output_root, 'nuitka_build')
                abs_nuitka_out = os.path.abspath(nuitka_out)
                if os.path.exists(abs_nuitka_out):
                    shutil.rmtree(abs_nuitka_out)
                os.makedirs(abs_nuitka_out, exist_ok=True)

                entry_name = os.path.splitext(os.path.basename(source_dark_file))[0] + '.py'
                entry_path = os.path.join(output_root, entry_name)
                if not os.path.exists(entry_path):
                    print(f"Ошибка: точка входа для Nuitka не найдена: {entry_path}", file=sys.stderr)
                    return False
                abs_entry = os.path.abspath(entry_path)
                abs_output_root = os.path.abspath(output_root)
                # Формируем список опций для Nuitka
                if sys.platform == 'win32':
                    nuitka_options = [
                        '--standalone',
                        f'--include-plugin-directory={abs_output_root}',
                        f'--output-dir={abs_nuitka_out}',
                        abs_entry
                    ]
                else:
                    nuitka_options = [
                        '--standalone',
                        f'--include-plugin-directory={abs_output_root}',
                        f'--output-dir={abs_nuitka_out}',
                        f'--output-filename={os.path.splitext(os.path.basename(source_dark_file))[0]}',
                        abs_entry
                    ]

                print(f"Запуск Nuitka: nuitka {' '.join(nuitka_options)}", flush=True)

                def find_true_python_executable():
                    """
                    Находит настоящий системный python.exe, избегая самого себя (frozen .exe).
                    Это необходимо для запуска Nuitka в чистом, изолированном процессе,
                    независимо от того, запущен ли dark_start.exe как скрипт или как .exe.
                    """
                    current_exe_path = os.path.dirname(os.path.abspath(sys.executable))
                    python_names = ['python.exe', 'python3.exe', 'python', 'python3']

                    for path in os.environ.get('PATH', '').split(os.pathsep):
                        # Пропускаем каталог, в котором находится наш frozen .exe
                        if os.path.normcase(path) == os.path.normcase(current_exe_path):
                            continue
                        for name in python_names:
                            exe_path = os.path.join(path, name)
                            if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                                return exe_path
                    # В крайнем случае, если не нашли ничего лучше
                    return shutil.which('python') or shutil.which('python3')

                python_for_nuitka = find_true_python_executable()

                if not python_for_nuitka:
                    print("Критическая ошибка: Не удалось найти 'python' или 'python3' в системной переменной PATH.", file=sys.stderr)
                    print("Nuitka требует наличия Python для своей работы.", file=sys.stderr)
                    return False

                import subprocess
                
                # Запускаем Nuitka как полностью отдельный процесс через системный Python.
                # Это самый надежный способ, который гарантирует, что Nuitka будет работать
                # в чистом окружении.
                command = [python_for_nuitka, '-m', 'nuitka'] + nuitka_options

                # Первая попытка запуска Nuitka
                try:
                    # Используем capture_output, чтобы проверить stderr в случае ошибки
                    subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                except subprocess.CalledProcessError as e:
                    # Проверяем, вызвана ли ошибка отсутствием Nuitka
                    if "No module named nuitka" in e.stderr:
                        print("\nМодуль Nuitka не найден. Попытка автоматической установки...", flush=True)
                        install_command = [python_for_nuitka, '-m', 'pip', 'install', 'nuitka']
                        try:
                            subprocess.run(install_command, check=True, capture_output=True, text=True, encoding='utf-8')
                            print("Nuitka успешно установлена.", flush=True)
                            
                            # Вторая попытка запуска Nuitka после установки
                            print("Повторный запуск Nuitka...", flush=True)
                            subprocess.run(command, check=True)
                        except (subprocess.CalledProcessError, FileNotFoundError) as install_error:
                            print(f"Ошибка при установке или повторном запуске Nuitka: {install_error}", file=sys.stderr)
                            if isinstance(install_error, subprocess.CalledProcessError):
                                print(f"Вывод ошибки: {install_error.stderr}", file=sys.stderr)
                            return False
                    else:
                        print(f"Ошибка при запуске Nuitka: {e.stderr}", file=sys.stderr)
                        return False

                print(f"Nuitka сборка завершена: {os.path.abspath(nuitka_out)}")

            return True
        except Exception as e:
            print(f"\nОшибка при создании сборки: {e}", file=sys.stderr)
            return False
    else:
        return dark_code