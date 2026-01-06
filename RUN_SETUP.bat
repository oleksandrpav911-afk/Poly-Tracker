@echo off
echo ============================================================
echo הגדרת הפעלה אוטומטית - Polymarket Monitors
echo ============================================================
echo.
echo הסקריפט יוצר Tasks ב-Windows שיפעילו את המערכות אוטומטית
echo בכל הפעלה של המחשב.
echo.
echo חשוב: צריך להריץ כנהלה (Administrator)!
echo.
pause

cd /d "%~dp0"

powershell.exe -ExecutionPolicy Bypass -File "setup_auto_start.ps1"

echo.
echo ============================================================
echo סיום
echo ============================================================
echo.
pause
