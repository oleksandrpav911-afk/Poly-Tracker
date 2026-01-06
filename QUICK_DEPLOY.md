# עדכון מהיר - 3 שלבים

## 1️⃣ יצירת Repository ב-GitHub

1. לך ל: https://github.com/new
2. שם: `polymarket-tracker`
3. בחר **Public**
4. לחץ **Create repository**

## 2️⃣ העלאת הקבצים

### דרך GitHub Desktop (מומלץ):

1. הורד: https://desktop.github.com/
2. פתח → **File → Add Local Repository**
3. בחר: `C:\Users\gtoli\polymarket-tracker`
4. לחץ **Publish repository**

### או דרך PowerShell:

```powershell
cd C:\Users\gtoli\polymarket-tracker
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/polymarket-tracker.git
git branch -M main
git push -u origin main
```

## 3️⃣ חיבור ל-Streamlit Cloud

1. לך ל: https://share.streamlit.io/
2. התחבר עם GitHub
3. לחץ **New app**
4. בחר את ה-repository
5. בחר: `dashboard.py`
6. לחץ **Deploy**

✅ **סיימת!** הדשבורד יהיה זמין בכתובת: `https://your-app-name.streamlit.app`

---

## 🔄 עדכון עתידי

אחרי כל שינוי, פשוט:

**GitHub Desktop:**
- Commit → Push

**או PowerShell:**
```powershell
git add .
git commit -m "Updated dashboard"
git push
```

Streamlit Cloud יתעדכן אוטומטית תוך דקה! 🚀
