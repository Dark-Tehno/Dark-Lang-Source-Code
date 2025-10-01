import os
import sys
import queue
import threading
import itertools
import time
from dark_code.dark_exceptions import DarkRuntimeError

tk = None
ttk = None

class GuiManager:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.event_queue = queue.Queue()
        self.result_queue = queue.Queue()

        self.widgets = {}
        self.next_widget_id = itertools.count(1)
        self.root = None

        self.gui_thread = threading.Thread(target=self._run_gui, daemon=True)
        self.gui_thread.start()

        self.command_handlers = {
            "create_window": self._handle_create_window,
            "create_label": self._handle_create_widget,
            "create_button": self._handle_create_widget,
            "create_entry": self._handle_create_widget,
            "set_text": self._handle_set_text,
            "get_text": self._handle_get_text,
        }

    def _get_widget(self, widget_id):
        """Безопасно получает виджет по ID или корневое окно, если ID=0."""
        if widget_id == 0:
            return self.root
        widget = self.widgets.get(widget_id)
        if not widget:
            raise DarkRuntimeError(f"GUI widget with ID {widget_id} not found.")
        return widget

    def _button_click_handler(self, widget_id):
        """Обработчик клика по кнопке, отправляет асинхронное событие."""
        self.event_queue.put({'type': 'click', 'widget_id': widget_id})

    def _handle_create_window(self, kwargs):
        self.root.title(kwargs.get('title', 'Dark GUI'))
        self.root.geometry(f"{kwargs.get('width', 400)}x{kwargs.get('height', 300)}")
        self.root.deiconify()

    def _handle_create_widget(self, command, kwargs):
        widget_map = {
            'create_label': ttk.Label,
            'create_button': ttk.Button,
            'create_entry': ttk.Entry,
        }
        widget_class = widget_map[command]
        parent = self._get_widget(kwargs['parent_id'])
        widget_id = next(self.next_widget_id)

        if widget_class == ttk.Button:
            widget = widget_class(parent, text=kwargs.get('text', ''), command=lambda w_id=widget_id: self._button_click_handler(w_id))
        else:
            widget = widget_class(parent, text=kwargs.get('text', ''))

        widget.pack(padx=5, pady=5)
        self.widgets[widget_id] = widget
        self.result_queue.put({'request_id': kwargs['request_id'], 'value': widget_id})

    def _handle_set_text(self, kwargs):
        widget = self._get_widget(kwargs['widget_id'])
        text = kwargs.get('text', '')
        if isinstance(widget, (ttk.Label, ttk.Button)):
            widget.config(text=text)
        elif isinstance(widget, ttk.Entry):
            widget.delete(0, tk.END)
            widget.insert(0, text)

    def _handle_get_text(self, kwargs):
        widget = self._get_widget(kwargs['widget_id'])
        text = ''
        if isinstance(widget, ttk.Entry):
            text = widget.get()
        elif isinstance(widget, (ttk.Label, ttk.Button)):
            text = widget.cget("text")
        self.result_queue.put({'request_id': kwargs['request_id'], 'value': text})

    def _handle_stop(self):
        if self.root:
            self.root.quit()


    def _run_gui(self):
        """Эта функция выполняется в фоновом потоке и управляет окном Tkinter."""
        self.root = tk.Tk()
        icon_path_ico = 'assets/icon.ico'
        icon_path_png = 'assets/icon.png'
        try:
            if sys.platform == "win32" and os.path.exists(icon_path_ico):
                self.root.iconbitmap(icon_path_ico)
            elif os.path.exists(icon_path_png):
                photo = tk.PhotoImage(file=icon_path_png)
                self.root.wm_iconphoto(True, photo)
        except tk.TclError:
            print("Warning: Could not load icon 'assets/icon.ico'.")
        self.root.withdraw() 

        def on_closing():
            """Когда пользователь нажимает на крестик, отправляем событие."""
            self.event_queue.put({'type': 'window_close'})

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        def process_queue():
            """Обрабатывает команды из очереди."""
            try:
                while True:
                    command, kwargs = self.command_queue.get_nowait()
                    if command == "stop":
                        self._handle_stop()
                        return

                    handler = self.command_handlers.get(command)
                    if handler:
                        try:
                            if hasattr(handler, '__func__') and handler.__func__ is GuiManager._handle_create_widget:
                                handler(command, kwargs)
                            else:
                                handler(kwargs)
                        except Exception as e:
                            if 'request_id' in kwargs:
                                self.result_queue.put({'request_id': kwargs['request_id'], 'error': str(e)})
                            else:
                                print(f"GUI Error (async): {e}")

            except queue.Empty:
                pass 
            finally:
                if self.root and self.root.winfo_exists():
                    self.root.after(100, process_queue)

        process_queue()
        self.root.mainloop()


    def send_command(self, command, **kwargs):
        """Отправляет команду в GUI-поток без ожидания ответа."""
        self.command_queue.put((command, kwargs))

    def send_command_and_wait(self, command, timeout=5, **kwargs):
        """Отправляет команду и блокируется до получения результата."""
        request_id = f"{command}_{time.monotonic()}"
        kwargs['request_id'] = request_id
        self.command_queue.put((command, kwargs))

        try:
            result = self.result_queue.get(timeout=timeout)

            while result.get('request_id') != request_id:
                self.result_queue.put(result)
                result = self.result_queue.get(timeout=timeout)

            if 'error' in result:
                raise DarkRuntimeError(f"GUI Error: {result['error']}")

            return result.get('value')

        except queue.Empty:
            raise DarkRuntimeError(f"GUI command '{command}' timed out after {timeout} seconds.")

    def check_events(self):
        """Возвращает список всех накопившихся асинхронных событий (клики и т.д.)."""
        events = []
        try:
            while True:
                events.append(self.event_queue.get_nowait())
        except queue.Empty:
            pass
        return events

    def stop(self):
        """Останавливает GUI-поток."""
        if self.gui_thread.is_alive():
            self.send_command("stop")
            self.gui_thread.join(timeout=2)


