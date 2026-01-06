# עדכון Repository קיים ב-GitHub

## שלב 1: חיבור התיקייה המקומית ל-Repository הקיים

פתח PowerShell בתיקיית הפרויקט והרץ:

```powershell
# אתחול Git
git init

# הוספת כל הקבצים
git add .

# יצירת commit ראשון
git commit -m "Updated dashboard with new features"

# חיבור ל-repository הקיים (החלף את ה-URL בכתובת ה-repository שלך)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# העלאה ל-GitHub
git branch -M main
git push -u origin main
```

**אם יש כבר קבצים ב-repository:**
```powershell
git pull origin main --allow-unrelated-histories
git push origin main
```

---

## שלב 2: עדכון עתידי

אחרי כל שינוי בקוד, פשוט:

```powershell
git add .
git commit -m "Updated dashboard"
git push
```

**Streamlit Cloud יתעדכן אוטומטית תוך 1-2 דקות!** 🚀

---

## מה צריך להעלות?

✅ **חייבים:**
- `dashboard.py` (עם כל השינויים)
- `requirements.txt`

✅ **מומלץ:**
- `.gitignore` (כבר קיים)

❌ **לא להעלות:**
- קבצי נתונים (`.json`, `.csv`)
- `processed_trades.json`
- `telegram_monitor.lock`
