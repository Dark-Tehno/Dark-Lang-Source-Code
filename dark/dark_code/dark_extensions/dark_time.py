import sys
import time as python_time


def native_time_time(args):
    """Returns the current time in seconds since the Epoch."""
    if args: raise TypeError("Функция time.time() не принимает аргументов")
    return python_time.time()

def native_time_sleep(args):
    """Sleeps for a specified number of seconds."""
    if len(args) != 1: raise TypeError("time.sleep() принимает 1 аргумент (секунды)")
    seconds = args[0]
    if not isinstance(seconds, (int, float)):
        raise TypeError("Аргументом для функции time.sleep() должно быть число")
    sys.stdout.flush()
    python_time.sleep(seconds)
    return None