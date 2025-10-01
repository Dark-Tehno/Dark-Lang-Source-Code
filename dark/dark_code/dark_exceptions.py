import os

class DarkError(Exception):
    """Base exception class for dark language errors."""
    def __init__(self, message, line=None, col=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col
        self.filename = None 
        self.traceback = []

    @property
    def column(self):
        return self.col
    
    def add_trace(self, filename, line, context_name):
        """Добавляет новый фрейм в начало трассировки стека."""
        if not self.traceback or self.traceback[0] != (filename, line, context_name):
            self.traceback.insert(0, (filename, line, context_name))

    def __str__(self):
        error_type = self.__class__.__name__.replace("Dark", "")
        if error_type == "SyntaxError":
            error_type = "Синтаксическая ошибка"
        elif error_type == "RuntimeError":
            error_type = "Ошибка выполнения"

        C_ERROR = '\033[91m'
        C_FILE = '\033[96m' 
        C_LINE = '\033[93m' 
        C_CONTEXT = '\033[92m'
        C_RESET = '\033[0m'

        traceback_str = ""
        if self.traceback:
            traceback_str = "Трассировка вызовов (от последнего к первому):\n"
            for file, line, context in self.traceback:
                traceback_str += f'  Файл "{C_FILE}{os.path.abspath(file)}{C_RESET}", строка {C_LINE}{line}{C_RESET}, в {C_CONTEXT}{context}{C_RESET}\n'
            traceback_str += "\n"

        loc_parts = []
        if self.filename:
            loc_parts.append(f'Файл: "{C_FILE}{os.path.abspath(self.filename)}{C_RESET}"')
        if self.line:
            loc_parts.append(f"строка {C_LINE}{self.line}{C_RESET}")
        if self.col:
            loc_parts.append(f"позиция {C_LINE}{self.col}{C_RESET}")
        
        loc_info = f"  [{', '.join(loc_parts)}]" if loc_parts else ""

        code_context = ""
        if self.filename and self.line and os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if 0 < self.line <= len(lines):
                    line_content = lines[self.line - 1].rstrip().replace('\t', '    ')
                    line_num_str = f"{C_LINE}{self.line}{C_RESET}"
                    code_context = f"\n\n  {line_num_str} | {line_content}"
                    if self.col:
                        padding = len(str(self.line)) + 3
                        pointer_padding = ' ' * (self.col - 1)
                        code_context += f"\n  {' ' * padding}{C_ERROR}{pointer_padding}^{C_RESET}"
                        terminal_width = os.get_terminal_size().columns
                        code_context += f'\n{"-" * terminal_width}'
            except (IOError, UnicodeDecodeError):
                pass

        return f"{traceback_str}{C_ERROR}{error_type}{C_RESET}: {self.message}\n{loc_info}{code_context}"

class DarkSyntaxError(DarkError): pass
class DarkRuntimeError(DarkError): pass