gui_manager = None

def _get_manager():
    """Получает или создает единственный экземпляр GuiManager."""
    global gui_manager
    if gui_manager is None or not gui_manager.gui_thread.is_alive():
        gui_manager = GuiManager()
    return gui_manager

def _create_widget(widget_type, args):
    if len(args) < 1: raise DarkRuntimeError(f"gui.create_{widget_type}() requires at least a parent_id argument.")
    parent_id = int(args[0])
    text = str(args[1]) if len(args) > 1 else ''
    manager = _get_manager()
    widget_id = manager.send_command_and_wait(f"create_{widget_type}", parent_id=parent_id, text=text)
    return widget_id

def native_gui_create_window(args):
    if len(args) != 3: raise DarkRuntimeError("gui.create_window() requires 3 arguments: title, width, height")
    _get_manager().send_command("create_window", title=str(args[0]), width=int(args[1]), height=int(args[2]))
    return 0

def native_gui_create_label(args): return _create_widget('label', args)
def native_gui_create_button(args): return _create_widget('button', args)
def native_gui_create_entry(args): return _create_widget('entry', args)

def native_gui_set_text(args):
    if len(args) != 2: raise DarkRuntimeError("gui.set_text() requires 2 arguments: widget_id, text")
    _get_manager().send_command("set_text", widget_id=int(args[0]), text=str(args[1]))
    return None

def native_gui_get_text(args):
    if len(args) != 1: raise DarkRuntimeError("gui.get_text() requires 1 argument: widget_id")
    widget_id = int(args[0])
    manager = _get_manager()
    return manager.send_command_and_wait("get_text", widget_id=widget_id)

def native_gui_check_events(args):
    if args: raise DarkRuntimeError("gui.check_events() takes no arguments.")
    return _get_manager().check_events()

def native_gui_stop(args):
    if args: raise DarkRuntimeError("gui.stop() takes no arguments.")
    manager = _get_manager()
    if manager:
        manager.stop()
    global gui_manager
    gui_manager = None
    return None

def get_module(use_tkinter=True):
    global tk, ttk

    if not use_tkinter:
        return {'error': lambda args: "Модуль gui отключен директивой #!notkinter"}

    if tk is not None:
        return {
            'create_window': native_gui_create_window, 'create_label': native_gui_create_label,
            'create_button': native_gui_create_button, 'create_entry': native_gui_create_entry,
            'set_text': native_gui_set_text, 'get_text': native_gui_get_text,
            'check_events': native_gui_check_events, 'stop': native_gui_stop,
        }

    try:
        import tkinter
        from tkinter import ttk as t
        tk = tkinter
        ttk = t
    except ModuleNotFoundError:
        print("""Для стабильной работы на Linux(Debian, Ubuntu, Mint) необходимо выполнить `sudo apt-get install python3-tk` 
или для Fedora, CentOS, RHEL - `sudo dnf install python3-tkinter`
или для Arch Linux, Manjaro - `sudo pacman -S tk`""", file=sys.stderr)
        return {'error': lambda args: "Модуль tkinter не найден. Установите его для вашей ОС."}

    return {
        'create_window': native_gui_create_window, 'create_label': native_gui_create_label,
        'create_button': native_gui_create_button, 'create_entry': native_gui_create_entry,
        'set_text': native_gui_set_text, 'get_text': native_gui_get_text,
        'check_events': native_gui_check_events, 'stop': native_gui_stop,
    }
