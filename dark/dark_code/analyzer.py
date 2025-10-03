import os
from dark_code.native_modules import NATIVE_MODULES
from dark_code.lexer import lex
from dark_code.parser import Parser

BUILTIN_FUNCTIONS_INFO = {
    'print': {'params': None}, 
    'println': {'params': None},
    'input': {'params': 0},
    'to_int': {'params': 1},
    'to_str': {'params': 1},
    'to_float': {'params': 1},
    'type': {'params': 1}
}

class StaticAnalyzer:
    """
    Выполняет статический анализ AST для поиска семантических ошибок,
    таких как неопределенные переменные или неверные вызовы функций.
    """
    def __init__(self):
        self.errors = []
        self.scopes = []
        self.analyzed_files = {}  
        self.current_file_path = None

    def add_error(self, message, line, file_path=None, error_type='semantic'):
        file_path = file_path or self.current_file_path
        error_tuple = (message, line, os.path.abspath(file_path))
        if not any(e['message'] == message and e['line'] == line and os.path.abspath(e['file']) == error_tuple[2] for e in self.errors):
            self.errors.append({'message': message, 'line': line, 'file': file_path, 'type': error_type})

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def define(self, name, info):
        if self.scopes:
            self.scopes[-1][name] = info

    def find(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def analyze(self, ast, file_path, use_with_python=False):
        self.errors = []
        self.analyzed_files = {}
        self.enter_scope()
        self._analyze_ast(ast, file_path, use_with_python)
        self.exit_scope()
        return self.errors

    def _analyze_module_ast(self, module_ast, module_path):
        """
        Анализирует АСД модуля в изолированном окружении.
        Возвращает словарь с экспортируемыми именами.
        """
        original_scopes = self.scopes
        original_path = self.current_file_path

        self.scopes = []

        try:
            self.enter_scope()
            self._analyze_ast(module_ast, module_path)
            exports = self.scopes[0] if self.scopes else {}
            self.exit_scope()
            return exports
        finally:
            self.scopes = original_scopes
            self.current_file_path = original_path

    def _get_or_analyze_module(self, module_name, script_dir, import_line):
        if module_name in NATIVE_MODULES:
            return {k: {'type': 'native_function'} for k in NATIVE_MODULES[module_name]}

        module_path = os.path.join(script_dir, module_name + ".dark")
        abs_path = os.path.abspath(module_path)

        if abs_path in self.analyzed_files:
            return self.analyzed_files[abs_path]

        if not os.path.exists(abs_path):
            self.add_error(f"не удалось найти модуль '{module_name}'", import_line, self.current_file_path)
            return None

        self.analyzed_files[abs_path] = {} 

        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                src = f.read()
            tokens = lex(src)
            parser = Parser(tokens)
            module_ast = parser.parse()
            if parser.errors:
                for e in parser.errors:
                    self.add_error(e.message, e.line, abs_path, error_type='syntax')
                return {}

            module_exports = self._analyze_module_ast(module_ast, abs_path)
            self.analyzed_files[abs_path] = module_exports
            return module_exports
        except Exception as e:
            self.add_error(f"не удалось проанализировать модуль '{module_name}': {e}", import_line, self.current_file_path)
            return None

    def _analyze_ast(self, ast, file_path, use_with_python=False):
        self.current_file_path = file_path
        
        for name, info in BUILTIN_FUNCTIONS_INFO.items():
            self.define(name, {'type': 'builtin_function', **info})

        if use_with_python:
            self.define('python', {'type': 'module', 'exports': {'exec': {'type': 'native_function'}}})
        
        for stmt in ast[1]:
            if stmt[0] == 'func_def':
                name = stmt[1]
                params = stmt[2]
                line = stmt[4]
                if self.find(name):
                    self.add_error(f"Переопределение существующей функции или переменной '{name}'", line)
                self.define(name, {'type': 'function', 'params': len(params)})
            elif stmt[0] == 'class_def':
                name, parent_name, method_nodes, line = stmt[1], stmt[2], stmt[3], stmt[4]
                if self.find(name):
                    self.add_error(f"Переопределение существующего класса или переменной '{name}'", line)
                
                methods = {}
                for method_node in method_nodes:
                    if method_node[0] == 'func_def':
                        method_name, method_params = method_node[1], method_node[2]
                        methods[method_name] = {'type': 'function', 'params': len(method_params)}

                self.define(name, {'type': 'class', 'methods': methods, 'parent': parent_name})
            elif stmt[0] == 'assign':
                var_name = stmt[1]
                line = stmt[3]
                if not self.find(var_name):
                    self.define(var_name, {'type': 'variable'})
            elif stmt[0] == 'import':
                module_name, line = stmt[1], stmt[2]
                script_dir = os.path.dirname(file_path)
                module_exports = self._get_or_analyze_module(module_name, script_dir, line)
                if module_exports is not None:
                    self.define(module_name, {'type': 'module', 'exports': module_exports})

        for stmt in ast[1]:
            self.visit_stmt(stmt)

    def visit_stmt(self, node):
        if not isinstance(node, tuple): return
        
        method_name = f'visit_stmt_{node[0]}'
        visitor = getattr(self, method_name, lambda n: None)
        visitor(node)

    def visit_expr(self, node, line):
        if not isinstance(node, tuple): return

        node_type = node[0]
        if node_type == 'var':
            name = node[1]
            if not self.find(name):
                self.add_error(f"Использование неопределенной переменной или функции '{name}'", line)
        
        elif node_type == 'func_call':
            callable_node, args, call_line = node[1], node[2], node[3]
            self.visit_expr(callable_node, call_line)
            for arg in args:
                self.visit_expr(arg, call_line)
            
            if callable_node[0] == 'var':
                func_name = callable_node[1]
                func_info = self.find(func_name)
                if func_info:
                    if func_info['type'] not in ('function', 'builtin_function', 'class'):
                        self.add_error(f"Попытка вызова не-функции и не-класса '{func_name}'", call_line)
                    elif func_info['type'] in ('function', 'builtin_function'):
                        expected_args = func_info.get('params')
                        if expected_args is not None and len(args) != expected_args:
                            self.add_error(f"Функция '{func_name}' ожидает {expected_args} аргументов, но было передано {len(args)}", call_line)
                    elif func_info['type'] == 'class':
                        constructor_info = func_info.get('methods', {}).get('__main__')
                        if constructor_info:
                            expected_args = constructor_info.get('params', 1) - 1
                            if len(args) != expected_args:
                                self.add_error(f"Конструктор для класса '{func_name}' ожидает {expected_args} аргументов, но было передано {len(args)}", call_line)
                        elif len(args) > 0:
                            self.add_error(f"Класс '{func_name}' не имеет конструктора для приёма аргументов", call_line)
            
            elif callable_node[0] == 'member_access':
                obj_node, member_name = callable_node[1], callable_node[2]
                if obj_node[0] == 'var':
                    module_name = obj_node[1]
                    module_info = self.find(module_name)
                    if module_info and module_info.get('type') == 'module':
                        if member_name not in module_info['exports']:
                            self.add_error(f"Модуль '{module_name}' не содержит члена '{member_name}'", call_line)
                        else:
                            member_info = module_info['exports'][member_name]
                            if member_info.get('type') not in ('function', 'native_function'):
                                self.add_error(f"Попытка вызова не-функции '{module_name}.{member_name}'", call_line)
                            elif member_info.get('type') == 'function':
                                expected_args = member_info.get('params')
                                if expected_args is not None and len(args) != expected_args:
                                    self.add_error(f"Функция '{module_name}.{member_name}' ожидает {expected_args} аргументов, но было передано {len(args)}", call_line)
        
        elif node_type == 'member_access':
            obj_node, member_name = node[1], node[2]
            self.visit_expr(obj_node, line)
            if obj_node[0] == 'var':
                module_name = obj_node[1]
                module_info = self.find(module_name)
                if module_info and module_info.get('type') == 'module':
                    if member_name not in module_info['exports']:
                        self.add_error(f"Модуль '{module_name}' не содержит члена '{member_name}'", line)
        
        elif node_type in ('binop', 'logical_op'):
            self.visit_expr(node[2], line); self.visit_expr(node[3], line)
        elif node_type in ('unary', 'to_int', 'to_str', 'to_float', 'type'):
            self.visit_expr(node[1], line)
        elif node_type == 'list':
            for item in node[1]: self.visit_expr(item, line)
        elif node_type == 'dict':
            for k, v in node[1]: self.visit_expr(k, line); self.visit_expr(v, line)
        elif node_type == 'index_access':
            self.visit_expr(node[1], line); self.visit_expr(node[2], line)

    
    def visit_stmt_if(self, n):
        clauses, false_body, line = n[1], n[2], n[3]
        for cond_expr, body in clauses:
            self.visit_expr(cond_expr, line)
            self.enter_scope()
            for stmt_node in body:
                self.visit_stmt(stmt_node)
            self.exit_scope()
        if false_body:
            self.enter_scope()
            for stmt_node in false_body:
                self.visit_stmt(stmt_node)
            self.exit_scope()
    def visit_stmt_while(self, n): self.visit_expr(n[1], n[3]); self.enter_scope(); [self.visit_stmt(s) for s in n[2]]; self.exit_scope()
    def visit_stmt_for(self, n): self.visit_expr(n[2], n[4]); self.enter_scope(); self.define(n[1], {'type': 'variable'}); [self.visit_stmt(s) for s in n[3]]; self.exit_scope()
    def visit_stmt_func_def(self, n): self.enter_scope(); [self.define(p, {'type': 'parameter'}) for p in n[2]]; [self.visit_stmt(s) for s in n[3]]; self.exit_scope()
    def visit_stmt_class_def(self, node):
        _, name, parent_name, method_nodes, line = node

        if parent_name:
            parent_info = self.find(parent_name)
            if not parent_info or parent_info.get('type') != 'class':
                self.add_error(f"Базовый класс '{parent_name}' не найден или не является классом", line)
        
        for method_node in method_nodes:
            self.visit_stmt(method_node)
    def visit_stmt_try_except(self, n): self.enter_scope(); [self.visit_stmt(s) for s in n[1]]; self.exit_scope(); self.enter_scope(); self.define(n[2], {'type': 'variable'}) if n[2] else None; [self.visit_stmt(s) for s in n[3]]; self.exit_scope()
    def visit_stmt_assign(self, n): self.visit_expr(n[2], n[3]); self.define(n[1], {'type': 'variable'})
    def visit_stmt_index_assign(self, n): self.visit_expr(n[1], n[4]); self.visit_expr(n[2], n[4]); self.visit_expr(n[3], n[4])
    def visit_stmt_return(self, n): self.visit_expr(n[1], n[2]) if n[1] else None
    def visit_stmt_expr(self, n): self.visit_expr(n[1], n[2])
    def visit_stmt_print(self, n): [self.visit_expr(arg, n[2]) for arg in n[1]]
    def visit_stmt_println(self, n): [self.visit_expr(arg, n[2]) for arg in n[1]]
    def visit_stmt_import(self, n): pass