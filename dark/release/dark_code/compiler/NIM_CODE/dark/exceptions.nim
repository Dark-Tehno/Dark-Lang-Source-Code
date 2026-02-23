import strutils, tables

proc translateSyntaxErrorMessage(message: string): string =
  const TOKEN_TRANSLATIONS = {
    "RPAR": "')'",
    "LPAR": "'('",
    "RBRACKET": "']'",
    "LBRACKET": "'['",
    "RBRACE": "'}'",
    "LBRACE": "'{'",
    "SEMI": "';' или новая строка",
    "COMMA": "','",
    "ASSIGN": "'='",
    "ID": "идентификатор (имя переменной)",
    "NUMBER": "число",
    "STRING": "строка",
    "EOF": "конец файла",
    "COLON": "':'",
    "DOT": "'.'",
    "THEN": "ключевое слово 'then'",
    "DO": "ключевое слово 'do'",
    "END": "ключевое слово 'end'",
    "IN": "ключевое слово 'in'",
    "RELOP": "оператор сравнения (==, !=, <, > и т.д.)",
    "OP": "арифметический оператор (+, -, *, /)",
  }.toTable()

  const MESSAGE_TEMPLATES = {
    "Invalid target for assignment": "недопустимая цель для присваивания. Присваивать значения можно только переменным, элементам списка или словаря.",
    "Unexpected token in factor": "неожиданный синтаксис. Возможно, вы пропустили оператор или использовали неверный символ.",
  }.toTable()

  if message in MESSAGE_TEMPLATES:
    return MESSAGE_TEMPLATES[message]

  let parts = message.split(", got ")
  if parts.len == 2 and parts[0].startsWith("Expected "):
    let expected = parts[0][9..^1]
    let got = parts[1]
    let expectedStr = TOKEN_TRANSLATIONS.getOrDefault(expected, expected)
    let gotStr = TOKEN_TRANSLATIONS.getOrDefault(got, "'" & got & "'")
    return "Ожидаемый токен " & expectedStr & ", получен " & gotStr

  var translatedMessage = message
  for token, translation in TOKEN_TRANSLATIONS:
    translatedMessage = translatedMessage.replace(token, translation)

  return translatedMessage

type DarkError* = object of CatchableError
  message*: string
  line*, col*: int
  filename*: string

proc newDarkError*(message: string, line: int = 0, col: int = 0, filename: string = ""): DarkError =
  result = DarkError(message: message, line: line, col: col, filename: filename)

proc formatError*(err: DarkError, errorType: string="DarkError"): string =
  var translatedType = errorType
  if translatedType == "DarkSyntaxError":
    translatedType = "Синтаксическая ошибка"
  elif translatedType == "DarkRuntimeError":
    translatedType = "Ошибка выполнения"
  elif translatedType == "DarkWetherError":
    translatedType = "Ошибка модуля Wether"
  elif translatedType == "DarkError":
    translatedType = "Ошибка"

  const C_ERROR = "\x1b[91m"
  const C_RESET = "\x1b[0m"

  return C_ERROR & translatedType & C_RESET & ": " & translateSyntaxErrorMessage(err.message)

type DarkSyntaxError* = object of DarkError
type DarkRuntimeError* = object of DarkError