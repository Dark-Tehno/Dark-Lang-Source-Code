import math as python_math
import random as python_random


def sqrt(x):
    """Вычисляет квадратный корень из числа."""
    return python_math.sqrt(x)

def pow(x, y):
    """Вычисляет базовую величину в степени exp."""
    return python_math.pow(x, y)

def floor(x):
    """Возвращает пол номера."""
    return python_math.floor(x)

def ceil(x):
    """Возвращает максимальное значение числа."""
    return python_math.ceil(x)

def pi():
    """Возвращает значение числа PI."""
    return python_math.pi

def random(a, b):
    """Возвращает случайное значение с плавающей точкой в диапазоне от a до b."""
    return python_random.randint(a, b)

def randint(a, b):
    """Возвращает случайное целое число в диапазоне от a до b."""
    return python_random.randint(a, b)