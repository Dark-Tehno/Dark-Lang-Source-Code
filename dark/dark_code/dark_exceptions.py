# 0.3.1:
import os

class DarkError(Exception):
    """Base exception class for dark language errors."""
    def __init__(self, message, line=None, col=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col
        self.filename = None 

    @property
    def column(self):
        return self.col

    def __str__(self):
        error_type = self.__class__.__name__.replace("Dark", "")
        if error_type == "SyntaxError":
            error_type = "Синтаксическая ошибка"
        elif error_type == "RuntimeError":
            error_type = "Ошибка выполнения"

        loc_parts = []
        if self.filename:
            loc_parts.append(f"Файл: \"{os.path.abspath(self.filename)}\"")
        if self.line:
            loc_parts.append(f"строка {self.line}")
        if self.col:
            loc_parts.append(f"позиция {self.col}")
        
        loc_info = f"  [{', '.join(loc_parts)}]" if loc_parts else ""

        code_context = ""
        if self.filename and self.line and os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if 0 < self.line <= len(lines):
                    line_content = lines[self.line - 1].rstrip()
                    code_context = f"\n\n  {self.line} | {line_content}"
                    if self.col:
                        padding = len(str(self.line)) + 3 
                        code_context += f"\n  {' ' * padding}{' ' * (self.col - 1)}^"
                        terminal_width = os.get_terminal_size().columns
                        code_context += f'\n{"-" * terminal_width}'
            except (IOError, UnicodeDecodeError):
                pass

        return f"{error_type}: {self.message}\n{loc_info}{code_context}"

class DarkSyntaxError(DarkError): pass
class DarkRuntimeError(DarkError): pass