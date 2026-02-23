#!/bin/bash

# Останавливаем скрипт при любой ошибке
set -e

# --- Проверка зависимостей ---
if ! command -v patchelf &> /dev/null
then
    echo "Ошибка: 'patchelf' не найден. Эта утилита необходима для сборки в режиме --standalone."
    echo "Пожалуйста, установите ее, выполнив: sudo apt-get install patchelf"
    exit 1
fi

# --- Переменные ---
BUILD_DIR="build-linux"
RELEASE_DIR="release-linux"
EXECUTABLE_NAME="dark"

echo "--- Очистка предыдущих сборок ---"
rm -rf "$BUILD_DIR"
rm -rf "$RELEASE_DIR"

echo "--- Компиляция с помощью Nuitka для Linux ---"
python3 -m nuitka \
    --standalone \
    --output-dir="$BUILD_DIR" \
    --output-filename="$EXECUTABLE_NAME" \
    --enable-plugin=tk-inter \
    --include-data-dir=code=code \
    --include-data-dir=dark_code/compiler/NIM_CODE=dark_code/compiler/NIM_CODE \
    --include-data-dir=assets=assets \
    dark_start.py 

echo "--- Создание финальной директории релиза ---"
mkdir -p "$RELEASE_DIR"

echo "--- Копирование файлов в директорию релиза ---"
# Копируем всё содержимое из .dist папки
cp -r "$BUILD_DIR/dark_start.dist/"* "$RELEASE_DIR/"

echo "--- Очистка временных файлов сборки ---"
rm -rf "$BUILD_DIR"

echo "--- Сборка для Linux успешно завершена! ---"
echo "Готовое приложение находится в папке '$RELEASE_DIR'."
