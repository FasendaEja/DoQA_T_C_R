@echo off
chcp 65001 >nul
title DoQA Review Tool
echo ========================================
echo   DoQA Review Tool - запуск...
echo ========================================
echo.

:: Проверка виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo [ОШИБКА] Виртуальное окружение не найдено!
    echo.
    echo Сначала запустите setup.bat для первичной настройки.
    echo.
    pause
    exit /b 1
)

:: Активация виртуального окружения
call venv\Scripts\activate.bat

:: Проверка .env
if not exist ".env" (
    echo [ОШИБКА] Файл .env не найден!
    echo.
    echo Сначала запустите setup.bat и заполните .env.
    echo.
    pause
    exit /b 1
)

:: Запуск утилиты
python doqa_review.py

echo.
echo ========================================
echo   Готово! Нажмите любую клавишу...
echo ========================================
pause >nul
