# הוראות עדכון הדשבורד ב-Streamlit Cloud

## שלב 1: יצירת Repository ב-GitHub

1. לך ל: https://github.com/new
2. צור repository חדש:
   - שם: `polymarket-tracker` (או שם אחר)
   - בחר **Public** (חינמי) או **Private**
   - **אל תסמן** "Add a README file"
   - לחץ **Create repository**

## שלב 2: העלאת הקבצים ל-GitHub

### אפשרות א: דרך GitHub Desktop (הכי פשוט)

1. הורד והתקן: https://desktop.github.com/
2. פתח GitHub Desktop
3. לחץ **File → Add Local Repository**
4. בחר את התיקייה: `C:\Users\gtoli\polymarket-tracker`
5. לחץ **Publish repository**
6. בחר את ה-repository שיצרת
7. לחץ **Publish**

### אפשרות ב: דרך Command Line

פתח PowerShell בתיקיית הפרויקט והרץ:

```powershell
# אתחול Git
git init

# הוספת כל הקבצים
git add .

# יצירת commit ראשון
git commit -m "Initial commit - Polymarket Tracker Dashboard"

# הוספת remote (החלף YOUR_USERNAME בשם המשתמש שלך)
git remote add origin https://github.com/YOUR_USERNAME/polymarket-tracker.git

# העלאה ל-GitHub
git branch -M main
git push -u origin main
```

## שלב 3: חיבור ל-Streamlit Cloud

1. לך ל: https://share.streamlit.io/
2. התחבר עם חשבון GitHub שלך
3. לחץ על **"New app"**
4. בחר:
   - **Repository**: `polymarket-tracker` (או השם שבחרת)
   - **Branch**: `main`
   - **Main file path**: `dashboard.py`
5. לחץ **Deploy**

## שלב 4: עדכון עתידי

אחרי כל שינוי בקוד:

### דרך GitHub Desktop:
1. פתח GitHub Desktop
2. תראה את השינויים
3. כתוב הודעה (למשל: "Updated colors and filters")
4. לחץ **Commit to main**
5. לחץ **Push origin**

### דרך Command Line:
```powershell
git add .
git commit -m "Updated dashboard with new features"
git push
```

**Streamlit Cloud יתעדכן אוטומטית תוך 1-2 דקות!**

---

## קבצים שצריכים להיות ב-Repository:

✅ **חייבים:**
- `dashboard.py`
- `requirements.txt`

✅ **מומלץ:**
- `README.md` (אופציונלי)
- `.gitignore` (כבר קיים)

❌ **לא להעלות:**
- קבצי נתונים (`.json`, `.csv`) - כבר ב-`.gitignore`
- קבצים רגישים (tokens, keys)

---

## פתרון בעיות

### "Repository not found"
- ודא שהעלית את הקבצים ל-GitHub
- ודא שהשם של ה-repository נכון

### "Module not found"
- ודא ש-`requirements.txt` מעודכן
- Streamlit Cloud יתקין אוטומטית את כל התלויות

### "App not updating"
- בדוק שהעלית את השינויים ל-GitHub (git push)
- המתן 1-2 דקות לעדכון
