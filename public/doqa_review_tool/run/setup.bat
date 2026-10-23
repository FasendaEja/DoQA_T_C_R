@echo off
chcp 65001 >nul
title DoQA Review Tool - Установка
echo ========================================
echo   Установка DoQA Review Tool
echo ========================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Скачайте Python с https://www.python.org/downloads/windows/
    echo При установке ОБЯЗАТЕЛЬНО отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python найден
python --version
echo.

:: Создание виртуального окружения
if not exist "venv\" (
    echo [*] Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано
) else (
    echo [OK] Виртуальное окружение уже существует
)
echo.

:: Активация и установка зависимостей
call venv\Scripts\activate.bat
echo [*] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости
    pause
    exit /b 1
)
echo [OK] Зависимости установлены
echo.

:: Создание папки input для входящих файлов
if not exist "input\" (
    mkdir input
    echo [OK] Папка input создана
) else (
    echo [OK] Папка input уже существует
)
echo.

:: Создание .env из шаблона
if not exist ".env" (
    copy .env.example .env >nul
    echo [OK] Файл .env создан из шаблона
    echo.
    echo [!] ВАЖНО: Отредактируйте .env и заполните параметры
    echo [!] Сейчас откроется блокнот с файлом .env
    echo.
    pause
    notepad .env
) else (
    echo [OK] Файл .env уже существует
)

echo.
echo ========================================
echo   Установка завершена!
echo ========================================
echo.
echo Теперь:
echo   1. Заполните .env нужными параметрами
echo   2. Для режима file: поместите xlsx файлы в папку input/
echo   3. Запустите run.bat для работы утилиты
echo.
echo ========================================
pause
