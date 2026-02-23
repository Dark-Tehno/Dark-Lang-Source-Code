import std/times
import std/os

proc dark_time*(): float =
    return times.epochTime()

proc dark_sleep*(seconds: float) =
  os.sleep(int(seconds * 1000))
