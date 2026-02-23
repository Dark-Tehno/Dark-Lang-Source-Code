import math
import random


proc dark_sqrt*(x: float): float =
    return math.sqrt(x)

proc dark_pow*(x: float, y: float): float =
    return math.pow(x, y)

proc dark_floor*(x: float): float =
    return math.floor(x)

proc dark_ceil*(x: float): float =
    return math.ceil(x)

proc dark_pi*(): float =
    return math.PI

proc dark_random*(a: int, b: int): int =
    random.randomize()
    return random.rand(a..b)