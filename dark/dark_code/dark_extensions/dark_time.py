import sys
import time as python_time


def native_time_time(args):
    """Returns the current time in seconds since the Epoch."""
    if args: raise TypeError("time.time() takes no arguments")
    return python_time.time()

def native_time_sleep(args):
    """Sleeps for a specified number of seconds."""
    if len(args) != 1: raise TypeError("time.sleep() takes 1 argument (seconds)")
    seconds = args[0]
    if not isinstance(seconds, (int, float)):
        raise TypeError("Argument for time.sleep() must be a number")
    sys.stdout.flush()
    python_time.sleep(seconds)
    return None