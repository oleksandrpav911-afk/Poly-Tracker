"""
סקריפט בדיקה למערכת התראות טלגרם
בודק שהכל מוגדר נכון ושולח הודעת בדיקה
"""

import requests
import sys
from datetime import datetime

# תיקון encoding
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# ייבוא מהקובץ הראשי
from telegram_notifier import TelegramNotifier, get_user_activity, WALLET_ADDRESS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MIN_TRADE_SIZE_USDC, ALLOWED_SPORTS

def test_telegram_connection():
    """בדיקת חיבור לבוט טלגרם"""
    print("=" * 60)
    print("בדיקת חיבור לבוט טלגרם")
    print("=" * 60)
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN לא מוגדר!")
        return False
    
    if not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID לא מוגדר!")
        return False
    
    print(f"\n✓ BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"✓ CHAT_ID: {TELEGRAM_CHAT_ID}")
    
    # בדיקת חיבור
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"\n✅ חיבור מוצלח!")
                print(f"   שם הבוט: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                return True
            else:
                print(f"❌ שגיאה: {data}")
                return False
        else:
            print(f"❌ שגיאה: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ שגיאה בחיבור: {e}")
        return False

def send_test_message():
    """שליחת הודעת בדיקה"""
    print("\n" + "=" * 60)
    print("שליחת הודעת בדיקה")
    print("=" * 60)
    
    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    test_message = f"""
🧪 <b>הודעת בדיקה - Polymarket Tracker</b>

✅ המערכת פעילה ומוכנה!

📋 <b>הגדרות נוכחיות:</b>
• ארנק: {WALLET_ADDRESS[:10]}...
• סוגי ספורט: {', '.join(ALLOWED_SPORTS)}
• סכום מינימלי: ${MIN_TRADE_SIZE_USDC} USDC
• תדירות בדיקה: כל 5 דקות

⏰ זמן: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

המערכת תשלח התראות על עסקאות חדשות ב-NBA ו-Soccer מעל ${MIN_TRADE_SIZE_USDC} USDC.
"""
    
    if notifier.send_message(test_message):
        print("\n✅ הודעת הבדיקה נשלחה בהצלחה!")
        print("   בדוק בטלגרם שההודעה הגיעה")
        return True
    else:
        print("\n❌ שגיאה בשליחת הודעת הבדיקה")
        return False

def test_wallet_activity():
    """בדיקת פעילות הארנק"""
    print("\n" + "=" * 60)
    print("בדיקת פעילות הארנק")
    print("=" * 60)
    
    print(f"\n🔍 בודק פעילות עבור: {WALLET_ADDRESS}")
    activities = get_user_activity(WALLET_ADDRESS)
    
    if not activities:
        print("⚠️ לא נמצאו פעילויות")
        return False
    
    print(f"\n✅ נמצאו {len(activities)} פעילויות")
    
    # מיון לפי זמן
    activities.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # הצגת 5 האחרונות
    print("\n📊 5 העסקאות האחרונות:")
    print("-" * 60)
    
    trade_count = 0
    for i, activity in enumerate(activities[:10], 1):
        if activity.get('type') == 'TRADE':
            trade_count += 1
            if trade_count <= 5:
                title = activity.get('title', 'N/A')[:50]
                side = activity.get('side', 'N/A')
                usdc_size = activity.get('usdcSize', 0)
                timestamp = activity.get('timestamp', 0)
                
                if isinstance(timestamp, (int, float)):
                    dt = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = str(timestamp)
                
                print(f"{trade_count}. {side} - ${usdc_size:.2f} - {time_str}")
                print(f"   {title}")
    
    return True

def main():
    """פונקציה ראשית"""
    print("\n" + "=" * 60)
    print("בדיקת מערכת התראות טלגרם - Polymarket")
    print("=" * 60)
    
    results = {
        'telegram_connection': False,
        'test_message': False,
        'wallet_activity': False
    }
    
    # בדיקת חיבור
    results['telegram_connection'] = test_telegram_connection()
    
    if results['telegram_connection']:
        # שליחת הודעת בדיקה
        results['test_message'] = send_test_message()
    
    # בדיקת פעילות
    results['wallet_activity'] = test_wallet_activity()
    
    # סיכום
    print("\n" + "=" * 60)
    print("סיכום בדיקות")
    print("=" * 60)
    
    print(f"\n{'✅' if results['telegram_connection'] else '❌'} חיבור לבוט טלגרם")
    print(f"{'✅' if results['test_message'] else '❌'} שליחת הודעת בדיקה")
    print(f"{'✅' if results['wallet_activity'] else '❌'} בדיקת פעילות הארנק")
    
    if all(results.values()):
        print("\n🎉 הכל תקין! המערכת מוכנה לעבודה")
        print("\n💡 להפעלת מעקב רציף, הרץ:")
        print("   python telegram_monitor.py")
    else:
        print("\n⚠️ יש בעיות שצריך לפתור")
        if not results['telegram_connection']:
            print("   - בדוק את TELEGRAM_BOT_TOKEN")
        if not results['test_message']:
            print("   - בדוק את TELEGRAM_CHAT_ID")
            print("   - ודא ששלחת הודעה לבוט לפחות פעם אחת")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
