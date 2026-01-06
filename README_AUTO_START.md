# הפעלה אוטומטית של מערכות המעקב

## שיטה 1: Task Scheduler (מומלץ)

### שלב 1: פתיחת Task Scheduler
1. לחץ על `Win + R`
2. הקלד `taskschd.msc` ולחץ Enter
3. Task Scheduler יפתח

### שלב 2: יצירת Task חדש
1. לחץ על **"Create Basic Task"** (מימין)
2. שם: `Polymarket Monitor Positions`
3. תיאור: `מעקב אוטומטי אחר שינויים בפוזיציות`
4. לחץ **Next**

### שלב 3: הגדרת טריגר
1. בחר **"When the computer starts"**
2. לחץ **Next**

### שלב 4: הגדרת פעולה
1. בחר **"Start a program"**
2. לחץ **Next**
3. **Program/script**: `C:\Users\gtoli\polymarket-tracker\python.exe`
   - (או הנתיב המלא ל-Python שלך - בדוק עם `where python`)
4. **Add arguments**: `monitor_positions.py`
5. **Start in**: `C:\Users\gtoli\polymarket-tracker`
6. לחץ **Next**

### שלב 5: סיום
1. סמן **"Open the Properties dialog for this task when I click Finish"**
2. לחץ **Finish**
3. בחלון Properties:
   - סמן **"Run whether user is logged on or not"**
   - סמן **"Run with highest privileges"**
   - לחץ **OK**

### חזור על התהליך עבור:
- **Task שני**: `Polymarket Monitor Trades`
  - **Add arguments**: `telegram_monitor.py`

---

## שיטה 2: Startup Folder (פשוט יותר)

### שלב 1: פתיחת Startup Folder
1. לחץ על `Win + R`
2. הקלד `shell:startup` ולחץ Enter
3. תיקיית Startup תיפתח

### שלב 2: יצירת קיצורי דרך
1. העתק את `start_all_monitors.bat` לתיקיית Startup
2. או צור קיצורי דרך לשני הקבצים:
   - `monitor_positions.py`
   - `telegram_monitor.py`

---

## מניעת מצב שינה

### הגדרת Power Options
1. לחץ על `Win + X` → **Power Options**
2. לחץ על **"Additional power settings"** (מימין)
3. לחץ על **"Change when the computer sleeps"**
4. הגדר:
   - **"Put the computer to sleep"**: **Never**
   - **"Turn off the display"**: לפי העדפתך
5. לחץ **Save changes**

---

## בדיקה שהכל עובד

1. הפעל מחדש את המחשב
2. פתח Task Manager (`Ctrl + Shift + Esc`)
3. לחץ על **"Details"**
4. חפש תהליכי `python.exe` שרצים עם:
   - `monitor_positions.py`
   - `telegram_monitor.py`

אם הם רצים - הכל תקין! ✅

---

## פתרון בעיות

### התהליכים לא רצים אחרי הפעלה מחדש?
- בדוק ש-Python מותקן וזמין ב-PATH
- בדוק שהנתיבים ב-Task Scheduler נכונים
- בדוק את ה-Logs ב-Task Scheduler (History)

### המחשב נכנס למצב שינה?
- ודא שהגדרת Power Options כמו שמוסבר למעלה
- בדוק ש-Task Scheduler מוגדר לרוץ גם כשהמשתמש לא מחובר
