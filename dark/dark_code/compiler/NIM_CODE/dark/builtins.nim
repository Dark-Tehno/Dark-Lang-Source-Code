import strutils, typetraits
from ./exceptions import DarkSyntaxError, formatError


proc print*(args: varargs[string, `$`]) =
    for arg in args:
        write(stdout, arg & " ")

proc println*(args: varargs[string, `$`]) =
    for arg in args:
        write(stdout, arg & " ")
    write(stdout, "\n")

proc input*(): string = 
    return readLine(stdin)

proc to_int*(str: string): int =

    try:
        return parseInt(str)
    except ValueError:
        var message = "Не удается преобразовать значение в int"
        var err: DarkSyntaxError = DarkSyntaxError(message: message, line: 0, col: 0, filename: "<script>")
        echo formatError(err, "DarkSyntaxError")
        quit()

proc to_float*(str: string): float =
    try:
        return parseFloat(str)
    except ValueError:
        var message = "Не удается преобразовать значение в float"
        var err: DarkSyntaxError = DarkSyntaxError(message: message, line: 0, col: 0, filename: "<script>")
        echo formatError(err, "DarkSyntaxError")
        quit()

proc to_str*(data: auto): string = 
    return $(data)

proc dark_type*(data: auto): string =
  let type_of = name(typeof(data))
  case type_of
  of "string": "str"
  of "int": "int"
  of "bool": "bool"
  else:
    if type_of.startsWith("float"): "float"
    elif type_of.startsWith("seq"): "list"
    elif type_of.startsWith("Table"): "dict"
    else: type_of