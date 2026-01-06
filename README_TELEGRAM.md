# התראות טלגרם - הוראות התקנה

## שלב 1: יצירת בוט בטלגרם

1. פתח טלגרם וחפש את `@BotFather`
2. שלח `/newbot`
3. בחר שם לבוט (למשל: "Polymarket Tracker")
4. בחר username לבוט (חייב להסתיים ב-bot)
5. **שמור את ה-TOKEN** שהבוט נותן לך

## שלב 2: קבלת Chat ID

יש שתי אפשרויות:

### אפשרות א: @userinfobot
1. חפש `@userinfobot` בטלגרם
2. שלח `/start`
3. הבוט ישלח לך את ה-Chat ID שלך

### אפשרות ב: דרך הבוט שלך
1. שלח הודעה לבוט שיצרת
2. פתח בדפדפן: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. חפש את `"chat":{"id":` - המספר הזה הוא ה-Chat ID

## שלב 3: הגדרת הקוד

### אפשרות א: עדכון ישיר בקובץ

ערוך את `telegram_notifier.py`:
```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
MIN_TRADE_SIZE_USDC = 100  # סכום מינימלי בדולרים
SPORT_FILTER = "NBA"       # סוג ספורט
```

### אפשרות ב: משתני סביבה (מומלץ)

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN="your_token_here"
$env:TELEGRAM_CHAT_ID="your_chat_id_here"
$env:MIN_TRADE_SIZE_USDC="100"
$env:SPORT_FILTER="NBA"
```

**Windows (CMD):**
```cmd
set TELEGRAM_BOT_TOKEN=your_token_here
set TELEGRAM_CHAT_ID=your_chat_id_here
set MIN_TRADE_SIZE_USDC=100
set SPORT_FILTER=NBA
```

## שלב 4: הרצה

### בדיקה חד פעמית:
```bash
python telegram_notifier.py
```

### מעקב רציף (כל 5 דקות):
```bash
python telegram_monitor.py
```

### הרצה ברקע (Windows):
```bash
start /B python telegram_monitor.py
```

## הגדרות

- **MIN_TRADE_SIZE_USDC**: סכום מינימלי בדולרים להתראה (ברירת מחדל: 100)
- **SPORT_FILTER**: סוג ספורט למעקב (NBA, NFL, NHL, וכו')
- **תדירות בדיקה**: כל 5 דקות (ניתן לשנות ב-`telegram_monitor.py`)

## דוגמה להודעה

כשהארנק מבצע עסקה ב-NBA מעל $100, תקבל הודעה:

```
🟢 קנייה - NBA

📊 Suns vs. Rockets: O/U 222.5
🎯 תוצאה: Under
💰 סכום: $192.00 USDC
📈 כמות: 400.00
💵 מחיר: 0.4800

⏰ זמן: 2026-01-05 15:26:11
🔗 ארנק: 0x16b29c50...
```

## פתרון בעיות

### "טלגרם לא מוגדר"
- ודא שהגדרת את `TELEGRAM_BOT_TOKEN` ו-`TELEGRAM_CHAT_ID`

### "שגיאה בשליחת הודעה"
- ודא שה-TOKEN נכון
- ודא ששלחת הודעה לבוט לפחות פעם אחת
- ודא שה-Chat ID נכון

### לא מקבל התראות
- ודא שהעסקה היא ב-NBA (או הסוג שהגדרת)
- ודא שהסכום מעל המינימום שהגדרת
- בדוק שהסקריפט רץ

## אבטחה

⚠️ **חשוב**: לעולם אל תעלה את ה-TOKEN ל-GitHub או מקומות ציבוריים!

- השתמש במשתני סביבה
- או הוסף את הקובץ ל-`.gitignore`
