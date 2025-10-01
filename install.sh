#!/bin/bash
if [ "$(id -u)" -ne 0 ]; then
  echo "Ошибка: для установки требуются права суперпользователя. Пожалуйста, запустите скрипт с 'sudo'." >&2
  exit 1
fi

INSTALL_BIN_DIR="/usr/local/bin"
INSTALL_LIB_DIR="/usr/local/lib/dark"
EXECUTABLE="dark/dark_start"

echo "Начало установки Dark Programming Language..."

echo "Создание директории для библиотек: $INSTALL_LIB_DIR"
mkdir -p "$INSTALL_LIB_DIR"

echo "Копирование исполняемого файла в $INSTALL_BIN_DIR"
cp "./$EXECUTABLE" "$INSTALL_BIN_DIR/dark"

echo "Копирование библиотек в $INSTALL_LIB_DIR"
cp -r ./dark/dark_code "$INSTALL_LIB_DIR/"

echo "Установка прав на исполнение для 'dark'"
chmod +x "$INSTALL_BIN_DIR/dark"

echo ""
echo "Установка успешно завершена!"
echo "Теперь вы можете запускать свои скрипты командой: dark your_script.dark"
echo "Для удаления выполните 'sudo rm /usr/local/bin/dark && sudo rm -rf /usr/local/lib/dark'"

exit 0
