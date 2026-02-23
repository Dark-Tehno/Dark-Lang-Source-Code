#!/bin/bash
if [ "$(id -u)" -ne 0 ]; then
  echo "Ошибка: для установки требуются права суперпользователя. Пожалуйста, запустите скрипт с 'sudo'." >&2
  exit 1
fi

INSTALL_BIN_DIR="/usr/local/bin"
INSTALL_LIB_DIR="/usr/local/lib/dark"
EXECUTABLE_NAME="dark"

echo "Начало установки Dark Programming Language..."

echo "Создание директории для библиотек: $INSTALL_LIB_DIR"
mkdir -p "$INSTALL_LIB_DIR"

echo "Копирование исполняемого файла в $INSTALL_BIN_DIR"
cp -r dark/release-linux/* "$INSTALL_LIB_DIR/"

echo "Установка прав на исполнение для '$INSTALL_LIB_DIR/$EXECUTABLE_NAME'"
chmod +x "$INSTALL_LIB_DIR/$EXECUTABLE_NAME"

echo "Создание символической ссылки для запуска в $INSTALL_BIN_DIR"
ln -sf "$INSTALL_LIB_DIR/$EXECUTABLE_NAME" "$INSTALL_BIN_DIR/$EXECUTABLE_NAME"

echo ""
echo "Установка успешно завершена!"
echo "Теперь вы можете запускать свои скрипты командой: dark your_script.dark"
echo "Для удаления выполните:"
echo "  sudo rm \"$INSTALL_BIN_DIR/$EXECUTABLE_NAME\""
echo "  sudo rm -rf \"$INSTALL_LIB_DIR\""

exit 0
