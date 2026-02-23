import os, tables, unicode
from ../dark/builtins import println, print, input, to_int, to_float, dark_type
from ./dark_os import system
from ./time import dark_time, dark_sleep


proc version*(): auto =
    return "1.0.0"

proc docs*(): auto =
    when defined(windows):
        discard execShellCmd("start https://vsp210.ru/dark-lang/")
    elif defined(macosx):
        discard execShellCmd("open https://t.me/vsp210_official")
    else: 
        discard execShellCmd("xdg-open https://vsp210.ru/dark-lang/")
    return "Докментация по языку Dark"

proc telegram*(): auto =
    when defined(windows):
        discard execShellCmd("start https://t.me/vsp210_official")
    elif defined(macosx):
        discard execShellCmd("open https://t.me/vsp210_official")
    else: 
        discard execShellCmd("xdg-open https://t.me/vsp210_official")
    return "Телеграм канал создателя языка Dark"

# calculator:
proc print_header(title: string): auto =
    let line = "========================================"
    println(line)
    println("    " & title)
    println(line)

proc add(a: float, b: float): string =
    return $(a + b)

proc subtract(a: float, b: float): string =
    return $(a - b)

proc multiply*(a: float, b: float): string =
    return $(a * b)

proc divide(a: float, b: float): string =
    if b == 0:
        println("Ошибка: Деление на ноль!")
        return "Error"
    return $(a / b)

proc get_number(prompt: string): float =
    while true:
        try:
            println(prompt)
            let input_str = input()
            return to_float(input_str)
        except ValueError:
            println("Ошибка: Введите корректное число.")
        except Exception as e:
            println("Ошибка: Введите корректное число. (" & e.msg & ")")

proc get_op_symbol(choice: string): string =
    if choice == "1": return "+"
    if choice == "2": return "-"
    if choice == "3": return "*"
    if choice == "4": return "/"
    return "?"


type OperationProc = proc(a: float, b: float): string

proc calculator*() =
    var operations = {
        "1": (operation: OperationProc(vsp210.add), desc: "Сложение"),
        "2": (operation: vsp210.subtract, desc: "Вычитание"),
        "3": (operation: vsp210.multiply, desc: "Умножение"),
        "4": (operation: vsp210.divide, desc: "Деление")
    }.toTable()
    var history: seq[string] = @[]

    while true:
        print_header("Калькулятор на Dark.Lang")
        println("Выберите операцию:")

        for key, val in operations:
            println(key & ") " & val.desc)

        println("5) Показать историю")
        println("6) Выход")

        var choice = input()

        if choice == "6":
            println("До свидания!")
            quit()

        if choice == "5":
            print_header("История операций")
            if history.len() == 0:
                println("История пуста.")
            else:
                for item in history:
                    println(item)
        else:
            try:
                var op_details = operations[choice]

                print_header(op_details.desc)

                var num1 = get_number("Введите первое число:")
                var num2 = get_number("Введите второе число:")
                var result = op_details.operation(num1, num2)

                if result != "Error":
                    var result_str = $num1 & " " & get_op_symbol(choice) & " " & $num2 & " = " & result
                    println("Результат: " & result_str)
                    history.add(result_str)

            except Exception:
                println("Неверный выбор. Попробуйте снова.")

        println("\nНажмите Enter для продолжения...")
        discard input()
        discard system("cls||clear")


# history:
var history_text = "Привет!\nМеня зовут Владимир, мне 15 лет, и я увлечён разработкой на Python.\nВ данном случае вы видите мой язык программирования Dark.\nКакое-то время я хотел быть писателем, а какое-то — спортсменом, но в итоге, не написав ни одной книги до конца и не став спортсменом, я стал программистом.\nИ я уверен, что если человек есть, значит, у него есть и интерес, и его надо развивать.\nУдачи!"

proc history*(): auto =
    for c in history_text:
        print($c)
        dark_sleep(0.01)
    println("")

# philosophy:
var encrypted = "Czw987:вЦчпилщгвупчеgё:вЖёgCzw987:вФлвъофжмяГвшихрвцлчиВрвиВихквцчхйчжууВёgё:вСщхвщВёgCzw987:вfв—вCzw987гвшхокжщлтГвЁоВсжвцчхйчжуупчхижфпЁвKhyrдgё:вПвющхвшвДщхйхёgCzw987:вЩВвфжямтвулшщхгвйклвюъклшфхлвпвцчлсчжшфхлвишщчлюжЕщшЁдвdщхвсжсвпфГвпвЁфГ:вивсжнкхувлшщГвюжшщпюсжвкчъйхйхдggCzw987:вЦхоихтГвуфлвцхклтпщГшЁвшвщхзхрвыптхшхыплрвKhyrдддgg*вЦчхшщхлвтъюялгвюлувштхнфхлдg*вШтхнфхлвтъюялгвюлувожцъщжффхлдg*вСхквцпялщшЁвхкпфвчжогвжвюпщжлщшЁв—вуфхнлшщихдвЦхДщхуъвюпщжлухшщГвпуллщвофжюлфплдg*вfифхлвтъюялгвюлувфлЁифхлдg*вХяпзспвфпсхйкжвфлвкхтнфВвцчхьхкпщГвфложулюлффВупдg*вЛштпвчлжтпожэпЕвщчъкфхвхзБЁшфпщГв—вДщхвцтхьжЁвпклЁдg*вЛштпвчлжтпожэпЕвтлйсхвхзБЁшфпщГв—вихоухнфхгвДщхвьхчхяжЁвпклЁдggCzw987:вfвчжкгвющхвщВвпшцхтГоъляГвKhyrдвЪкжюпвпвъшцльхивщлзлгвухрвкчъйе"
var alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,.!?абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ\n"
var key = 7

proc transform_text(text: string, key: int, direction: int): string =
    result = ""
    var alphabetRunes: seq[Rune] = @[]
    for r in alphabet.runes: alphabetRunes.add(r)
    let alphabetRunesLen = alphabetRunes.len

    for cr in text.runes:
        let position = find(alphabetRunes, cr)
        if position != -1:
            var offset = position + (key * direction)
            var new_position = (offset + alphabetRunesLen) mod alphabetRunesLen
            result.add($alphabetRunes[new_position])
        else:
            result.add($cr)

proc philosophy*(): string =
    println(transform_text(encrypted, key, -1))