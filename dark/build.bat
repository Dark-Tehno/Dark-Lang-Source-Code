@echo off
setlocal

REM Папка для временной сборки Nuitka
set BUILD_DIR=build
REM Папка для чистого релиза
set RELEASE_DIR=release

echo --- Cleaning up previous builds ---
if exist %BUILD_DIR% ( rd /s /q %BUILD_DIR% )
if exist %RELEASE_DIR% ( rd /s /q %RELEASE_DIR% )

echo --- Compiling with Nuitka ---
python -m nuitka ^
    --standalone ^
    --output-dir=%BUILD_DIR% ^
    --enable-plugin=tk-inter ^
    --include-data-dir=code=code ^
    --include-data-dir=dark_code/compiler/NIM_CODE=dark_code/compiler/NIM_CODE ^
    --include-data-dir=assets=assets ^
    --msvc=latest ^
    --windows-icon-from-ico=assets/icon.png ^
    dark_start.py

if %errorlevel% neq 0 (
    echo [ERROR] Nuitka compilation failed.
    exit /b 1
)

echo --- Creating final release directory ---
mkdir %RELEASE_DIR%

echo --- Copying files to release directory ---
xcopy /E /I /Y "%BUILD_DIR%\dark_start.dist\*" "%RELEASE_DIR%\"

echo --- Cleaning up temporary build files ---
rd /s /q %BUILD_DIR%

echo --- Build finished successfully! ---
echo Your application is ready in the '%RELEASE_DIR%' folder.

endlocal
