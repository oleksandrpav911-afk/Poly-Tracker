"""
מעקב רציף עם התראות טלגרם
רץ ברקע ומעדכן על עסקאות חדשות
"""

import requests
import json
import time
import schedule
from datetime import datetime
from typing import List, Dict, Set
import sys
import os

# תיקון encoding - רק אם stdout פתוח
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# ייבוא מהקובץ הראשי
from telegram_notifier import TelegramNotifier, get_user_activity, WALLET_ADDRESS

# ייבוא ישירות מ-telegram_notifier (הערכים כבר מוגדרים שם)
import telegram_notifier
TELEGRAM_BOT_TOKEN = telegram_notifier.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = telegram_notifier.TELEGRAM_CHAT_ID
MIN_TRADE_SIZE_USDC = telegram_notifier.MIN_TRADE_SIZE_USDC
ALLOWED_SPORTS = telegram_notifier.ALLOWED_SPORTS

class TradeMonitor:
    """מעקב אחר עסקאות חדשות"""
    
    def __init__(self):
        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.last_check_time = datetime.now()
        self.processed_trade_ids: Set[str] = set()
        # קובץ למעקב משותף בין תהליכים
        self.processed_trades_file = "processed_trades.json"
        self._load_processed_trades()
    
    def _load_processed_trades(self):
        """טעינת עסקאות שכבר נשלחו מהקובץ"""
        try:
            if os.path.exists(self.processed_trades_file):
                with open(self.processed_trades_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_trade_ids = set(data.get('processed_trades', []))
        except Exception as e:
            print(f"שגיאה בטעינת עסקאות מעובדות: {e}")
    
    def _save_processed_trades(self):
        """שמירת עסקאות שכבר נשלחו לקובץ"""
        try:
            with open(self.processed_trades_file, 'w', encoding='utf-8') as f:
                json.dump({'processed_trades': list(self.processed_trade_ids)}, f, ensure_ascii=False)
        except Exception as e:
            print(f"שגיאה בשמירת עסקאות מעובדות: {e}")
    
    def check_new_trades(self):
        """בדיקת עסקאות חדשות"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] בודק עסקאות חדשות...")
        
        activities = get_user_activity(WALLET_ADDRESS)
        
        if not activities:
            print("לא נמצאו פעילויות")
            return
        
        # טעינה מחדש של העסקאות המעובדות (למקרה שתהליך אחר עדכן)
        self._load_processed_trades()
        
        # מיון לפי זמן
        activities.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # סינון רק עסקאות חדשות
        new_activities = []
        for activity in activities:
            trade_id = f"{activity.get('transactionHash', '')}_{activity.get('timestamp', '')}"
            if trade_id not in self.processed_trade_ids:
                new_activities.append(activity)
        
        if new_activities:
            print(f"נמצאו {len(new_activities)} עסקאות חדשות")
            
            # שליחת התראות
            notified = 0
            for activity in new_activities:
                trade_id = f"{activity.get('transactionHash', '')}_{activity.get('timestamp', '')}"
                
                # בדיקה כפולה - גם ב-notifier וגם כאן
                if self.notifier.should_notify(activity):
                    message = self.notifier.format_trade_message(activity)
                    if self.notifier.send_message(message):
                        # סימון כמעובד גם כאן וגם ב-notifier
                        self.processed_trade_ids.add(trade_id)
                        self.notifier.processed_trades.add(trade_id)
                        notified += 1
                        time.sleep(0.5)  # מניעת spam
            
            # שמירת העסקאות המעובדות
            if notified > 0:
                self._save_processed_trades()
            
            print(f"✓ נשלחו {notified} התראות")
        else:
            print("אין עסקאות חדשות")

def main():
    """פונקציה ראשית"""
    # בדיקה שתהליך אחר לא רץ
    lock_file = "telegram_monitor.lock"
    
    # בדיקה אם יש תהליך אחר שרץ
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            print(f"⚠️ אזהרה: נמצא קובץ lock (PID: {pid})")
            print("אם אתה בטוח שאין תהליך אחר שרץ, מחק את הקובץ: telegram_monitor.lock")
            print("אחרת, עצור את התהליך הקודם לפני הפעלה מחדש")
            # נמשיך בכל מקרה, אבל נדפיס אזהרה
        except:
            # אם יש בעיה בקריאת הקובץ, נסה להמשיך
            try:
                os.remove(lock_file)
            except:
                pass
    
    # יצירת lock file
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
    except:
        pass
    
    print("=" * 60)
    print("מעקב רציף עם התראות טלגרם")
    print("=" * 60)
    print(f"\nכתובת ארנק: {WALLET_ADDRESS}")
    print(f"סוגי ספורט: {', '.join(ALLOWED_SPORTS)}")
    print(f"סכום מינימלי: ${MIN_TRADE_SIZE_USDC} USDC")
    print(f"תדירות בדיקה: כל 5 דקות")
    print("\nלעצירה: Ctrl+C")
    print("=" * 60)
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n⚠️ יש להגדיר טלגרם:")
        print("1. צור בוט בטלגרם דרך @BotFather")
        print("2. קבל את ה-BOT_TOKEN")
        print("3. קבל את ה-CHAT_ID (שלח הודעה ל-@userinfobot)")
        print("4. הגדר משתני סביבה או עדכן בקובץ")
        print("\nאו הגדר משתני סביבה:")
        print("  set TELEGRAM_BOT_TOKEN=your_token")
        print("  set TELEGRAM_CHAT_ID=your_chat_id")
        # הסרת lock file
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except:
                pass
        return
    
    monitor = TradeMonitor()
    
    # בדיקה ראשונית
    monitor.check_new_trades()
    
    # הגדרת לוח זמנים - כל 5 דקות
    schedule.every(5).minutes.do(monitor.check_new_trades)
    
    # הרצה רציפה
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # בדיקה כל דקה
    except KeyboardInterrupt:
        print("\n\n⏹️ מעקב הופסק")
    finally:
        # הסרת lock file בעת יציאה
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except:
                pass

if __name__ == "__main__":
    main()
