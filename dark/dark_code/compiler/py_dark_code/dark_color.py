def red(text):
    return '\033[91m' + text + '\033[0m'
def green(text):
    return '\033[92m' + text + '\033[0m'
def blue(text):
    return '\033[94m' + text + '\033[0m'
def yellow(text):
    return '\033[93m' + text + '\033[0m'
def cyan(text):
    return '\033[96m' + text + '\033[0m'
def magenta(text):
    return '\033[95m' + text + '\033[0m'
def white(text):
    return '\033[97m' + text + '\033[0m'
def black(text):
    return '\033[30m' + text + '\033[0m'
def orange(text):
    return '\033[38;5;208m' + text + '\033[0m'
def purple(text):
    return '\033[38;5;93m' + text + '\033[0m'
def pink(text):
    return '\033[38;5;206m' + text + '\033[0m'
def brown(text):
    return '\033[38;5;94m' + text + '\033[0m'
def gray(text):
    return '\033[90m' + text + '\033[0m'
def light_gray(text):
    return '\033[37m' + text + '\033[0m'
def dark_gray(text):
    return '\033[38;5;240m' + text + '\033[0m'
def light_blue(text):
    return '\033[38;5;111m' + text + '\033[0m'
def light_green(text):
    return '\033[38;5;151m' + text + '\033[0m'
def light_cyan(text):
    return '\033[38;5;159m' + text + '\033[0m'
def light_red(text):
    return '\033[38;5;204m' + text + '\033[0m'
def light_magenta(text):
    return '\033[38;5;201m' + text + '\033[0m'
def dark_red(text):
    return '\033[38;5;88m' + text + '\033[0m'
def dark_green(text):
    return '\033[38;5;22m' + text + '\033[0m'
def dark_blue(text):
    return '\033[38;5;20m' + text + '\033[0m'
def dark_yellow(text):
    return '\033[38;5;178m' + text + '\033[0m'
def dark_cyan(text):
    return '\033[38;5;30m' + text + '\033[0m'
def dark_magenta(text):
    return '\033[38;5;53m' + text + '\033[0m'
def dark_white(text):
    return '\033[97m' + text + '\033[0m'
def dark_black(text):
    return '\033[30m' + text + '\033[0m'
def dark_orange(text):
    return '\033[38;5;208m' + text + '\033[0m'
def dark_purple(text):
    return '\033[38;5;93m' + text + '\033[0m'
def dark_pink(text):
    return '\033[38;5;213m' + text + '\033[0m'
def dark_brown(text):
    return '\033[38;5;94m' + text + '\033[0m'


def rgb_color(r, g, b, text):
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise TypeError("Компоненты RGB должны быть целыми числами")
    if not isinstance(text, str):
        raise TypeError("Текстовый аргумент должен быть строкой")
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
        raise TypeError("Компоненты RGB должны быть целыми числами от 0 до 255")
    if not isinstance(text, str):
        raise TypeError("Текстовый аргумент должен быть строкой")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def rgba_color(r, g, b, a, text):
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
        raise TypeError("Компоненты RGB должны быть целыми числами от 0 до 255")
    if not isinstance(a, (int, float)) or not (0 <= a <= 1):
        raise TypeError("Альфа-компонент должен быть числом от 0 до 1")
    if not isinstance(text, str):
        raise TypeError("Текстовый аргумент должен быть строкой")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def hex_color(hex_code, text):
    if not isinstance(hex_code, str):
        raise TypeError("Шестнадцатеричный код должен быть строкой")
    if not isinstance(text, str):
        raise TypeError("Текстовый аргумент должен быть строкой")
    
    hex_code = hex_code.lstrip('#')
    if hex_code.lower().startswith('0x'):
        hex_code = hex_code[2:]

    if len(hex_code) == 3:
        hex_code = ''.join([c*2 for c in hex_code])
    if len(hex_code) != 6:
        raise RuntimeError("Неверный формат hex кода. Ожидаемые 3 или 6 символов..")
    
    try:
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
    except ValueError:
        raise RuntimeError("Недопустимое значение hex кода.")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def hsl_color(h, s, l, text):
    if not all(isinstance(c, (int, float)) for c in [h, s, l]):
        raise TypeError("Компоненты HSL должны быть пронумерованы")
    if not isinstance(text, str):
        raise TypeError("Текстовый аргумент должен быть строкой")
    
    if not (0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100):
        raise RuntimeError("Значения HSL вне диапазона: h (0-360), s (0-100), l (0-100)")

    s /= 100
    l /= 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    
    r, g, b = 0, 0, 0
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x

    r = round((r + m) * 255)
    g = round((g + m) * 255)
    b = round((b + m) * 255)

    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"