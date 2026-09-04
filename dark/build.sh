#!/bin/bash
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

# echo "--- Очистка предыдущих сборок ---"
# rm -rf "$BUILD_DIR"
# rm -rf "$RELEASE_DIR"

echo "--- Компиляция с помощью Nuitka для Linux ---"
python3 -m nuitka \
    --standalone \
    --output-filename="$EXECUTABLE_NAME" \
    --enable-plugin=tk-inter \
    --include-data-dir=code=code \
    --include-data-dir=assets=assets \
    --include-raw-dir=dark_code/compiler/py_dark_code=dark_code/compiler/py_dark_code \
    --no-deployment-flag=self-execution \
    dark_start.py 

# echo --- Cleaning and creating final release directory ---
echo "--- Очистка предыдущей релиза ---"
if [ -d "$RELEASE_DIR" ]; then
    rm -rf "$RELEASE_DIR"
fi
mkdir -p "$RELEASE_DIR"

echo "--- Копирование файлов в директорию релиза ---"
# Копируем всё содержимое из .dist папки
cp -r "dark_start.dist/"* "$RELEASE_DIR/"

echo "--- Очистка временных файлов сборки ---"
rm -rf "dark_start.dist"
rm -rf "dark_start.build"

echo "--- Сборка для Linux успешно завершена! ---"
echo "Готовое приложение находится в папке '$RELEASE_DIR'."
