# דשבורד Polymarket Wallet Tracker

דשבורד אינטראקטיבי למעקב אחר ארנק ב-Polymarket.

## התקנה

1. התקן את התלויות:
```bash
pip install -r requirements.txt
```

## הפעלה

הרץ את הפקודה הבאה:
```bash
streamlit run dashboard.py
```

הדשבורד יפתח אוטומטית בדפדפן בכתובת: `http://localhost:8501`

## תכונות הדשבורד

- 📊 **סטטיסטיקות כלליות**: סה"כ עסקאות, נפח מסחר, ערך USDC, מחיר ממוצע
- 📈 **גרפים אינטראקטיביים**:
  - חלוקת עסקאות לפי תוצאה (Pie Chart)
  - עסקאות לפי שעה ביום
  - נפח מסחר מצטבר לאורך זמן
- 📋 **טבלת עסקאות**: עם אפשרויות סינון והצגה
- 💾 **הורדת נתונים**: CSV או JSON
- 🔄 **רענון אוטומטי**: נתונים מתעדכנים כל 5 דקות

## הערות

- הדשבורד משתמש ב-caching כדי לא להעמיס על ה-API
- ניתן לשנות את כתובת הארנק בקובץ `dashboard.py`
