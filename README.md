<!-- Copyright 2026 Dark.Tehno

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->
<div align="center">
  <img src="https://www.vsp210.ru/static/img/image-not_bg.png" alt="Логотип Dark" width="150" height="150">
  <h1>Dark Programming Language</h1>
  <p>Исходный код интерпретируемого языка программирования Dark, написанного на Python. Современный, динамический язык, созданный с акцентом на простоту и эффективность.</p>

  <p>
    <a href="https://vsp210.ru/dark-lang/"><strong>Документация</strong></a> ·
    <a href="https://github.com/Dark-Tehno/Dark-Lang-Source-Code/issues/new/choose"><strong>Сообщить об ошибке / Предложить идею</strong></a> ·
    <a href="https://marketplace.visualstudio.com/items?itemName=vsp210.dark-lang"><strong>Расширение для VS Code</strong></a>
  </p>

  <p>
    <a href="https://vsp210.ru/dark-lang/"><img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version"></a>
    <img src="https://img.shields.io/badge/language-Python-blue.svg" alt="Python language">
    <img src="https://img.shields.io/github/license/Dark-Tehno/Dark-Lang-Source-Code" alt="License">
  </p>
</div>

**Dark** — это современный, динамический язык программирования, созданный с акцентом на простоту и эффективность. Его синтаксис интуитивно понятен, что делает его отличным выбором как для начинающих, так и для опытных разработчиков.

Этот репозиторий содержит полный исходный код интерпретатора языка, включая лексер, парсер, исполнитель, а также все встроенные модули.

## 🎉 Что нового в 2.0.0

Главное событие этого релиза — **система компиляции завершена** и больше не помечена как экспериментальная: `--compile` компилирует скрипт Dark в набор Python-файлов и, при необходимости, собирает из них нативный standalone-исполняемый файл через **Nuitka**.

## 🚀 Ключевые особенности

*   **Простой и чистый синтаксис:** Вдохновленный Python, синтаксис Dark легко читается и пишется.
*   **Объектно-ориентированное программирование:** Полная поддержка классов, наследования, конструктора `__main__` и переопределения операторов через специальные методы (`__add__`, `__eq__` и т.д.).
*   **Компиляция в исполняемый файл:** Флаг `--compile` собирает `.dark`-скрипт в Python-код и, через Nuitka, в нативный `.exe` / standalone-бинарник.
*   **Менеджер пакетов dpm:** Встроенный `dpm` (Dark Package Manager) устанавливает, удаляет и управляет Python-расширениями внутри виртуальных окружений `denv`.
*   **Богатая стандартная библиотека:** Встроенные модули для работы с файловой системой (`os`), математикой (`math`), HTTP-запросами (`http`), временем (`time`), файлами (`file`), цветным выводом в консоль (`color`), погодой (`weather`) и многим другим.
*   **Мощная интеграция с Python:**
    *   Возможность писать **модули-расширения** на Python и импортировать их в Dark.
    *   Прямое выполнение Python-кода из Dark-скриптов с помощью модуля `python` (директива `#!USE_WITH_PYTHON`).
*   **Импорт модулей из интернета:** можно импортировать `.dark`-модуль напрямую по URL.
*   **Инструменты для разработки:**
    *   **VS Code расширение** с подсветкой синтаксиса, IntelliSense, линтером и запуском кода.
    *   Встроенный **линтер** для проверки синтаксиса и семантики (`--check`).
    *   Просмотр AST скрипта (`--parser`) и интерактивный REPL (`--repl`).
    *   **Кэширование AST** для ускорения повторного запуска скриптов.

## ✍️ Пример кода

Вот небольшой пример, демонстрирующий синтаксис Dark. Этот код печатает текст с эффектом пишущей машинки.

```dark
# Импортируем стандартные модули
import "time"
import "stdlib"

# Наша история
history = "Привет, Хабр! Это мой язык Dark."

# Функция для красивой печати
function type_writer(text, delay) do
    # Разбиваем строку на символы
    chars = stdlib.str_split(text, "")

    # Итерируемся по списку символов
    for char in chars do
        print(char) # Печатаем символ без переноса строки
        time.sleep(delay)
    end
    println("") # Перенос строки в конце
end

# Запускаем!
type_writer(history, 0.05)
```

## 🛠️ Установка и использование

1.  **Скачайте установщик** последней версии со страницы документации.
    *   <a href="https://vsp210.ru/media/public/Dark-Lang-setup-v2.0.0.exe" class="download-button">**Скачать установщик Dark v2.0.0 (Для Windows)**</a> *(ссылка появится в документации)*
    *   Для Linux загрузите исходный код и перейдите в папку Dark-Lang-Source-Code через терминал.
    Затем выполните:
    ```bash
    sudo ./install.sh
    ```

2.  **Установите расширение для VS Code** для комфортной разработки.
    *   **Dark Language Support** в VS Code Marketplace

3.  **Настройте VS Code (Windows)**, указав путь к исполняемому файлу `dark_start.exe` в `settings.json`:
    ```json
    {
        "dark.executorPath": "C:\Program Files (x86)\Dark-Lang\dark_start.exe"
    }
    ```
    (Линус версия сделает всё сама)

4.  **Создайте свой первый файл** `script.dark` и запустите его с помощью иконки ▶ в редакторе или через консоль.

### Запуск из консоли

Вы можете запускать скрипты напрямую:

```bash
# Запуск скрипта
dark_start.exe my_script.dark

# Проверка синтаксиса (линтинг) без выполнения
dark_start.exe --check my_script.dark
```

### Компиляция в исполняемый файл

С версии 2.0.0 компиляция полностью готова к использованию:

```bash
# Сгенерировать Python-код в папку ./build_output
dark --compile my_script.dark --out ./build_output

# Сгенерировать и собрать standalone-исполняемый файл через Nuitka
dark --compile my_script.dark --out ./build_output --nuitka-args="--onefile"

# Только сгенерировать Python-код, без сборки .exe
dark --compile my_script.dark --out ./build_output --nonuitka
```

> Для сборки через Nuitka требуется предустановленный компилятор C (например, MSVC на Windows).

### Менеджер пакетов dpm

```bash
# Установить пакет
dark --dpm install utils

# Удалить пакет
dark --dpm uninstall utils

# Список установленных пакетов
dark --dpm list

# Зафиксировать зависимости проекта
dark --dpm freeze
```

## 📚 Документация

Подробное описание синтаксиса, ООП, стандартной библиотеки, менеджера пакетов `dpm`, компиляции и аргументов запуска доступно в **[официальной документации](https://vsp210.ru/dark-lang/)**.

## 👨‍💻 Об авторе

Привет! Меня зовут Владимир, мне 16 лет. Я увлекся программированием и решил создать собственный язык, чтобы глубже погрузиться в мир компиляторов, парсеров и интерпретаторов. Dark — это мой главный проект, в который я вкладываю свои знания и время.

## 🤝 Содействие

Если вы нашли ошибку или у вас есть предложение по улучшению языка, пожалуйста, **создайте Issue**. Это лучший способ помочь проекту. Любая обратная связь очень важна для его развития!

---

*Спасибо, что уделили время моему проекту!*
