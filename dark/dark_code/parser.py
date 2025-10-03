from dark_code.dark_exceptions import DarkSyntaxError
from dark_code.lexer import KEYWORDS

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