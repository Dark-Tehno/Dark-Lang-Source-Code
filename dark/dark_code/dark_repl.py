from dark_code.dark_lang import Parser, lex, run, DarkRuntimeError
from dark_code import data


class DarkREPL:
    def __init__(self, dark_root_dir, denv_path=None):
        self.env = {}
        self.dark_root_dir = dark_root_dir
        self.denv_path = denv_path
        self.modules = {}
        self.current_code_buffer = []

    def start(self):
        """Запускает основной цикл REPL."""
        print("Dark REPL (Read-Eval-Print Loop)")
        print("Введите 'exit()' или 'quit()' для выхода.")
        print("Введите 'help()' для получения справки.")
        print(f"Версия Dark: {data.__version__}")

        while True:
            try:
                prompt = '... ' if self.current_code_buffer else '>>> '
                line = input(prompt)

                if line.strip() in ('exit()', 'quit()'):
                    break
                if line.strip() == 'help()':
                    self.show_help()
                    continue

                self.current_code_buffer.append(line)
                code = "\n".join(self.current_code_buffer)

                if self.is_block_incomplete(code):
                    continue

                self.execute_code(code)
                self.current_code_buffer = []

            except (KeyboardInterrupt, EOFError):
                print('Используйте quit() или exit() для выхода из REPL.')
            except Exception as e:
                print(f"Неожиданная ошибка в REPL: {e}")
                self.current_code_buffer = []

    def is_block_incomplete(self, code):
        """Проверяет, является ли блок кода (например, if, function) незавершенным."""
        block_starters = code.count(' do') + code.count(' then') + code.count('{')
        block_enders = code.count('end') + code.count('}')
        if block_starters > block_enders:
            return True
        if code.strip().endswith(('do', 'then', ',', '(', '[', '=', '+', '-', '*', '/', 'and', 'or')):
            return True
        
        return False

    def execute_code(self, code):
        """Выполняет фрагмент кода Dark."""
        try:
            tokens = lex(code)
            parser = Parser(tokens)
            ast = parser.parse()

            if parser.errors:
                for error in parser.errors:
                    print(f"Синтаксическая ошибка: {error.message} (строка {error.line})")
                return

            result = run(ast, env=self.env, source_name='<repl>', modules=self.modules,
                         dark_root_dir=self.dark_root_dir, denv_path=self.denv_path)

            if result is not None:
                print(repr(result))

        except DarkRuntimeError as e:
            print(f"Ошибка выполнения: {e.message}")

    def show_help(self):
        """Отображает справочную информацию."""
        print("\n--- Справка Dark REPL ---")
        print("  exit() или quit() - выход из REPL.")
        print("  help()            - показать это сообщение.")
        print("Вы можете вводить любой код на языке Dark.")
        print("Многострочные блоки, такие как 'if...end' или 'function...end', поддерживаются.")
        print("-------------------------\n")
