from dark_code.dark_exceptions import DarkRuntimeError


def color(args, color_name):
    if len(args) >= 1: 
        text = args[0]
    else:
        text = ""
    COLOR_CODES = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'white': '\033[97m',
        'black': '\033[30m',
        'orange': '\033[38;5;208m',
        'purple': '\033[38;5;93m',
        'pink': '\033[38;5;206m',
        'brown': '\033[38;5;94m',
        'gray': '\033[90m',
        'light_gray': '\033[37m',
        'dark_gray': '\033[38;5;240m',
        'light_blue': '\033[38;5;111m',
        'light_green': '\033[38;5;151m',
        'light_cyan': '\033[38;5;159m',
        'light_red': '\033[38;5;204m',
        'light_magenta': '\033[38;5;201m',
        'dark_red': '\033[38;5;88m',
        'dark_green': '\033[38;5;22m',
        'dark_blue': '\033[38;5;20m',
        'dark_yellow': '\033[38;5;178m',
        'dark_cyan': '\033[38;5;30m',
        'dark_magenta': '\033[38;5;53m',
    }
    RESET_CODE = '\033[0m'
    
    if color_name in COLOR_CODES:
        return COLOR_CODES[color_name] + text + RESET_CODE
    else:
        raise DarkRuntimeError(f"Unsupported color: {color_name}")

def rgb_color(args):
    if len(args) != 4: raise TypeError("rgb() takes 3 arguments (r, g, b, text)")
    r, g, b, text = args
    if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
        raise TypeError("RGB components must be integers")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
        raise TypeError("RGB components must be integers between 0 and 255")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def rgba_color(args):
    if len(args) != 5: raise TypeError("rgba() takes 4 arguments (r, g, b, a, text)")
    r, g, b, a, text = args
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in [r, g, b]):
        raise TypeError("RGB components must be integers between 0 and 255")
    if not isinstance(a, (int, float)) or not (0 <= a <= 1):
        raise TypeError("Alpha component must be a number between 0 and 1")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def hex_color(args):
    if len(args) != 2: raise TypeError("hex() takes 2 arguments (hex_code, text)")
    hex_code, text = args
    if not isinstance(hex_code, str):
        raise TypeError("Hex code must be a string")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    hex_code = hex_code.lstrip('#')
    if hex_code.lower().startswith('0x'):
        hex_code = hex_code[2:]

    if len(hex_code) == 3:
        hex_code = ''.join([c*2 for c in hex_code])
    if len(hex_code) != 6:
        raise DarkRuntimeError("Invalid hex code format. Expected 3 or 6 characters.")
    
    try:
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
    except ValueError:
        raise DarkRuntimeError("Invalid hex code value.")
    
    return f"\033[38;2;{r};{g};{b}m" + text + "\033[0m"

def hsl_color(args):
    if len(args) != 4: raise TypeError("hsl() takes 3 arguments (h, s, l, text)")
    h, s, l, text = args
    if not all(isinstance(c, (int, float)) for c in [h, s, l]):
        raise TypeError("HSL components must be numbers")
    if not isinstance(text, str):
        raise TypeError("Text argument must be a string")
    
    if not (0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100):
        raise DarkRuntimeError("HSL values out of range: h (0-360), s (0-100), l (0-100)")

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