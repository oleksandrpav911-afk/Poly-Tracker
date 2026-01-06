# איך לבדוק שהתהליכים רצים

## שלב 1: פתיחת Task Manager
1. לחץ `Ctrl + Shift + Esc` (או `Ctrl + Alt + Delete` → Task Manager)
2. אם אתה רואה תצוגה קטנה, לחץ על **"More details"**

## שלב 2: מעבר לטאב Details
1. לחץ על הטאב **"Details"** (בחלק העליון)
2. זה יציג את כל התהליכים שרצים

## שלב 3: חיפוש התהליכים
1. לחץ על העמודה **"Command line"** (אם היא לא מוצגת, לחץ ימני על כותרת עמודה → בחר "Command line")
2. לחץ `Ctrl + F` לחיפוש
3. חפש: `monitor_positions.py`
4. אם נמצא - זה אומר שהתהליך רץ! ✅
5. חפש גם: `telegram_monitor.py`
6. אם נמצא - זה אומר שהתהליך רץ! ✅

## איך זה אמור להיראות:
- **Image name**: `python.exe`
- **Command line**: `C:\Users\gtoli\AppData\Local\Programs\Python\Python312\python.exe "C:\Users\gtoli\polymarket-tracker\monitor_positions.py"`
- **Command line**: `C:\Users\gtoli\AppData\Local\Programs\Python\Python312\python.exe "C:\Users\gtoli\polymarket-tracker\telegram_monitor.py"`

## אם לא מוצאים:
1. פתח Task Scheduler (`Win + R` → `taskschd.msc`)
2. מצא את **"Polymarket Monitor Positions"**
3. לחץ ימני → **"Run"**
4. חזור על כך עבור **"Polymarket Monitor Trades"**
5. בדוק שוב ב-Task Manager

## טיפ:
אפשר גם לסנן לפי `python.exe` ולבדוק את ה-Command line של כל תהליך.
