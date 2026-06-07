import sys
import time as python_time


def time():
    """Возвращает текущее время в секундах с момента начала эпохи."""
    return python_time.time()

def sleep(seconds):
    """Переходит в спящий режим на определенное количество секунд."""
    if not isinstance(seconds, (int, float)):
        raise TypeError("Аргументом для функции time.sleep() должно быть число")
    sys.stdout.flush()
    python_time.sleep(seconds)
    return None