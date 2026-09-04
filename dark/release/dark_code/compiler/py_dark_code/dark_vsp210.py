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
import os
import time
import webbrowser


def version():
    """Возвращает версию языка Dark."""
    try:
        from dark_code.data import __version__
        return __version__
    except Exception:
        return "1.3.0"


def docs():
    """Открывает документацию по языку Dark."""
    webbrowser.open("https://vsp210.ru/dark-lang/")
    return "Докментация по языку Dark"


def telegram():
    """Открывает Telegram-канал создателя языка Dark."""
    webbrowser.open("https://t.me/vsp210_official/")
    return "Телеграм канал создателя языка Dark"


def _unsupported_in_compiled_build(feature_name):
    raise RuntimeError(
        f"vsp210.{feature_name}() недоступен в скомпилированной сборке: "
        f"эта функция запускает внутренний .dark-скрипт через полный интерпретатор Dark, "
        f"который не поставляется вместе со скомпилированной программой."
    )


def philosophy():
    print("""vsp210: Привет, мир!
?: А?
vsp210: Не узнаёшь свой первый вывод программы?
?: Кто ты?
vsp210: Я — vsp210, создатель языка программирования Dark.
?: И что с этого?
vsp210: Ты нашёл место, где чудесное и прекрасное встречаются. Это как инь и янь: в каждом есть частичка другого.

vsp210: Позволь мне поделиться с тобой философией Dark...

* Простое лучше, чем сложное.
* Сложное лучше, чем запутанное.
* Код пишется один раз, а читается — множество. Поэтому читаемость имеет значение.
* Явное лучше, чем неявное.
* Ошибки никогда не должны проходить незамеченными.
* Если реализацию трудно объяснить — это плохая идея.
* Если реализацию легко объяснить — возможно, это хорошая идея.

vsp210: Я рад, что ты используешь Dark. Удачи и успехов тебе, мой друг!
""")


def history():
    history = "Привет!\nМеня зовут Владимир, мне 16 лет, и я увлечён разработкой на Python.\nВ данном случае вы видите мой язык программирования Dark.\nКакое-то время я хотел быть писателем, а какое-то — спортсменом, но в итоге, не написав ни одной книги до конца и не став спортсменом, я стал программистом.\nИ я уверен, что если человек есть, значит, у него есть и интерес, и его надо развивать.\nУдачи!"
    def type_writer(text, delay):
        chars = text.split("")
        for char in chars:
            print(char)
            time.sleep(delay)

    type_writer(history, 0.01)



def _dark_type(x):
    if isinstance(x, dict):
        return 'dict'
    if isinstance(x, list):
        return 'list'
    if isinstance(x, (int, float)):
        return 'num'
    if isinstance(x, str):
        return 'str'
    if isinstance(x, bool):
        return 'bool'
    return type(x).__name__

def print_header(title):
    line = "========================================"
    print(line)
    print(("    " + title))
    print(line)
def add(a, b):
    return (a + b)
def subtract(a, b):
    return (a - b)
def multiply(a, b):
    return (a * b)
def divide(a, b):
    if (b == 0):
        print("Ошибка: Деление на ноль!")
        return "Error"
    return (a / b)
def get_number(prompt):
    while True:
        try:
            print(prompt)
            input_str = input()
            return float(input_str)
        except Exception as e:
            print((("Ошибка: Введите корректное число. (" + e.message) + ")"))
def get_op_symbol(choice):
    if (choice == "1"):
        return "+"
    if (choice == "2"):
        return "-"
    if (choice == "3"):
        return "*"
    if (choice == "4"):
        return "/"
    return "?"
def run_calculator():
    operations = {"1": {"func": add, "desc": "Сложение"}, "2": {"func": subtract, "desc": "Вычитание"}, "3": {"func": multiply, "desc": "Умножение"}, "4": {"func": divide, "desc": "Деление"}}
    history = []
    while True:
        print_header("Калькулятор на Dark.Lang")
        print("Выберите операцию:")
        for key in operations.keys():
            print(((key + ") ") + operations[key]["desc"]))
        print("5) Показать историю")
        print("6) Выход")
        choice = input()
        if (choice == "6"):
            print("До свидания!")
            exit()
        if (choice == "5"):
            print_header("История операций")
            if (len(history) == 0):
                print("История пуста.")
            else:
                for item in history:
                    print(item)
        else:
            try:
                op_details = operations[choice]
                print_header(op_details["desc"])
                num1 = get_number("Введите первое число:")
                num2 = get_number("Введите второе число:")
                result = op_details["func"](num1, num2)
                if (_dark_type(result) != "str"):
                    result_str = ((((((str(num1) + " ") + get_op_symbol(choice)) + " ") + str(num2)) + " = ") + str(result))
                    print(("Результат: " + result_str))
                    history.append(result_str)
            except Exception as e:
                print("Неверный выбор. Попробуйте снова.")
        print("\nНажмите Enter для продолжения...")
        input()
        os.system("cls||clear")


def calculator():
    run_calculator()
