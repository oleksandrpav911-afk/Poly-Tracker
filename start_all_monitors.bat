@echo off
echo ============================================================
echo הפעלת כל מערכות המעקב
echo ============================================================
echo.

cd /d "%~dp0"

echo הפעלת מעקב פוזיציות...
start "Monitor Positions" python monitor_positions.py

timeout /t 2 /nobreak >nul

echo הפעלת מעקב עסקאות...
start "Monitor Trades" python telegram_monitor.py

echo.
echo ============================================================
echo כל המערכות הופעלו!
echo ============================================================
echo.
echo לסגירה: סגור את חלונות הקונסולה
pause
