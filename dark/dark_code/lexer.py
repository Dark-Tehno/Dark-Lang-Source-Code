import re


class Token:
    def __init__(self, t, v=None, line=None, col=None):
        self.type = t
        self.value = v
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type},{repr(self.value)},{self.line},{self.col})"

    @property
    def type_name(self):
        return self.type


TOKEN_SPEC = [
    ('NUMBER',  r'(\d+(_\d+)*(\.\d+(_\d+)*)?|\.\d+(_\d+)*)([eE][+-]?\d+(_\d+)*)?'),
    ('ID',      r'[^\W\d]\w*'),
    ('STRING',  r'"""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'|`(?:.|\n)*?`|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\\\'])*\''),
    ('COMMENT', r'#.*|<!--(?:.|\n)*?-->'),
    ('RELOP',   r'==|!=|<>|<=|>=|<|>'),
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
    ('MISMATCH', r'.'),
]

KEYWORDS = {'print', 'println', 'assert', 'enumerate', 'if', 'then', 'end', 'while', 'do', 'input', 'to_int', 'to_str', 'type', 'else', 'import', 'true', 'false', 'function', 'return', 'for', 'in', 'to_float', 'try', 'except', 'and', 'or', 'not', 'class', 'use', 'from'}

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
            have_underscore = '_' in val
            if have_underscore:
                val = val.replace('_', '')
            val_to_store = float(val) if is_float else int(val)
            tokens.append(Token('NUMBER', val_to_store, line_num, col))
        elif kind == 'ID':
            if val in KEYWORDS:
                tokens.append(Token(val.upper(), line=line_num, col=col))
            else:
                tokens.append(Token('ID', val, line_num, col))
        elif kind == 'STRING':
            token_line_num = line_num
            quote_type = None
            if val.startswith('"""') or val.startswith("'''") or val.startswith('`'):
                if val.startswith('"""') or val.startswith("'''"):
                    quote_type = val[:3]
                    str_val = val[3:-3]
                else:
                    quote_type = '`'
                    str_val = val[1:-1]
                num_newlines = val.count('\n')
                if num_newlines > 0:
                    line_num += num_newlines
                    line_start = m.start() + val.rfind('\n') + 1
            else:
                quote_type = val[0]
                str_val = val[1:-1]

            processed_val = str_val.encode('raw_unicode_escape').decode('unicode_escape')
            tokens.append(Token('STRING', (processed_val, quote_type), token_line_num, col))
        elif kind == 'RELOP':
            tokens.append(Token('RELOP', val, line_num, col))
        elif kind == 'OP':
            tokens.append(Token('OP', val, line_num, col))
        elif kind in ('ASSIGN', 'LPAR', 'RPAR', 'SEMI', 'DOT', 'COMMA', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'COLON'):
            tokens.append(Token(kind, val, line_num, col))
        elif kind == 'NEWLINE':
            tokens.append(Token('SEMI', line=line_num, col=col))
            line_num += 1
            line_start = pos
        elif kind == 'SKIP' or kind == 'COMMENT':
            continue
        elif kind == 'MISMATCH':
            tokens.append(Token('ERROR', f'Неожиданная точка: {val!r}', line_num, col))
            continue
    tokens.append(Token('EOF', line=line_num, col=1))
    return tokens