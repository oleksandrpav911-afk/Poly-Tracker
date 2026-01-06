# פתרון בעיות Streamlit Cloud

## שלב 1: בדיקת GitHub

1. לך ל: https://github.com/oleksandrpav911-afk/Poly-Tracker
2. ודא ש-`dashboard.py` מעודכן (יש בו את הפונקציות `style_sport_type`)
3. ודא ש-`requirements.txt` קיים

## שלב 2: בדיקת Streamlit Cloud

1. לך ל: https://share.streamlit.io/
2. התחבר עם GitHub
3. מצא את ה-app שלך
4. לחץ עליו

### בדיקות:

**א. בדוק את ה-Logs:**
- לחץ על **"Manage app"** או **"⋮"** (3 נקודות)
- לחץ על **"View logs"** או **"Logs"**
- חפש שגיאות (אדום)

**ב. בדוק את ההגדרות:**
- לחץ על **"Settings"** או **"⚙️"**
- ודא ש:
  - **Main file path**: `dashboard.py`
  - **Branch**: `main`
  - **Python version**: 3.9 או 3.10

**ג. Reboot את ה-App:**
- לחץ על **"⋮"** (3 נקודות)
- לחץ על **"Reboot app"** או **"Restart"**
- המתן 30-60 שניות

## שלב 3: אם עדיין לא עובד

### אפשרות א: מחק ויצור מחדש
1. ב-Streamlit Cloud, מחק את ה-app הישן
2. לחץ **"New app"**
3. בחר את ה-repository: `Poly-Tracker`
4. בחר: `dashboard.py`
5. לחץ **Deploy**

### אפשרות ב: Force Update
1. ב-GitHub Desktop, עשה שינוי קטן ב-`dashboard.py` (למשל, הוסף הערה)
2. Commit ו-Push
3. זה יגרום ל-Streamlit Cloud להתעדכן

### אפשרות ג: בדוק את requirements.txt
ודא ש-`requirements.txt` מכיל:
```
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
plotly>=5.17.0
```

## שלב 4: בדיקה מהירה

פתח את ה-URL של ה-app שלך ב-Streamlit Cloud ובדוק:
- האם הדף נטען?
- האם יש שגיאות בקונסול (F12 → Console)?
- האם הנתונים מופיעים?

---

## שגיאות נפוצות:

**"Module not found"**
→ בדוק ש-`requirements.txt` מעודכן

**"File not found"**
→ ודא ש-`dashboard.py` הוא הקובץ הראשי

**"App is not updating"**
→ לחץ **Reboot app** או מחק ויצור מחדש
