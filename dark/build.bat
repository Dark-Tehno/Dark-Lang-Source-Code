REM Copyright 2026 Dark.Tehno
REM
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.
REM You may obtain a copy of the License at
REM
REM     http://www.apache.org/licenses/LICENSE-2.0
REM
REM Unless required by applicable law or agreed to in writing, software
REM distributed under the License is distributed on an "AS IS" BASIS,
REM WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM See the License for the specific language governing permissions and
REM limitations under the License.
@echo off
setlocal

REM Папка для временной сборки Nuitka
set BUILD_DIR=build
REM Папка для чистого релиза
set RELEASE_DIR=release

REM echo --- Cleaning up previous builds ---
REM if exist %BUILD_DIR% ( rd /s /q %BUILD_DIR% )

echo --- Compiling with Nuitka ---
python -m nuitka ^
    --standalone ^
    --enable-plugin=tk-inter ^
    --include-data-dir=code=code ^
    --include-data-dir=assets=assets ^
    --include-raw-dir=dark_code/compiler/py_dark_code=dark_code/compiler/py_dark_code ^
    --msvc=latest ^
    --windows-icon-from-ico=assets/icon.ico ^
    --no-deployment-flag=self-execution ^
    dark_start.py

if %errorlevel% neq 0 (
    echo [ERROR] Nuitka compilation failed.
    exit /b 1
)

echo --- Cleaning and creating final release directory ---
if exist %RELEASE_DIR% ( rd /s /q %RELEASE_DIR% )
mkdir %RELEASE_DIR%

echo --- Copying files to release directory ---
xcopy /E /I /Y "dark_start.dist\*" "%RELEASE_DIR%\"

echo --- Cleaning up temporary build files ---
rd /s /q "dark_start.dist"
rd /s /q "dark_start.build"

echo --- Build finished successfully! ---
echo Your application is ready in the '%RELEASE_DIR%' folder.

endlocal
