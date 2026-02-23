from dark_code.dark_lang import DarkCompileError


OP_TO_METHOD = {
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
    '<>': '__ne__',
}
OP_TO_RMETHOD = {
    '+': '__radd__',
    '-': '__rsub__',
    '*': '__rmul__',
    '/': '__rdiv__',
}
METHOD_TO_OP = {
    '__add__': '+',
    '__sub__': '-',
    '__mul__': '*',
    '__div__': '/',
    '__lt__': '<',
    '__gt__': '>',
    '__le__': '<=',
    '__ge__': '>=',
    '__eq__': '==',
    '__ne__': '!=',
}

BUILTINS = {
    # "функция": ["значение в Nim", Возвращает?, какой тип данных вернёт?]
    "print": ["print", False, None],
    "println": ["println", False, None],
    "input": ["input", True, "str"],
    "to_int": ["to_int", True, "num"],
    "to_float": ["to_float", True, "float"],
    "to_str": ["to_str", True, "str"],
    "type": ["dark_type", True, "str"]
}

class NIMTranspiler:
    def __init__(self):
        self.scopes = [{}]
        self.functions = {}
        self.nim_code = "import dark/builtins\n\n"
        self.current_class = None
        self.class_fields = {}
        self.class_methods = {}
        self.class_parents = {}
        self.class_generic_params = {}
        self.class_constructor_param_to_field = {}
        self.indent_level = 0
        self.import_tables = True


    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def define(self, name, var_type):
        self.scopes[-1][name] = var_type

    def find(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def find_class_method(self, class_name, method_name):
        if class_name in self.class_methods and method_name in self.class_methods[class_name]:
            return True
        
        parent = self.class_parents.get(class_name)
        if parent:
            return self.find_class_method(parent, method_name)
            
        return False

    def find_class_in_ast(self, ast, class_name):
        for stmt in ast[1]:
            if stmt[0] == 'class_def' and stmt[1] == class_name:
                return stmt
        return None

    def get_all_methods_from_class_ast(self, class_ast):
        if not class_ast:
            return []
        
        methods = class_ast[3]
        all_methods = []
        queue = list(methods)
        visited_methods = set()

        while queue:
            method_node = queue.pop(0)
            if method_node[0] == 'func_def':
                method_name, _, method_body, _ = method_node[1:5]
                if method_name in visited_methods: continue
                visited_methods.add(method_name)

                for stmt_in_body in method_body:
                    if stmt_in_body[0] == 'func_def':
                        queue.append(stmt_in_body)
                all_methods.append(method_node)
        return all_methods

    def transpile(self, ast, code_buffer=None, indent_level=0):
        self.indent_level = indent_level
        indent = "    " * self.indent_level
        code = code_buffer if code_buffer is not None else ast[1]

        for stmt in code:
            stmt_type = stmt[0]
            if stmt_type in ('print', 'println'):
                args_nim = []
                for arg in stmt[1]:
                    nim_expr, expr_type = self.transpile_expr(arg, log=True)
                    if expr_type == 'JsonNode':
                        args_nim.append(f"(if {nim_expr}.kind == JString: {nim_expr}.getStr() else: ${nim_expr})")
                    else:
                        args_nim.append(f"$({nim_expr})")
                
                self.nim_code += f"{indent}{BUILTINS[stmt_type][0]}({', '.join(args_nim)})\n"
            elif stmt_type == 'assign':
                var_name = stmt[1]
                expr_node = stmt[2]
                is_new_var = self.find(var_name) is None
                nim_expr, expr_type = self.transpile_expr(expr_node, log=True)
                declaration = 'var ' if is_new_var else ''
                self.nim_code += f"{indent}{declaration}{var_name} = {nim_expr}\n"
                if is_new_var:
                    self.define(var_name, expr_type)
            elif stmt_type == 'if':
                clauses, false_body, line = stmt[1], stmt[2], stmt[3]
                for i, (condition, body) in enumerate(clauses):
                    keyword = "if" if i == 0 else "elif"
                    self.nim_code += f"{indent}{keyword} {self.transpile_expr(condition)}:\n"
                    self.enter_scope()
                    self.transpile(ast, code_buffer=body, indent_level=self.indent_level + 1)
                    self.exit_scope()
                if false_body:
                    self.nim_code += f"{indent}else:\n"
                    self.enter_scope()
                    self.transpile(ast, code_buffer=false_body, indent_level=self.indent_level)
                    self.exit_scope()
            elif stmt_type == 'while':
                cond, body, line = stmt[1], stmt[2], stmt[3]
                self.nim_code += f"{indent}while {self.transpile_expr(cond)}:\n"
                self.enter_scope()
                self.transpile(ast, code_buffer=body, indent_level=self.indent_level + 1)
                self.exit_scope()
            elif stmt_type == 'for':
                var_name, iterable_expr, body, line = stmt[1], stmt[2], stmt[3], stmt[4]
                self.nim_code += f"{indent}for {var_name} in {self.transpile_expr(iterable_expr)}:\n"
                self.enter_scope()
                self.define(var_name, 'auto')
                self.transpile(ast, code_buffer=body, indent_level=self.indent_level + 1)
                self.exit_scope()
            # elif stmt_type == 'try_except': # ('try_except', [('assign', 'result', ('binop', '/', ('num', 10, 3), ('num', 0, 3), 3), 3)], 'e', [('println', [('binop', '+', ('str', 'Произошла ошибка: ', '"', 5), ('index_access', ('var', 'e', 5), ('str', 'message', '"', 5), 5), 5)], 5)], 2)
            #     try_body, except_name_var, except_body, line = stmt[1], stmt[2], stmt[3], stmt[4]
            #     self.nim_code += f"{indent}try:\n"
            #     self.enter_scope()
            #     self.transpile(ast, code_buffer=try_body, indent_level=self.indent_level + 1)
            #     self.exit_scope()
            #     self.nim_code += f"{indent}except Exception as {except_name_var}:\n"
            #     self.enter_scope()
            #     if except_name_var:
            #         self.define(except_name_var, 'Exception')
            #     self.transpile(ast, code_buffer=except_body, indent_level=self.indent_level + 1)
            #     self.exit_scope()
            elif stmt_type == 'member_assign':
                obj_node, member_name, value_node, line = stmt[1], stmt[2], stmt[3], stmt[4]
                obj_nim, obj_type = self.transpile_expr(obj_node, log=True)
                value_nim, _ = self.transpile_expr(value_node, log=True)
                nim_member_name = member_name[2:] if member_name.startswith("__") else member_name
                self.nim_code += f"{indent}{obj_nim}.{nim_member_name} = {value_nim}\n"
            elif stmt_type == 'func_def':
                func_name, func_params, func_body, line = stmt[1], stmt[2], stmt[3], stmt[4]
                
                clean_body = [s for s in func_body if s[0] != 'func_def']
                if not self.current_class:
                    nested_funcs = [s for s in func_body if s[0] == 'func_def']
                    for f in nested_funcs:
                        self.transpile(ast, code_buffer=[f], indent_level=self.indent_level)

                if self.current_class:
                    self_param_name = func_params[0]
                    other_params = func_params[1:]

                    if func_name == '__main__':
                        nim_params = []
                        constructor_generics = []
                        param_to_field = self.class_constructor_param_to_field.get(self.current_class, {})

                        for p in other_params:
                            if p in param_to_field:
                                field_name = param_to_field[p]
                                generic_type = self.class_fields[self.current_class].get(field_name)
                                if not generic_type:
                                    parent = self.class_parents.get(self.current_class)
                                    if parent:
                                        if field_name in self.class_fields.get(parent, {}):
                                            generic_type = self.class_fields[parent].get(field_name)
                                if generic_type and generic_type in self.class_generic_params.get(self.current_class, []):
                                    nim_params.append(f"{p}: {generic_type}")
                                    if generic_type not in constructor_generics:
                                        constructor_generics.append(generic_type)
                                else:
                                    nim_params.append(f"{p}: auto")
                            else:
                                nim_params.append(f"{p}: auto")
                        
                        nim_params_str = ", ".join(nim_params)
                        proc_generic_part = ""
                        if constructor_generics:
                            proc_generic_part = f"[{', '.join(sorted(constructor_generics))}]"
                        
                        class_generics = self.class_generic_params.get(self.current_class, [])
                        return_type_generic_part = ""
                        if class_generics:
                            return_type_generic_part = f"[{', '.join(sorted(class_generics))}]"

                        self.indent_level = 0
                        indent = "    " * self.indent_level
                        self.nim_code += f"{indent}proc new{self.current_class}*{proc_generic_part}({nim_params_str}): {self.current_class}{return_type_generic_part} =\n"
                        body_indent = "    " * (self.indent_level + 1)
                        self.nim_code += f"{body_indent}new(result)\n"
                        
                        self.enter_scope()
                        self.define(self_param_name, 'constructor_self')
                        for p in other_params:
                            self.define(p, 'auto')
                        self.transpile(ast, code_buffer=clean_body, indent_level=self.indent_level + 1)
                        self.exit_scope()
                        
                    elif func_name == '__str__':
                        class_generics = self.class_generic_params.get(self.current_class, [])
                        proc_generic_part = ""
                        if class_generics:
                            proc_generic_part = f"[{', '.join(sorted(class_generics))}]"
                        
                        self.indent_level = 0
                        indent = "    " * self.indent_level
                        self.nim_code += f"{indent}proc `$`*{proc_generic_part}(self: {self.current_class}{proc_generic_part}): string =\n"
                        self.enter_scope()
                        self.define(self_param_name, 'method_self')
                        self.transpile(ast, code_buffer=clean_body, indent_level=self.indent_level + 1)
                        self.exit_scope()
                        
                    elif func_name in METHOD_TO_OP:
                        op = METHOD_TO_OP[func_name]
                        other_params = func_params[1:]
                        other_param_nim = f"{other_params[0]}: auto"

                        class_generics = self.class_generic_params.get(self.current_class, [])
                        proc_generic_part = ""
                        if class_generics:
                            proc_generic_part = f"[{', '.join(sorted(class_generics))}]"
                        
                        return_type = 'auto'
                        for body_stmt in clean_body:
                            if body_stmt[0] == 'return' and body_stmt[1] is not None:
                                _, return_type = self.transpile_expr(body_stmt[1], log=True)
                                break

                        if return_type == self.current_class and class_generics:
                            return_type += proc_generic_part

                        proc_or_method = "proc"

                        self.indent_level = 0
                        indent = "    " * self.indent_level
                        self.nim_code += f"{indent}{proc_or_method} `{op}`*{proc_generic_part}(self: {self.current_class}{proc_generic_part}; {other_param_nim}): {return_type} =\n"
                        self.enter_scope()
                        self.define(self_param_name, 'method_self')
                        self.define(other_params[0], 'auto')
                        self.transpile(ast, code_buffer=clean_body, indent_level=self.indent_level + 1)
                        self.exit_scope()
                        
                    else:  
                        class_generics = self.class_generic_params.get(self.current_class, [])
                        proc_generic_part = ""
                        if class_generics:
                            proc_generic_part = f"[{', '.join(sorted(class_generics))}]"
                        class_generic_part_for_self = proc_generic_part

                        nim_params_str = "; ".join([f"{p}: auto" for p in other_params])
                        if nim_params_str:
                            nim_params_str = "; " + nim_params_str
                        
                        return_type = 'auto'
                        for body_stmt in clean_body:
                            if body_stmt[0] == 'return' and body_stmt[1] is not None:
                                _, return_type = self.transpile_expr(body_stmt[1], log=True)
                                break

                        proc_or_method = "method"
                        parent = self.class_parents.get(self.current_class)
                        is_override = parent and self.find_class_method(parent, func_name)
                        
                        base_pragma = ""
                        if not is_override:
                            base_pragma = " {.base.}"
                        
                        self.indent_level = 0
                        indent = "    " * self.indent_level
                        self.nim_code += f"{indent}{proc_or_method} {func_name}*{proc_generic_part}(self: {self.current_class}{class_generic_part_for_self}{nim_params_str}): {return_type}{base_pragma} =\n"
                        self.enter_scope()
                        self.define(self_param_name, 'method_self')
                        for p in other_params:
                            self.define(p, 'auto')
                        self.transpile(ast, code_buffer=clean_body, indent_level=self.indent_level + 1)
                        self.exit_scope()
                else:
                    nim_params = [f"{p}: auto" for p in func_params]
                    
                    return_type = 'void'
                    has_return_value = False
                    for body_stmt in clean_body:
                        if body_stmt[0] == 'return' and body_stmt[1] is not None:
                            has_return_value = True
                            _, return_type = self.transpile_expr(body_stmt[1], log=True)
                            break
                    self.functions[func_name] = [has_return_value, return_type]

                    self.nim_code += f"{indent}proc {func_name}*({', '.join(nim_params)}): auto =\n"
                    self.enter_scope()
                    for param in func_params:
                        self.define(param, 'auto')
                    self.transpile(ast, code_buffer=clean_body, indent_level=self.indent_level + 1)
                    self.exit_scope()
            elif stmt_type == 'class_def':
                class_name, base_class_node, methods, line = stmt[1], stmt[2], stmt[3], stmt[4]
                self.current_class = class_name
                self.class_fields[class_name] = {}
                self.class_methods[class_name] = set()
                self.class_generic_params[class_name] = []
                self.class_constructor_param_to_field[class_name] = {}
                if base_class_node:
                    parent_for_lookup = base_class_node
                    while isinstance(parent_for_lookup, tuple) and parent_for_lookup[0] in ('type_inst', 'var'):
                        parent_for_lookup = parent_for_lookup[1]
                    self.class_parents[class_name] = str(parent_for_lookup)

                def stringify_type_spec(node):
                    if not isinstance(node, tuple):
                        return str(node)
                    
                    if node[0] == 'var':
                        return node[1]
                    elif node[0] == 'type_inst':
                        base = stringify_type_spec(node[1])
                        params = ", ".join([stringify_type_spec(p) for p in node[2]])
                        return f"{base}[{params}]"
                    return "RootObj"

                all_methods = self.get_all_methods_from_class_ast(stmt)

                for method_node in all_methods:
                    if method_node[0] == 'func_def':
                        method_name, method_params, method_body, _ = method_node[1:5]
                        self.class_methods[class_name].add(method_name)
                        
                        self_param_name = method_params[0] if method_params else None
                        if not self_param_name: continue
                        
                        q = list(method_body)
                        while q:
                            node = q.pop(0)
                            if not isinstance(node, tuple): continue
                            
                            if node[0] == 'member_assign' and node[1][0] == 'var' and node[1][1] == self_param_name:
                                field_name = node[2]
                                value_node = node[3]
                                
                                if method_name == '__main__' and value_node[0] == 'var' and value_node[1] in method_params[1:]:
                                    param_name = value_node[1]
                                    self.class_constructor_param_to_field[class_name][param_name] = field_name
                                    generic_param_name = f"T{param_name.capitalize()}"
                                    self.class_fields[class_name][field_name] = generic_param_name
                                    if generic_param_name not in self.class_generic_params[class_name]:
                                        self.class_generic_params[class_name].append(generic_param_name)
                                elif field_name not in self.class_fields[class_name]:
                                    self.class_fields[class_name][field_name] = 'auto'
                            
                            for child in node:
                                if isinstance(child, list):
                                    q.extend(child)
                                elif isinstance(child, tuple):
                                    q.append(child)

                parent_name = self.class_parents.get(class_name)
                if parent_name:
                    parent_mapping = self.class_constructor_param_to_field.get(parent_name, {})
                    for p, f in parent_mapping.items():
                        if p not in self.class_constructor_param_to_field[class_name]:
                            self.class_constructor_param_to_field[class_name][p] = f

                parent_name = self.class_parents.get(class_name)
                if parent_name:
                    parent_generics = self.class_generic_params.get(parent_name, [])
                    for gp in parent_generics:
                        if gp not in self.class_generic_params[class_name]:
                            self.class_generic_params[class_name].append(gp)

                generic_part = ""
                if self.class_generic_params[class_name]:
                    generic_part = f"[{', '.join(sorted(self.class_generic_params[class_name]))}]"

                self.nim_code += f"{indent}type {class_name}*{generic_part} = ref object of "
                if parent_name:
                    base_type_str = stringify_type_spec(base_class_node)
                    parent_generics_for_base = self.class_generic_params.get(parent_name, [])
                    if parent_generics_for_base and '[' not in base_type_str:
                        base_type_str += f"[{', '.join(sorted(parent_generics_for_base))}]"

                    self.nim_code += f"{base_type_str}\n"
                elif base_class_node:
                     self.nim_code += f"{stringify_type_spec(base_class_node)}\n"
                else:
                    self.nim_code += "RootObj\n" 
                
                for field, field_type in sorted(self.class_fields[class_name].items()):
                    nim_field_name = field
                    is_public = True
                    if field.startswith("__"):
                        nim_field_name = field[2:]
                        is_public = False
                    
                    if not nim_field_name: continue

                    export_marker = "*" if is_public else ""
                    self.nim_code += f"{indent}  {nim_field_name}{export_marker}: {field_type}\n"
                self.nim_code += "\n"
                
                self.enter_scope()

                if not self.find_class_method(class_name, '__str__'):
                    class_generics = self.class_generic_params.get(class_name, [])
                    proc_generic_part = ""
                    if class_generics:
                        proc_generic_part = f"[{', '.join(sorted(class_generics))}]"
                    
                    self.nim_code += f"{indent}proc `$`*{proc_generic_part}(self: {class_name}{proc_generic_part}): string =\n"
                    self.nim_code += f"{indent}  result = \"<instance of {class_name} object at 0x\" & $cast[uint64](self) & \">\"\n\n"

                has_own_constructor = any(m[1] == '__main__' for m in all_methods)
                if not has_own_constructor and parent_name:
                    parent_class_ast = self.find_class_in_ast(ast, parent_name)
                    if parent_class_ast:
                        parent_all_methods = self.get_all_methods_from_class_ast(parent_class_ast)
                        parent_constructor_ast = next((m for m in parent_all_methods if m[1] == '__main__'), None)
                        if parent_constructor_ast:
                            self.transpile(ast, code_buffer=[parent_constructor_ast], indent_level=self.indent_level)

                for method_node in all_methods:
                    method_name, method_params, method_body, method_line = method_node[1:5]
                    clean_body = [s for s in method_body if s[0] != 'func_def']
                    clean_method_node = ('func_def', method_name, method_params, clean_body, method_line)
                    self.transpile(ast, code_buffer=[clean_method_node], indent_level=self.indent_level)
                self.exit_scope()
                self.current_class = None
            elif stmt_type == 'return':
                if stmt[1]:
                    self.nim_code += f"{indent}return {self.transpile_expr(stmt[1])}\n"
                else:
                    self.nim_code += f"{indent}return\n"
            elif stmt_type == 'expr':
                expr_node = stmt[1]
                nim_expr = self.transpile_expr(expr_node)
                is_proc = False
                if expr_node[0] == 'func_call':
                    func_name = expr_node[1][1]
                    func_info = self.functions.get(func_name)
                    if func_info and not func_info[0]:
                        is_proc = True
                elif expr_node[0] in ('print', 'println'):
                    is_proc = True
                
                if not is_proc:
                    self.nim_code += f"{indent}discard {nim_expr}\n"
                else:
                    self.nim_code += f"{indent}{nim_expr}\n"

        return self.nim_code

    def transpile_expr(self, expr, log=False):
        if not isinstance(expr, tuple) or not expr:
            raise DarkCompileError(f"Неверный узел выражения: {expr}")

        if expr[0] == 'var':
            var_name = expr[1]
            var_info = self.find(var_name)
            if var_info == 'constructor_self':
                if log: return 'result', self.current_class
                return 'result'
            if var_info == 'method_self':
                if log: return 'self', self.current_class
                return 'self'

            var_type = var_info or 'auto'
            if log:
                return var_name, var_type
            return var_name
        elif expr[0] == 'binop':
            op = expr[1]
            left_node, right_node, line = expr[2], expr[3], expr[4]
            left_nim, left_type = self.transpile_expr(left_node, log=True)
            right_nim, right_type = self.transpile_expr(right_node, log=True)

            method_name = OP_TO_METHOD.get(op)
            if left_type in self.class_methods and method_name and self.find_class_method(left_type, method_name):
                result = f"({left_nim} {op} {right_nim})"
                if log: return result, 'auto'
                return result

            rmethod_name = OP_TO_RMETHOD.get(op)
            if right_type in self.class_methods and rmethod_name and self.find_class_method(right_type, rmethod_name):
                result = f"({left_nim} {op} {right_nim})"
                if log: return result, 'auto'
                return result

            nim_op = op
            final_type = 'auto'
            if op == '+' and (left_type == 'string' or right_type == 'string'):
                nim_op = '&'
                left_nim = f"$({left_nim})"
                right_nim = f"$({right_nim})"
                final_type = 'string'
            else:
                final_type = 'int' if left_type == 'int' and right_type == 'int' else 'float'
            
            result = f"({left_nim} {nim_op} {right_nim})"
            if log:
                return result, final_type
            return result
        elif expr[0] == 'logical_op':
            op, left, right, line = expr[1], expr[2], expr[3], expr[4]
            left_nim = self.transpile_expr(left)
            right_nim = self.transpile_expr(right)
            result = f"({left_nim} {op} {right_nim})"
            if log:
                return result, 'bool'
            return result
        elif expr[0] == 'unary':
            op, node, line = expr[1], expr[2], expr[3]
            node_nim = self.transpile_expr(node)
            result = f"{op} ({node_nim})"
            if log:
                _, node_type = self.transpile_expr(node, log=True)
                return_type = 'bool' if op == 'not' else node_type
                return result, return_type
            return result
        elif expr[0] == 'num':
            if log:
                return str(expr[1]), 'int'
            return str(expr[1])
        elif expr[0] == 'str':
            result = expr[1].replace('\n', '\\n').replace('\t', '\\t')
            if log:
                return f'"{result}"', 'string'
            return f'"{result}"' 
        elif expr[0] == 'float':
            if log:
                return str(expr[1]), 'float'
            return str(expr[1])
        elif expr[0] == 'bool':
            nim_bool = 'true' if expr[1] else 'false'
            if log:
                return nim_bool, 'bool'
            return nim_bool
        elif expr[0] == 'list':
            elements = [self.transpile_expr(e) for e in expr[1]]
            nim_list = f"@[{', '.join(elements)}]"
            if log:
                return nim_list, 'seq'
            return nim_list
        elif expr[0] == 'index_access': # ('index_access', ('var', 'my_list', 3), ('num', 1, 3), 3)
            collection_nim, collection_type = self.transpile_expr(expr[1], log=True)
            index_nim = self.transpile_expr(expr[2])
            result = f"{collection_nim}[{index_nim}]"
            
            result_type = 'auto'
            if collection_type == "JsonNode":
                result_type = "JsonNode"
            
            if log:
                return result, result_type
            return result
        elif expr[0] == 'dict':
            if self.import_tables:
                self.nim_code = "import json\n" + self.nim_code
                self.import_tables = False
            
            pairs_nim = []
            for k, v in expr[1]:
                key_nim = self.transpile_expr(k)
                value_nim = self.transpile_expr(v)
                pairs_nim.append(f"{key_nim}: {value_nim}")
            
            nim_dict = f"%*{{{', '.join(pairs_nim)}}}"
            
            if log:
                return nim_dict, "JsonNode"
            return nim_dict
        elif expr[0] == 'member_access': # ('member_access', ('var', 'person', 8), 'age', 8) = person.age
            obj_nim, obj_type = self.transpile_expr(expr[1], log=True)
            member_name = expr[2]
            nim_member_name = member_name[2:] if member_name.startswith("__") else member_name

            if obj_type == "JsonNode":
                result = f'{obj_nim}["{member_name}"]'
                result_type = "JsonNode"
            else:
                result = f"{obj_nim}.{nim_member_name}"
                result_type = 'auto'
            
            if log:
                return result, result_type
            return result
        elif expr[0] == 'func_call':
            callable_node, arg_nodes, line = expr[1], expr[2], expr[3]
            
            if callable_node[0] == 'var' and callable_node[1] in self.class_fields:
                class_name = callable_node[1]
                func_args = [self.transpile_expr(arg) for arg in arg_nodes]
                result = f"new{class_name}({', '.join(func_args)})"
                if log:
                    return result, class_name
                return result

            if callable_node[0] == 'member_access':
                obj_node, method_name, _ = callable_node[1], callable_node[2], callable_node[3]
                obj_nim, obj_type = self.transpile_expr(obj_node, log=True)

                if method_name == '__str__':
                    result = f"$({obj_nim})"
                    if log: return result, 'string'
                    return result

                if method_name in METHOD_TO_OP:
                    op = METHOD_TO_OP[method_name]
                    arg_nim = self.transpile_expr(arg_nodes[0])
                    result = f"({obj_nim} {op} {arg_nim})"
                    if log: return result, 'auto'
                    return result

                args_nim = [self.transpile_expr(arg) for arg in arg_nodes]
                result = f"{obj_nim}.{method_name}({', '.join(args_nim)})"
                if log: return result, 'auto'
                return result

            func_name = callable_node[1]
            if func_name not in self.functions and func_name not in BUILTINS:
                raise DarkCompileError(f"Функция '{func_name}' не определена", line=line)
            return self.transpile_expr_default_func_call(expr, log)
        elif expr[0] in BUILTINS:
            nim_name, returns_value, return_type = BUILTINS[expr[0]]
            if expr[0] == 'input':
                result = f"{nim_name}()"
            elif expr[0] == 'to_str':
                arg_nim, arg_type = self.transpile_expr(expr[1], log=True)
                if arg_type in self.class_methods and self.find_class_method(arg_type, '__str__'):
                    result = f"{arg_nim}.__str__()"
                else:
                    result = f"{nim_name}({arg_nim})"
            else:
                arg = self.transpile_expr(expr[1])
                result = f"{nim_name}({arg})"
            if log:
                return result, return_type
            return result
        else:
            raise DarkCompileError(f"Неподдерживаемый тип выражения для транспиляции: {expr[0]}", line=expr[-1] if isinstance(expr[-1], int) else None)

    def transpile_expr_default_func_call(self, expr, log=False):
        callable_node, arg_nodes, line = expr[1], expr[2], expr[3]
        func_name = callable_node[1]
        func_args = [self.transpile_expr(arg) for arg in arg_nodes]
        result = f"{func_name}({', '.join(func_args)})"
        
        if log:
            return_type = 'auto'
            if func_name in self.functions: return_type = self.functions[func_name][1]
            elif func_name in BUILTINS: return_type = BUILTINS[func_name][2]
            return result, return_type
        return result
