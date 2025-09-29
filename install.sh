#!/bin/bash

# Скрипт для установки языка программирования Dark в систему

# 1. Проверка прав суперпользователя (root/sudo)
if [ "$(id -u)" -ne 0 ]; then
  echo "Ошибка: для установки требуются права суперпользователя. Пожалуйста, запустите скрипт с 'sudo'." >&2
  exit 1
fi

# 2. Определение путей установки
# /usr/local/bin - стандартное место для пользовательских исполняемых файлов
INSTALL_BIN_DIR="/usr/local/bin"
# /usr/local/lib/dark - для библиотек и модулей вашего языка
INSTALL_LIB_DIR="/usr/local/lib/dark"

# Имя вашего исполняемого файла
EXECUTABLE="dark/dark_start"

echo "Начало установки Dark Programming Language..."

# 3. Создание директорий
echo "Создание директории для библиотек: $INSTALL_LIB_DIR"
mkdir -p "$INSTALL_LIB_DIR"

# 4. Копирование файлов
# Копируем исполняемый файл
echo "Копирование исполняемого файла в $INSTALL_BIN_DIR"
cp "./$EXECUTABLE" "$INSTALL_BIN_DIR/dark" # Переименовываем в 'dark' для удобства

# Копируем остальные необходимые файлы (например, модули языка)
echo "Копирование библиотек в $INSTALL_LIB_DIR"
# Убедитесь, что папка dark_code находится рядом со скриптом
cp -r ./dark/dark_code "$INSTALL_LIB_DIR/"
# Если есть другие папки, например assets, их тоже можно скопировать
# cp -r ./assets "$INSTALL_LIB_DIR/"

# 5. Установка прав на исполнение
echo "Установка прав на исполнение для 'dark'"
chmod +x "$INSTALL_BIN_DIR/dark"

echo ""
echo "Установка успешно завершена!"
echo "Теперь вы можете запускать свои скрипты командой: dark your_script.dark"
echo "Для удаления выполните 'sudo rm /usr/local/bin/dark && sudo rm -rf /usr/local/lib/dark'"

exit 0
