# מעקב אוטומטי - הסבר

## מה זה מעקב אוטומטי?

מעקב אוטומטי הוא תהליך שבו הסקריפט רץ ברקע ומעדכן נתונים באופן קבוע ללא התערבות ידנית.

## איך זה עובד?

הסקריפט `auto_tracker.py`:
1. **רץ ברקע** - ממשיך לרוץ גם כשאתה לא משתמש במחשב
2. **מעדכן נתונים** - כל שעה (ניתן לשנות)
3. **שומר snapshots** - שומר עותק של הנתונים בכל עדכון
4. **יוצר היסטוריה** - כך תוכל לראות שינויים לאורך זמן

## שימוש

### הרצה רגילה:
```bash
python auto_tracker.py
```

### הרצה ברקע (Windows):
```bash
start /B python auto_tracker.py
```

### הרצה כשירות (Windows):
ניתן להשתמש ב-Task Scheduler של Windows להרצה אוטומטית בעת הפעלת המחשב.

## הגדרות

בקובץ `auto_tracker.py` תוכל לשנות:
- **תדירות עדכון**: שורה `schedule.every(1).hours.do(track_wallet)`
  - `every(30).minutes` - כל 30 דקות
  - `every(2).hours` - כל שעתיים
  - `every().day.at("10:30")` - כל יום בשעה 10:30

- **תיקיית שמירה**: משתנה `DATA_DIR`

## יתרונות

✅ **לא צריך לזכור** - הסקריפט עובד לבד  
✅ **היסטוריה מלאה** - כל snapshot נשמר  
✅ **ניתוח מגמות** - אפשר לראות שינויים לאורך זמן  
✅ **התראות** - אפשר להוסיף התראות על פעילות חדשה  

## דוגמאות לשימוש

### מעקב כל 30 דקות:
```python
schedule.every(30).minutes.do(track_wallet)
```

### מעקב פעמיים ביום:
```python
schedule.every().day.at("09:00").do(track_wallet)
schedule.every().day.at("21:00").do(track_wallet)
```

### מעקב רק בימי עסקים:
```python
schedule.every().monday.at("09:00").do(track_wallet)
schedule.every().tuesday.at("09:00").do(track_wallet)
# וכו'...
```

## התקנת schedule

אם לא מותקן:
```bash
pip install schedule
```

## עצירת המעקב

לחץ `Ctrl+C` בטרמינל שבו הסקריפט רץ.
