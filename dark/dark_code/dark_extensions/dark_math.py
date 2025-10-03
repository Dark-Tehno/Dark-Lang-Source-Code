import math as python_math
import random as python_random


def native_math_sqrt(args):
    """Calculates the square root of a number."""
    if len(args) != 1: raise TypeError("math.sqrt() takes 1 argument")
    return python_math.sqrt(args[0])

def native_math_pow(args):
    """Calculates base to the power of exp."""
    if len(args) != 2: raise TypeError("math.pow() takes 2 arguments")
    return python_math.pow(args[0], args[1])

def native_math_floor(args):
    """Returns the floor of a number."""
    if len(args) != 1: raise TypeError("math.floor() takes 1 argument")
    return python_math.floor(args[0])

def native_math_ceil(args):
    """Returns the ceiling of a number."""
    if len(args) != 1: raise TypeError("math.ceil() takes 1 argument")
    return python_math.ceil(args[0])

def native_math_pi(args):
    """Returns the value of PI."""
    if args: raise TypeError("math.pi() takes no arguments")
    return python_math.pi

def native_math_random(args):
    """Returns a random float between 0.0 and 1.0."""
    if args: raise TypeError("math.random() takes no arguments")
    return python_random.random()