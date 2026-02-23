import strutils, tables, math
from ../dark/exceptions import DarkRuntimeError, formatError

proc dark_color*(text: string, color_name: string): string =
  const COLOR_CODES = {
    "red": "\x1b[91m",
    "green": "\x1b[92m",
    "blue": "\x1b[94m",
    "yellow": "\x1b[93m",
    "cyan": "\x1b[96m",
    "magenta": "\x1b[95m",
    "white": "\x1b[97m",
    "black": "\x1b[30m",
    "orange": "\x1b[38;5;208m",
    "purple": "\x1b[38;5;93m",
    "pink": "\x1b[38;5;206m",
    "brown": "\x1b[38;5;94m",
    "gray": "\x1b[90m",
    "light_gray": "\x1b[37m",
    "dark_gray": "\x1b[38;5;240m",
    "light_blue": "\x1b[38;5;111m",
    "light_green": "\x1b[38;5;151m",
    "light_cyan": "\x1b[38;5;159m",
    "light_red": "\x1b[38;5;204m",
    "light_magenta": "\x1b[38;5;201m",
    "dark_red": "\x1b[38;5;88m",
    "dark_green": "\x1b[38;5;22m",
    "dark_blue": "\x1b[38;5;20m",
    "dark_yellow": "\x1b[38;5;178m",
    "dark_cyan": "\x1b[38;5;30m",
    "dark_magenta": "\x1b[38;5;53m",
    "dark_white": "\x1b[97m",
    "dark_black": "\x1b[30m",
    "dark_orange": "\x1b[38;5;208m",
    "dark_purple": "\x1b[38;5;93m",
    "dark_pink": "\x1b[38;5;213m",
    "dark_brown": "\x1b[38;5;94m",
  }.toTable()
  const RESET_CODE = "\x1b[0m"
  let lowerColor = color_name.toLowerAscii()
  if lowerColor in COLOR_CODES:
    return COLOR_CODES[lowerColor] & text & RESET_CODE
  else:
    var message = "в модуле 'color' не найден член '" & color_name & "'"
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    quit()

proc rgb_color*(r: int, g: int, b: int, text: string): string =
  if not (0 <= r and r <= 255 and 0 <= g and g <= 255 and 0 <= b and b <= 255):
    var message = "Компоненты RGB должны быть целыми числами от 0 до 255"
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    quit()
    
  return "\x1b[38;2;" & $r & ";" & $g & ";" & $b & "m" & text & "\x1b[0m"

proc rgba_color*(r: int, g: int, b: int, a: float, text: string): string =
  if not (0 <= r and r <= 255 and 0 <= g and g <= 255 and 0 <= b and b <= 255):
    var message = "Компоненты RGB должны быть целыми числами от 0 до 255"
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    quit()
  if not (0.0 <= a and a <= 1.0):
    var message = "Альфа-компонент должен быть числом от 0 до 1"
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    quit()
  
  return "\x1b[38;2;" & $r & ";" & $g & ";" & $b & "m" & text & "\x1b[0m"

proc hex_color*(hex_code: string, text: string): string =
  var cleaned_hex_code = hex_code.strip(chars={'#'})
  if cleaned_hex_code.toLowerAscii().startsWith("0x"):
    cleaned_hex_code = cleaned_hex_code[2..^1]

  if cleaned_hex_code.len == 3:
    var expanded = ""
    for c in cleaned_hex_code:
      expanded &= repeat(c, 2)
    cleaned_hex_code = expanded

  if cleaned_hex_code.len != 6:
    var message = "Неверный формат hex кода. Ожидаемые 3 или 6 символов."
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    quit()

  try:
    let r = parseHexInt(cleaned_hex_code[0..1])
    let g = parseHexInt(cleaned_hex_code[2..3])
    let b = parseHexInt(cleaned_hex_code[4..5])
    return "\x1b[38;2;" & $r & ";" & $g & ";" & $b & "m" & text & "\x1b[0m"
  except ValueError:
    var message = "Недопустимое значение hex кода."
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    quit()

proc hsl_color*(h: int, s: int, l: int, text: string): string =
  if not (0 <= h and h <= 360 and 0 <= s and s <= 100 and 0 <= l and l <= 100):
    var message = "Значения HSL вне диапазона: h (0-360), s (0-100), l (0-100)"
    var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
    echo formatError(err, "DarkRuntimeError")
    quit()

  let s_float = s.float / 100.0
  let l_float = l.float / 100.0

  let c = (1.0 - abs(2.0 * l_float - 1.0)) * s_float
  let temp = h.float / 60.0
  let mod_val = temp - (float(temp.int div 2) * 2.0)
  let x = c * (1.0 - abs(mod_val - 1.0))
  let m = l_float - c / 2.0

  var r_float, g_float, b_float: float

  if 0 <= h and h < 60:
    r_float = c
    g_float = x
    b_float = 0.0
  elif 60 <= h and h < 120:
    r_float = x
    g_float = c
    b_float = 0.0
  elif 120 <= h and h < 180:
    r_float = 0.0
    g_float = c
    b_float = x
  elif 180 <= h and h < 240:
    r_float = 0.0
    g_float = x
    b_float = c
  elif 240 <= h and h < 300:
    r_float = x
    g_float = 0.0
    b_float = c
  elif 300 <= h and h < 360:
    r_float = c
    g_float = 0.0
    b_float = x

  let r = ((r_float + m) * 255.0 + 0.5).int
  let g = ((g_float + m) * 255.0 + 0.5).int
  let b = ((b_float + m) * 255.0 + 0.5).int

  return "\x1b[38;2;" & $r & ";" & $g & ";" & $b & "m" & text & "\x1b[0m"

echo hsl_color(120, 100, 50, "Привет, HSL!")