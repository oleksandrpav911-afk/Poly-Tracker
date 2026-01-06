"""
מעקב רציף אחר שינויים בפוזיציות
רץ ברקע ומעדכן על שינויים משמעותיים
"""

import schedule
import time
from datetime import datetime
from position_tracker import PositionTracker
import sys

# תיקון encoding - רק אם stdout פתוח
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("מעקב רציף אחר שינויים בפוזיציות")
    print("=" * 60)
    print(f"\nכתובת ארנק: 0x16b29c50f2439faf627209b2ac0c7bbddaa8a881")
    print(f"תדירות בדיקה: כל 10 דקות")
    print("\nלעצירה: Ctrl+C")
    print("=" * 60)
    
    tracker = PositionTracker()
    
    # בדיקה ראשונית
    tracker.check_and_notify()
    
    # הגדרת לוח זמנים - כל 10 דקות
    schedule.every(10).minutes.do(tracker.check_and_notify)
    
    # הרצה רציפה
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # בדיקה כל דקה
    except KeyboardInterrupt:
        print("\n\n⏹️ מעקב הופסק")

if __name__ == "__main__":
    main()
