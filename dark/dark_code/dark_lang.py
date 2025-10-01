import re
import os
import sys
from dark_code.native_modules import NATIVE_MODULES
from dark_code.dark_exceptions import DarkSyntaxError, DarkRuntimeError, DarkError


class Token:
    def __init__(self, t, v=None, line=None, col=None):
        self.type = t
        self.value = v
        self.line = line
        self.col = col
    def __repr__(self):
        return f"Token({self.type},{repr(self.value)},{self.line},{self.col})"

TOKEN_SPEC = [
    ('NUMBER',  r'(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'),
    ('ID',      r'[A-Za-z_]\w*'),
    ('STRING',  r'"""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\\\'])*\''),
    ('COMMENT', r'#.*'),
    ('RELOP',   r'==|!=|<=|>=|<|>'),
    ('OP',      r'[\+\-\*/]'),
    ('ASSIGN',  r'='),
    ('LPAR',    r'\('),
    ('RPAR',    r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('COLON',    r':'),
    ('COMMA',   r','),
    ('DOT',     r'\.'),
    ('SEMI',    r';'),
    ('SKIP',    r'[ \t]+'),
    ('NEWLINE', r'\n'),
]
TOKEN_SPEC.append(('MISMATCH', r'.')) 
KEYWORDS = {'print','println','if','then','end','while','do','input','to_int','to_str','type','else', 'import', 'true', 'false', 'function', 'return', 'for', 'in', 'to_float', 'try', 'except', 'and', 'or', 'not', 'class'}
master_re = re.compile('|'.join(f'(?P<{name}>{pattern})' for name,pattern in TOKEN_SPEC))

def lex(text):
    pos = 0
    tokens = []
    line_num = 1
    line_start = 0
    while pos < len(text):
        m = master_re.match(text, pos)
        kind = m.lastgroup
        val = m.group(kind)
        col = m.start() - line_start + 1
        pos = m.end()
                
        if kind == 'NUMBER':
            is_float = '.' in val or 'e' in val.lower()
            val_to_store = float(val) if is_float else int(val)
            tokens.append(Token('NUMBER', val_to_store, line_num, col))
        elif kind == 'ID':
            if val in KEYWORDS:
                tokens.append(Token(val.upper(), line=line_num, col=col))
            else:
                tokens.append(Token('ID', val, line_num, col))
        elif kind == 'STRING':
            token_line_num = line_num
            if val.startswith('"""') or val.startswith("'''"):
                str_val = val[3:-3]
                num_newlines = val.count('\n')
                if num_newlines > 0:
                    line_num += num_newlines
                    line_start = m.start() + val.rfind('\n') + 1
            else:
                str_val = val[1:-1]

            processed_val = str_val.encode('raw_unicode_escape').decode('unicode_escape')
            tokens.append(Token('STRING', processed_val, token_line_num, col))
        elif kind == 'RELOP':
            tokens.append(Token('RELOP', val, line_num, col))
        elif kind == 'OP':
            tokens.append(Token('OP', val, line_num, col))
        elif kind in ('ASSIGN','LPAR','RPAR','SEMI', 'DOT', 'COMMA', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COLON'):
            tokens.append(Token(kind, val, line_num, col))
        elif kind == 'NEWLINE':
            tokens.append(Token('SEMI', line=line_num, col=col))
            line_num += 1
            line_start = pos
        elif kind == 'SKIP' or kind == 'COMMENT':
            continue
        elif kind == 'MISMATCH':
            tokens.append(Token('ERROR', f'Unexpected character: {val!r}', line_num, col))
            continue
    tokens.append(Token('EOF', line=line_num, col=1))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.errors = []
        
    def cur(self):
        return self.tokens[self.i]
    
    def eat(self, t=None):
        tok = self.cur()
        if t and tok.type != t:
            raise DarkSyntaxError(f'Expected {t}, got {tok.type}', line=tok.line, col=tok.col)
        self.i += 1
        return tok

    def recover(self):
        """
        Выполняет восстановление после синтаксической ошибки.
        Пропускает токены до тех пор, пока не найдет точку синхронизации (конец инструкции),
        чтобы парсер мог продолжить анализ с нового места.
        """
        while self.cur().type not in ('SEMI', 'EOF'):
            self.i += 1
        
        
        if self.cur().type == 'SEMI':
            self.eat('SEMI')

    def parse(self):
        stmts = []
        while self.cur().type != 'EOF':
            if self.cur().type == 'SEMI':
                self.eat('SEMI'); continue
            try:
                stmts.append(self.stmt())
            except DarkSyntaxError as e:
                self.errors.append(e)
                self.recover()
        return ('prog', stmts)

    def stmt(self):
        tok = self.cur()
        line = tok.line
        if tok.type == 'PRINT':
            self.eat('PRINT')
            self.eat('LPAR')
            args = []
            if self.cur().type != 'RPAR':
                args.append(self.expr())
                while self.cur().type == 'COMMA':
                    self.eat('COMMA')
                    if self.cur().type == 'RPAR': break
                    args.append(self.expr())
            self.eat('RPAR')
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('print', args, line)
        if tok.type == 'PRINTLN':
            self.eat('PRINTLN')
            self.eat('LPAR')
            args = []
            if self.cur().type != 'RPAR':
                args.append(self.expr())
                while self.cur().type == 'COMMA':
                    self.eat('COMMA')
                    if self.cur().type == 'RPAR': break
                    args.append(self.expr())
            self.eat('RPAR')
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('println', args, line)
        if tok.type == 'IMPORT':
            self.eat('IMPORT')
            module_name_tok = self.eat('STRING')
            module_name = module_name_tok.value
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('import', module_name, line)
        if tok.type == 'FUNCTION':
            self.eat('FUNCTION')
            name = self.eat('ID').value
            line = self.cur().line
            self.eat('LPAR')
            params = []
            if self.cur().type != 'RPAR':
                params.append(self.eat('ID').value)
                while self.cur().type == 'COMMA':
                    self.eat('COMMA')
                    params.append(self.eat('ID').value)
            self.eat('RPAR')
            while self.cur().type == 'SEMI':
                self.eat('SEMI')
            self.eat('DO')
            body = []
            while self.cur().type not in ('END', 'EOF'):
                if self.cur().type == 'SEMI': self.eat('SEMI'); continue
                body.append(self.stmt())
            self.eat('END')
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('func_def', name, params, body, line)
        if tok.type == 'RETURN':
            self.eat('RETURN')
            val_expr = None
            if self.cur().type not in ('SEMI', 'END', 'EOF'):
                val_expr = self.expr()
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('return', val_expr, line)
        if tok.type == 'IF':
            self.eat('IF')
            cond = self.expr()
            self.eat('THEN')
            
            true_body = []
            while self.cur().type not in ('ELSE', 'END', 'EOF'):
                if self.cur().type == 'SEMI':
                    self.eat('SEMI'); continue
                true_body.append(self.stmt())
            
            clauses = [(cond, true_body)]
            false_body = None
            
            while self.cur().type == 'ELSE':
                self.eat('ELSE')
                if self.cur().type == 'IF':
                    self.eat('IF')
                    elif_cond = self.expr()
                    self.eat('THEN')
                    elif_body = []
                    while self.cur().type not in ('ELSE', 'END', 'EOF'):
                        if self.cur().type == 'SEMI':
                            self.eat('SEMI'); continue
                        elif_body.append(self.stmt())
                    clauses.append((elif_cond, elif_body))
                else:
                    false_body = []
                    while self.cur().type not in ('END', 'EOF'):
                        if self.cur().type == 'SEMI':
                            self.eat('SEMI'); continue
                        false_body.append(self.stmt())
                    break
            
            self.eat('END')
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('if', clauses, false_body, line)
        if tok.type == 'WHILE':
            self.eat('WHILE')
            cond = self.expr()
            self.eat('DO')
            body = []
            while self.cur().type not in ('END','EOF'):
                if self.cur().type == 'SEMI':
                    self.eat('SEMI')
                    continue
                body.append(self.stmt())
            self.eat('END')
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('while', cond, body, line)
        if tok.type == 'FOR':
            self.eat('FOR')
            var_name = self.eat('ID').value
            self.eat('IN')
            iterable_expr = self.expr()
            self.eat('DO')
            body = []
            while self.cur().type not in ('END', 'EOF'):
                if self.cur().type == 'SEMI':
                    self.eat('SEMI')
                    continue
                body.append(self.stmt())
            self.eat('END')
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('for', var_name, iterable_expr, body, line)
        if tok.type == 'TRY':
            self.eat('TRY')
            self.eat('DO')
            try_body = []
            while self.cur().type not in ('EXCEPT', 'EOF'):
                if self.cur().type == 'SEMI': self.eat('SEMI'); continue
                try_body.append(self.stmt())
            
            self.eat('EXCEPT')
            except_var = None
            if self.cur().type == 'ID':
                except_var = self.eat('ID').value
            
            self.eat('DO')
            except_body = []
            while self.cur().type not in ('END', 'EOF'):
                if self.cur().type == 'SEMI': self.eat('SEMI'); continue
                except_body.append(self.stmt())

            self.eat('END')
            if self.cur().type == 'SEMI': self.eat('SEMI')
            return ('try_except', try_body, except_var, except_body, line)
        if tok.type == 'CLASS':
            return self.class_def()

        node = self.expr()

        if self.cur().type == 'ASSIGN':
            assign_tok = self.eat('ASSIGN')
            rhs = self.expr()
            if self.cur().type == 'SEMI': self.eat('SEMI')

            if node[0] == 'var':
                return ('assign', node[1], rhs, assign_tok.line)
            elif node[0] == 'index_access':
                collection, index = node[1], node[2]
                return ('index_assign', collection, index, rhs, assign_tok.line)
            elif node[0] == 'member_access':
                obj, member = node[1], node[2]
                return ('member_assign', obj, member, rhs, assign_tok.line)
            else:
                raise DarkSyntaxError("Invalid target for assignment", line=assign_tok.line, col=assign_tok.col)
        
        if self.cur().type == 'SEMI': self.eat('SEMI')
        return ('expr', node, line)

    def class_def(self):
        self.eat('CLASS')
        name = self.eat('ID').value
        line = self.cur().line
        base_class_name = None
        if self.cur().type == 'LPAR':
            self.eat('LPAR')
            base_class_name = self.eat('ID').value
            self.eat('RPAR')
        
        self.eat('DO')
        methods = []
        while self.cur().type not in ('END', 'EOF'):
            if self.cur().type == 'SEMI': self.eat('SEMI'); continue
            if self.cur().type != 'FUNCTION':
                raise DarkSyntaxError(f"Only function definitions are allowed inside a class body.", line=self.cur().line, col=self.cur().col)
            methods.append(self.stmt())
        self.eat('END')
        if self.cur().type == 'SEMI': self.eat('SEMI')
        return ('class_def', name, base_class_name, methods, line)

    def expr(self):
        node = self.and_expr()
        while self.cur().type == 'OR':
            op_tok = self.eat('OR')
            node = ('logical_op', 'or', node, self.and_expr(), op_tok.line)
        return node

    def and_expr(self):
        node = self.rel_expr()
        while self.cur().type == 'AND':
            op_tok = self.eat('AND')
            node = ('logical_op', 'and', node, self.rel_expr(), op_tok.line)
        return node

    def rel_expr(self):
        node = self.add_expr()
        while self.cur().type == 'RELOP':
            op_tok = self.eat('RELOP')
            op = op_tok.value
            node = ('binop', op, node, self.add_expr(), op_tok.line)
        return node

    def add_expr(self):
        node = self.mul_expr()
        while self.cur().type == 'OP' and self.cur().value in ('+','-'):
            op_tok = self.eat('OP')
            op = op_tok.value
            node = ('binop', op, node, self.mul_expr(), op_tok.line)
        return node

    def mul_expr(self):
        node = self.primary()
        while self.cur().type == 'OP' and self.cur().value in ('*','/'):
            op_tok = self.eat('OP')
            op = op_tok.value
            node = ('binop', op, node, self.primary(), op_tok.line)
        return node

    def primary(self):
        node = self.factor()
        while self.cur().type in ('DOT', 'LBRACKET', 'LPAR'):
            if self.cur().type == 'DOT':
                dot_tok = self.eat('DOT')
                tok = self.cur()
                member_name = None
                if tok.type == 'ID':
                    member_name = tok.value
                    self.eat('ID')
                elif tok.type.lower() in KEYWORDS:
                    member_name = tok.type.lower()
                    self.eat(tok.type)
                else:
                    raise DarkSyntaxError(f'Expected identifier after dot, but got {tok.type}', line=tok.line, col=tok.col)
                node = ('member_access', node, member_name, dot_tok.line)
            elif self.cur().type == 'LBRACKET':
                lbracket_tok = self.eat('LBRACKET')
                index_expr = self.expr()
                self.eat('RBRACKET')
                node = ('index_access', node, index_expr, lbracket_tok.line)
            elif self.cur().type == 'LPAR':
                lpar_tok = self.eat('LPAR')
                args = []
                if self.cur().type != 'RPAR':
                    args.append(self.expr())
                    while self.cur().type == 'COMMA':
                        self.eat('COMMA')
                        if self.cur().type == 'RPAR': break
                        args.append(self.expr())
                self.eat('RPAR')
                node = ('func_call', node, args, lpar_tok.line)
        return node
    
    def factor(self):
        tok = self.cur()
        if tok.type == 'OP' and tok.value in ('+', '-'):
            op_tok = self.eat('OP')
            op = op_tok.value
            node = self.factor() 
            return ('unary', op, node, op_tok.line)

        if tok.type == 'NOT':
            op_tok = self.eat('NOT')
            node = self.factor()
            return ('unary', 'not', node, op_tok.line)

        if tok.type == 'STRING':
            self.eat('STRING')
            return ('str', tok.value)
        if tok.type == 'TRUE':
            self.eat('TRUE')
            return ('bool', True)
        if tok.type == 'FALSE':
            self.eat('FALSE')
            return ('bool', False)
        if tok.type == 'LBRACKET':
            self.eat('LBRACKET')
            elements = []
            
            while self.cur().type == 'SEMI': self.eat('SEMI')

            if self.cur().type != 'RBRACKET':
                elements.append(self.expr())
                while self.cur().type == 'COMMA':
                    self.eat('COMMA')
                    while self.cur().type == 'SEMI': self.eat('SEMI')
                    if self.cur().type == 'RBRACKET': break
                    elements.append(self.expr())
            
            while self.cur().type == 'SEMI': self.eat('SEMI')

            self.eat('RBRACKET')
            return ('list', elements)
        if tok.type == 'LBRACE':
            self.eat('LBRACE')
            pairs = []

            while self.cur().type == 'SEMI': self.eat('SEMI')

            if self.cur().type != 'RBRACE':
                key = self.expr(); self.eat('COLON'); value = self.expr()
                pairs.append((key, value))
                while self.cur().type == 'COMMA':
                    self.eat('COMMA')
                    while self.cur().type == 'SEMI': self.eat('SEMI')
                    if self.cur().type == 'RBRACE': break
                    key = self.expr(); self.eat('COLON'); value = self.expr()
                    pairs.append((key, value))

            while self.cur().type == 'SEMI': self.eat('SEMI')

            self.eat('RBRACE')
            return ('dict', pairs)
        if tok.type == 'TO_FLOAT':
            self.eat('TO_FLOAT')
            self.eat('LPAR')
            e = self.expr()
            self.eat('RPAR')
            return ('to_float', e)
        if tok.type == 'TO_INT':
            self.eat('TO_INT')
            self.eat('LPAR')
            e = self.expr()
            self.eat('RPAR')
            return ('to_int', e)
        if tok.type == 'TO_STR':
            self.eat('TO_STR')
            self.eat('LPAR')
            e = self.expr()
            self.eat('RPAR')
            return ('to_str', e)
        if tok.type == 'TYPE':
            self.eat('TYPE')
            self.eat('LPAR')
            e = self.expr()
            self.eat('RPAR')
            return ('type', e)
        if tok.type == 'INPUT':
            self.eat('INPUT')
            self.eat('LPAR')
            self.eat('RPAR')
            return ('input',)
        if tok.type == 'NUMBER':
            self.eat('NUMBER')
            return ('num', tok.value)
        if tok.type == 'ID':
            name = self.eat('ID').value
            return ('var', name)
        if tok.type == 'LPAR':
            self.eat('LPAR')
            e = self.expr()
            self.eat('RPAR')
            return e
        raise DarkSyntaxError('Unexpected token in factor', line=tok.line, col=tok.col)

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
        return f"<instance of {self.klass.name}>"

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