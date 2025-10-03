import os
import sys
from dark_code.native_modules import NATIVE_MODULES
from dark_code.dark_exceptions import DarkRuntimeError, DarkError
from dark_code.lexer import lex
from dark_code.parser import Parser

class DarkClass:
    def __init__(self, name, base_class, methods):
        self.name = name
        self.base_class = base_class
        self.methods = methods

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.base_class:
            return self.base_class.find_method(name)
        return None

class DarkInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    
    def __str__(self):
        return f"<instance of {self.klass.name} object at {hex(id(self))}>"

class BoundMethod:
    def __init__(self, instance, function):
        self.instance = instance
        self.function = function

class Function:
    def __init__(self, name, params, body, definition_env):
        self.name = name
        self.params = params
        self.body = body
        self.definition_env = definition_env

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


def run(ast, env=None, source_name='<string>', script_dir=None, imported_files=None, modules=None, use_with_python=False, use_tkinter=True):
    if env is None: env = {}
    if script_dir is None: script_dir = '.'
    if imported_files is None: imported_files = set()
    if modules is None: modules = {}

    BUILTIN_METHODS = {
        str: {
            'upper': (0, lambda o, a: o.upper()),
            'lower': (0, lambda o, a: o.lower()),
            'strip': (0, lambda o, a: o.strip()),
            'len':   (0, lambda o, a: len(o)),
            'startswith': (1, lambda o, a: o.startswith(a[0])),
            'endswith': (1, lambda o, a: o.endswith(a[0])),
            'find':  (1, lambda o, a: o.find(a[0])),
        },
        list: {
            'len':    (0, lambda o, a: len(o)),
            'append': (1, lambda o, a: o.append(a[0]) or 0),
            'pop':    (0, lambda o, a: o.pop()),
        },
        dict: {
            'len':  (0, lambda o, a: len(o)),
            'keys': (0, lambda o, a: list(o.keys())),
        }
    }
    
    if use_with_python:
        from dark_code.native_modules import native_python_exec
        modules['python'] = {'exec': lambda args: native_python_exec(args, env)}

    def _dark_obj_to_str(val, current_env):
        """Преобразует объект Dark в строку, вызывая __str__ если он есть."""
        if isinstance(val, DarkInstance):
            str_method = val.klass.find_method('__str__')
            if str_method:
                try:
                    bound_str_method = BoundMethod(val, str_method)
                    result = call_dark_function(bound_str_method.function, [bound_str_method.instance], self_instance=bound_str_method.instance)
                    if not isinstance(result, str):
                        raise DarkRuntimeError(f"Метод __str__ должен возвращать строку, а не {type(result).__name__}")
                    return result
                except DarkRuntimeError as e:
                    raise e
            return str(val) 
        return str(val)

    def is_truthy(val):
        return not (val is False or val == 0 or val == "" or (isinstance(val, (list, dict)) and not val)) 

    def call_dark_function(func, args, call_site_line=None, self_instance=None):
        if len(args) != len(func.params):
            raise DarkRuntimeError(f"Function '{func.name}' expects {len(func.params)} arguments, got {len(args)}", line=call_site_line)

        call_env = dict(func.definition_env)
        
        if '__current_self__' in env:
            call_env['__current_self__'] = env['__current_self__']
        if self_instance:
            call_env['__current_self__'] = self_instance
        for param_name, arg_val in zip(func.params, args):
            call_env[param_name] = arg_val
        try:
            for stmt_node in func.body:
                run_stmt(stmt_node, call_env)
        except ReturnSignal as ret:
            return ret.value
        except DarkRuntimeError as e:
            context_name = f"функция '{func.name}'"
            if self_instance:
                context_name = f"метод '{func.name}' класса '{self_instance.klass.name}'"
            
            e.add_trace(func.definition_env.get('__file__', '<unknown>'), call_site_line, context_name)
            raise e
        return 0 

    def eval_expr(node, current_env):
        t = node[0]
        line = node[-1] if isinstance(node[-1], int) else None

        if t == 'unary':
            op, expr_node, line = node[1], node[2], node[3]
            val = eval_expr(expr_node, current_env)
            
            if op == 'not':
                return not is_truthy(val)

            if not isinstance(val, (int, float)):
                raise DarkRuntimeError(f"Unary operator '{op}' not supported for type '{type(val).__name__}'", line=line)
            if op == '-':
                return -val
            return val 
        if t == 'input':
            try:
                return input()
            except (ValueError, EOFError):
                return ""
        if t == 'to_int':
            val = eval_expr(node[1], current_env)
            try: return int(val)
            except (ValueError, TypeError): raise DarkRuntimeError(f"Cannot convert value to int")
        if t == 'to_float':
            val = eval_expr(node[1], current_env)
            try: return float(val)
            except (ValueError, TypeError): raise DarkRuntimeError(f"Cannot convert value to float")
        if t == 'to_str':
            val = eval_expr(node[1], current_env)
            return _dark_obj_to_str(val, current_env)
        if t == 'type':
            val = eval_expr(node[1], current_env)
            if isinstance(val, int): return "int"
            if isinstance(val, float): return "float"
            if isinstance(val, str): return "str"
            if isinstance(val, bool): return "bool"
            if isinstance(val, list): return "list"
            if isinstance(val, dict): return "dict"
            if isinstance(val, Function): return "function"
            return "unknown"
        if t == 'bool':
            return node[1]
        if t == 'num':
            return node[1]
        if t == 'str':
            return node[1]
        if t == 'list':
            return [eval_expr(elem, current_env) for elem in node[1]]
        if t == 'dict':
            d = {}
            for k_node, v_node in node[1]:
                key = eval_expr(k_node, current_env)
                if not isinstance(key, (str, int, bool)):
                    raise DarkRuntimeError(f"Unhashable type for dict key: {type(key).__name__}")
                value = eval_expr(v_node, current_env)
                d[key] = value
            return d
        if t == 'var':
            name = node[1]
            if name in current_env:
                return current_env[name]
            if name in modules:
                return modules[name]
            raise DarkRuntimeError(f"имя '{name}' не определено")
        if t == 'logical_op':
            op, left_node, right_node, line = node[1], node[2], node[3], node[4]
            left_val = eval_expr(left_node, current_env)
            if op == 'and':
                if not is_truthy(left_val):
                    return left_val
                return eval_expr(right_node, current_env)
            if op == 'or':
                if is_truthy(left_val):
                    return left_val
                return eval_expr(right_node, current_env)
        if t == 'member_access':
            obj_node, member_name, line = node[1], node[2], node[3]
            obj = eval_expr(obj_node, current_env)

            if isinstance(obj, DarkInstance):
                if member_name.startswith('__'):
                    current_self = current_env.get('__current_self__')
                    if current_self is not obj:
                        raise DarkRuntimeError(f"не удается получить доступ к приватному атрибуту или методу '{member_name}' объекта '{obj.klass.name}'", line=line)

                if member_name in obj.fields:
                    return obj.fields[member_name]
                
                method = obj.klass.find_method(member_name)
                if method:
                    return BoundMethod(obj, method)

                raise DarkRuntimeError(f"объект '{obj.klass.name}' не имеет атрибута '{member_name}'", line=line)

            if isinstance(obj, dict):
                if member_name in obj:
                    return obj[member_name]
                else:
                    if obj_node[0] == 'var' and len(obj_node) > 1 and obj_node[1] in modules: 
                         raise DarkRuntimeError(f"в модуле '{obj_node[1]}' не найден член '{member_name}'", line=line)
                    raise DarkRuntimeError(f"в словаре не найден ключ '{member_name}'", line=line)
            
            
            if type(obj) in BUILTIN_METHODS and member_name in BUILTIN_METHODS[type(obj)]:
                return "builtin_method" 
            raise DarkRuntimeError(f"объект типа '{type(obj).__name__}' не поддерживает доступ к членам через точку", line=line)
        if t == 'binop':
            op, a_node, b_node, line = node[1], node[2], node[3], node[4]
            a = eval_expr(a_node, current_env)
            b = eval_expr(b_node, current_env)

            op_to_rmethod = {
                '+': '__radd__',
                '-': '__rsub__',
                '*': '__rmul__',
                '/': '__rdiv__',
            }

            if isinstance(a, DarkInstance):
                op_to_method = {
                    '+': '__add__',
                    '-': '__sub__',
                    '*': '__mul__',
                    '/': '__div__',
                    '<': '__lt__',
                    '>': '__gt__',
                    '<=': '__le__',
                    '>=': '__ge__',
                    '==': '__eq__',
                    '!=': '__ne__',
                }
                if op in op_to_method:
                    method_name = op_to_method[op]
                    method = a.klass.find_method(method_name)
                    if method:
                        result = call_dark_function(method, [a, b], call_site_line=line, self_instance=a)
                        return result

            if isinstance(b, DarkInstance) and op in op_to_rmethod:
                rmethod_name = op_to_rmethod[op]
                rmethod = b.klass.find_method(rmethod_name)
                if rmethod:
                    return call_dark_function(rmethod, [b, a], call_site_line=line, self_instance=b)

            
            if op == '==':
                return a == b
            if op == '!=':
                return a != b

            
            if isinstance(a, str) or isinstance(b, str):
                if op == '+':
                    return str(a) + str(b)
                if op == '<':
                    return str(a) < str(b)
                if op == '>':
                    return str(a) > str(b)
                if op == '<=':
                    return str(a) <= str(b)
                if op == '>=':
                    return str(a) >= str(b)
                raise DarkRuntimeError(f"оператор '{op}' не поддерживается для строк", line=line)

            
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                if op == '+': return a + b
                if op == '-': return a - b
                if op == '*': return a * b
                if op == '/':
                    if b == 0: raise DarkRuntimeError("деление на ноль", line=line)
                    return a / b
                if op == '<': return a < b
                if op == '>': return a > b
                if op == '<=': return a <= b
                if op == '>=': return a >= b
                raise DarkRuntimeError(f"неподдерживаемый числовой оператор: {op}", line=line)

            
            raise DarkRuntimeError(f"неподдерживаемые типы операндов для '{op}': '{type(a).__name__}' и '{type(b).__name__}'", line=line)
        if t == 'index_access':
            collection_node, index_node, line = node[1], node[2], node[3]
            collection = eval_expr(collection_node, current_env)
            index = eval_expr(index_node, current_env)
            if isinstance(collection, (list, str, dict)):
                try:
                    return collection[index]
                except IndexError:
                    
                    raise DarkRuntimeError(f"индекс {index} вне допустимого диапазона для объекта размером {len(collection)}", line=line)
                except KeyError:
                    
                    raise DarkRuntimeError(f"ключ '{index}' не найден в словаре")
                except TypeError:
                    
                    raise DarkRuntimeError(f"недопустимый тип индекса '{type(index).__name__}' для объекта типа '{type(collection).__name__}'", line=line)
            raise DarkRuntimeError(f"объект типа '{type(collection).__name__}' не поддерживает индексацию", line=line)
        if t == 'func_call':
            callable_node, arg_nodes, line = node[1], node[2], node[3]
            args = [eval_expr(arg, current_env) for arg in arg_nodes]

            
            if callable_node[0] == 'member_access':
                if len(callable_node) < 4:
                    raise DarkRuntimeError(f"Внутренняя ошибка: неверно сформирован узел member_access. Возможно, стоит очистить кэш (__darkcache__).", line=line)
                obj_node, method_name, _ = callable_node[1], callable_node[2], callable_node[3]
                obj = eval_expr(obj_node, current_env)
                obj_type = type(obj)

                if obj_type in BUILTIN_METHODS and method_name in BUILTIN_METHODS[obj_type]:
                    expected_argc, func_lambda = BUILTIN_METHODS[obj_type][method_name]
                    if len(args) != expected_argc:
                        raise DarkRuntimeError(f"метод {obj_type.__name__}.{method_name}() принимает {expected_argc} аргументов, но было передано {len(args)}", line=line)
                    try:
                        return func_lambda(obj, args)
                    except IndexError:
                        raise DarkRuntimeError(f"ошибка выполнения метода {obj_type.__name__}.{method_name}")
            
            
            func = eval_expr(callable_node, current_env)


            if isinstance(func, BoundMethod):
                if func.function.name.startswith('__'):
                    current_self = current_env.get('__current_self__')
                    if current_self is not func.instance:
                        raise DarkRuntimeError(f"не удается вызвать приватный метод '{func.function.name}' объекта '{func.instance.klass.name}'", line=line)

                method_args = [func.instance] + args
                return call_dark_function(func.function, method_args, line, self_instance=func.instance)

            if isinstance(func, DarkClass):
                instance = DarkInstance(func)
                constructor = func.find_method('__main__')
                if constructor:
                    constructor_args = [instance] + args
                    call_dark_function(constructor, constructor_args, line, self_instance=instance)
                elif args:
                    raise DarkRuntimeError(f"Class '{func.name}' does not have a constructor to accept arguments.", line=line)
                return instance

            if isinstance(func, Function):
                return call_dark_function(func, args, line)
            
            if callable(func): 
                try:
                    return func(args)
                except TypeError as e:
                    raise DarkRuntimeError(f"ошибка вызова нативной функции: {e}", line=line) from e

            raise DarkRuntimeError(f"объект не является функцией и не может быть вызван", line=line)

    def run_stmt(s, current_env):
        line = s[-1]
        try:
            typ = s[0]
            if typ == 'print':
                values = [_dark_obj_to_str(eval_expr(arg, current_env), current_env) for arg in s[1]]
                print(*values, end='')
            elif typ == 'println':
                values = [_dark_obj_to_str(eval_expr(arg, current_env), current_env) for arg in s[1]]
                print(*values)
            elif typ == 'import':
                module_name = s[1]
                if module_name in modules:
                    return 

                if module_name in NATIVE_MODULES:
                    modules[module_name] = NATIVE_MODULES[module_name]
                    return

                
                py_ext_path = None
                search_dir = script_dir
                while True:
                    potential_ext_dir = os.path.join(search_dir, 'dark_extensions')
                    potential_py_path = os.path.join(potential_ext_dir, module_name + ".py")
                    if os.path.exists(potential_py_path):
                        py_ext_path = potential_py_path
                        break
                    
                    parent_dir = os.path.dirname(search_dir)
                    if parent_dir == search_dir: 
                        break
                    search_dir = parent_dir

                if py_ext_path:
                    try:
                        ext_dir = os.path.dirname(py_ext_path)
                        if ext_dir not in sys.path:
                            sys.path.insert(0, ext_dir)
                        
                        py_module = __import__(module_name)
                        
                        if hasattr(py_module, 'get_module') and callable(py_module.get_module):
                            modules[module_name] = py_module.get_module(use_tkinter=use_tkinter)
                            return
                        else:
                            raise DarkRuntimeError(f"Python extension '{module_name}' does not have a callable 'get_module' function.", line=line)
                    except ImportError as e:
                        raise DarkRuntimeError(f"Failed to import Python extension '{module_name}': {e}", line=line)
                    except Exception as e:
                        raise DarkRuntimeError(f"Error loading Python extension '{module_name}': {e}", line=line)

                
                module_path = os.path.join(script_dir, module_name + ".dark")
                canonical_path = os.path.abspath(module_path)

                if not os.path.exists(canonical_path):
                    raise DarkRuntimeError(f"не удалось найти модуль или Python-расширение: {module_name}", line=line)
                else:
                    if canonical_path in imported_files:
                        return

                    imported_files.add(canonical_path)

                    with open(canonical_path, 'r', encoding='utf-8') as f:
                        src = f.read()
                    try:
                        tokens = lex(src)
                        module_ast = Parser(tokens).parse()
                        module_dir = os.path.dirname(canonical_path)
                        module_env = {}
                        modules[module_name] = module_env
                        module_env['__file__'] = canonical_path 
                        
                        run(module_ast, env=module_env, script_dir=module_dir, imported_files=imported_files, modules=modules, use_with_python=use_with_python)
                    except DarkError as e:
                        raise DarkRuntimeError(f"Error in module '{module_name}' ({canonical_path}):\n{e}", line=line)
            elif typ == 'func_def':
                name, params, body = s[1], s[2], s[3]
                func = Function(name, params, body, dict(current_env))
                func.definition_env['__file__'] = current_env.get('__file__', '<main>')
                current_env[name] = func 
                func.definition_env[name] = func 
            elif typ == 'class_def':
                name, base_class_name, method_nodes, line = s[1], s[2], s[3], s[4]
                
                base_class = None
                if base_class_name:
                    base_class = current_env.get(base_class_name)
                    if not isinstance(base_class, DarkClass):
                        raise DarkRuntimeError(f"Base class '{base_class_name}' not found or is not a class.", line=line)

                methods = {}
                for method_node in method_nodes:
                    if method_node[0] != 'func_def':
                        raise DarkRuntimeError("Only functions can be defined in a class.", line=method_node[4])
                    func_name, params, body, _ = method_node[1], method_node[2], method_node[3], method_node[4]
                    if not params:
                        raise DarkRuntimeError(f"Method '{func_name}' must have at least one parameter for the instance.", line=method_node[4])
                    method_func = Function(func_name, params, body, dict(current_env))
                    method_func.definition_env['__file__'] = current_env.get('__file__', '<main>')
                    methods[func_name] = method_func

                new_class = DarkClass(name, base_class, methods)
                current_env[name] = new_class

                for method in methods.values():
                    method.definition_env[name] = new_class
            elif typ == 'return':
                val_expr = s[1]
                return_val = 0
                if val_expr:
                    return_val = eval_expr(val_expr, current_env)
                raise ReturnSignal(return_val)
            elif typ == 'assign':
                current_env[s[1]] = eval_expr(s[2], current_env)
            elif typ == 'member_assign':
                obj_node, member_name, value_node, line = s[1], s[2], s[3], s[4]
                obj = eval_expr(obj_node, current_env)
                value = eval_expr(value_node, current_env)
                
                if not isinstance(obj, DarkInstance):
                    raise DarkRuntimeError(f"Only instances can have attributes assigned.", line=line)
                
                if member_name.startswith('__'):
                    current_self = current_env.get('__current_self__')
                    if current_self is not obj:
                        raise DarkRuntimeError(f"не удается установить приватный атрибут '{member_name}' для объекта '{obj.klass.name}'", line=line)

                obj.fields[member_name] = value
            elif typ == 'index_assign':
                collection_node, index_node, value_node = s[1], s[2], s[3]
                collection = eval_expr(collection_node, current_env)
                index = eval_expr(index_node, current_env)
                value = eval_expr(value_node, current_env)
                if isinstance(collection, (list, dict)):
                    if isinstance(collection, list):
                        if not isinstance(index, int):
                            raise DarkRuntimeError(f"индексы списка должны быть целыми числами, а не '{type(index).__name__}'", line=line)
                        if index < -len(collection) or index >= len(collection):
                            raise DarkRuntimeError(f"индекс {index} вне допустимого диапазона для присваивания в списке размером {len(collection)}", line=line)
                        collection[index] = value
                    elif isinstance(collection, dict):
                        if not isinstance(index, (str, int, bool)):
                             raise DarkRuntimeError(f"недопустимый тип ключа для словаря: '{type(index).__name__}'", line=line)
                        collection[index] = value
                else:
                    raise DarkRuntimeError(f"объект типа '{type(collection).__name__}' не поддерживает присваивание по индексу", line=line)
            elif typ == 'if':
                clauses, false_body = s[1], s[2]
                executed = False
                for cond_expr, body in clauses:
                    if is_truthy(eval_expr(cond_expr, current_env)):
                        for stmt_node in body:
                            run_stmt(stmt_node, current_env)
                        executed = True
                        break
                if not executed and false_body is not None:
                    for stmt_node in false_body:
                        run_stmt(stmt_node, current_env)
            elif typ == 'while':
                while is_truthy(eval_expr(s[1], current_env)):
                    for st in s[2]: run_stmt(st, current_env)
            elif typ == 'for':
                var_name, iterable_expr, body = s[1], s[2], s[3]
                iterable = eval_expr(iterable_expr, current_env)
                
                if not isinstance(iterable, (list, str, dict)):
                     raise DarkRuntimeError(f"объект типа '{type(iterable).__name__}' не является итерируемым", line=line)

                items_to_iterate = iterable
                if isinstance(iterable, dict):
                    items_to_iterate = list(iterable.keys())

                for item in items_to_iterate:
                    current_env[var_name] = item
                    for stmt_node in body:
                        run_stmt(stmt_node, current_env)
            elif typ == 'expr':
                eval_expr(s[1], current_env)
            elif typ == 'try_except':
                try_body, except_var, except_body, line = s[1], s[2], s[3], s[4]
                try:
                    for stmt_node in try_body:
                        run_stmt(stmt_node, current_env)
                except DarkRuntimeError as e:
                    
                    
                    
                    except_env = dict(current_env)
                    original_value = None
                    had_original_value = False

                    if except_var:
                        error_obj = {
                            'message': str(e.message),
                            'line': e.line,
                            'col': e.col
                        }
                        if except_var in except_env:
                            had_original_value = True
                            original_value = except_env[except_var]
                        except_env[except_var] = error_obj
                    
                    try:
                        for stmt_node in except_body:
                            run_stmt(stmt_node, except_env)
                    finally:
                        if except_var:
                            if had_original_value:
                                pass
                            else:
                                pass
        except (TypeError, NameError, RuntimeError, IndexError, KeyError, DarkRuntimeError) as e:
            if isinstance(e, DarkRuntimeError):
                e.line = e.line or line
                raise e
            raise DarkRuntimeError(str(e), line=line)

    try:
        if '__file__' not in env:
            env['__file__'] = os.path.abspath(source_name)
        for st in ast[1]:
            run_stmt(st, env)
    except ReturnSignal as e:
        return e.value
    return env