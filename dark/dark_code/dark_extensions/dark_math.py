# Copyright 2026 Dark.Tehno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import math as python_math
import random as python_random


def native_math_sqrt(args):
    """Вычисляет квадратный корень из числа."""
    if len(args) != 1: raise TypeError("math.sqrt() принимает 1 аргумент")
    return python_math.sqrt(args[0])

def native_math_pow(args):
    """Вычисляет базовую величину в степени exp."""
    if len(args) != 2: raise TypeError("math.pow() привнимает 2 аргумента")
    return python_math.pow(args[0], args[1])

def native_math_floor(args):
    """Возвращает пол номера."""
    if len(args) != 1: raise TypeError("math.floor() принимает 1 аргумент")
    return python_math.floor(args[0])

def native_math_ceil(args):
    """Возвращает максимальное значение числа."""
    if len(args) != 1: raise TypeError("math.ceil() принимает 1 аргумент")
    return python_math.ceil(args[0])

def native_math_pi(args):
    """Возвращает значение числа PI."""
    if args: raise TypeError("math.pi() не принимает аргументы")
    return python_math.pi

def native_math_random(args):
    """Возвращает случайное значение с плавающей точкой в диапазоне от a до b."""
    if len(args) != 2: raise TypeError("math.random() привнимает 2 аргумента")
    a = args[0]
    b = args[1]
    return python_random.randint(a, b)