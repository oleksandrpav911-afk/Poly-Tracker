@echo off
echo ============================================================
echo הפעלת מערכות המעקב - Polymarket
echo ============================================================
echo.

cd /d "%~dp0"

echo מפעיל Monitor Positions...
start "Polymarket Monitor Positions" python monitor_positions.py

timeout /t 2 /nobreak >nul

echo מפעיל Monitor Trades...
start "Polymarket Monitor Trades" python telegram_monitor.py

echo.
echo ============================================================
echo כל המערכות הופעלו!
echo ============================================================
echo.
echo שני חלונות נפתחו - אל תסגור אותם!
echo.
echo לסגירה: סגור את חלונות הקונסולה
echo.
pause
