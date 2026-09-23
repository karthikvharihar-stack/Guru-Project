@echo off
title Uttaradi Math - Guru Lekhana Seva Server
echo ========================================================
echo   Starting Uttaradi Math - Guru Lekhana Seva Server
echo   URL: http://127.0.0.1:5000
echo ========================================================
echo.
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo Opening browser at http://127.0.0.1:5000 ...
    timeout /t 2 /nobreak >nul
    start http://127.0.0.1:5000
    venv\Scripts\python.exe run.py
) else (
    echo Virtual environment not found. Please run setup first.
)

pause
