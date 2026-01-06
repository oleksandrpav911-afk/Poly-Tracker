# הפעלת הדשבורד באינטרנט

## אפשרות 1: Streamlit Community Cloud (מומלץ - חינמי ופשוט)

### שלב 1: העלאה ל-GitHub
1. צור repository חדש ב-GitHub
2. העלה את הקבצים:
   - `dashboard.py`
   - `requirements.txt`
   - `README.md` (אופציונלי)

### שלב 2: הפעלה ב-Streamlit Cloud
1. לך ל: https://share.streamlit.io/
2. התחבר עם חשבון GitHub
3. לחץ על "New app"
4. בחר את ה-repository וה-branch
5. בחר את הקובץ: `dashboard.py`
6. לחץ על "Deploy"

הדשבורד יהיה זמין בכתובת: `https://your-app-name.streamlit.app`

---

## אפשרות 2: ngrok (לבדיקה מהירה)

### התקנה:
```bash
# Windows - הורד מ: https://ngrok.com/download
# או דרך Chocolatey:
choco install ngrok
```

### הפעלה:
1. הפעל את הדשבורד:
```bash
streamlit run dashboard.py
```

2. בחלון אחר, הפעל ngrok:
```bash
ngrok http 8501
```

3. תקבל כתובת זמנית (למשל: `https://abc123.ngrok.io`)

**הערה:** הכתובת משתנה בכל הפעלה, וזה רק לבדיקה.

---

## אפשרות 3: VPS / שרת ענן

### דוגמה עם DigitalOcean / AWS / Azure:

1. **התקן Python ו-Streamlit על השרת**
2. **העלה את הקבצים**
3. **הפעל עם nohup או systemd:**
```bash
nohup streamlit run dashboard.py --server.port 8501 &
```

4. **הגדר reverse proxy (nginx) או firewall**

---

## אפשרות 4: Railway / Render (חינמי עם הגבלות)

### Railway:
1. לך ל: https://railway.app
2. התחבר עם GitHub
3. צור פרויקט חדש
4. בחר את ה-repository
5. הגדר:
   - **Start Command**: `streamlit run dashboard.py --server.port $PORT`
   - **Environment**: Python

### Render:
1. לך ל: https://render.com
2. צור "Web Service"
3. חבר ל-GitHub repository
4. הגדר:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run dashboard.py --server.port $PORT`

---

## המלצה

**לשימוש אישי/קטן:** Streamlit Community Cloud - הכי פשוט וחינמי
**לבדיקה מהירה:** ngrok
**לשימוש רציף:** Railway או Render

---

## אבטחה

⚠️ **חשוב:**
- אם יש מידע רגיש (API keys, וכו'), אל תעלה אותו ל-GitHub
- השתמש ב-`.gitignore` כדי להסתיר קבצים רגישים
- בדוק שהכתובת הארנק לא רגישה (אם כן, אפשר להעביר כפרמטר)

---

## עדכון הדשבורד

אחרי כל שינוי בקוד:
1. העלה את השינויים ל-GitHub
2. Streamlit Cloud יתעדכן אוטומטית תוך דקות
