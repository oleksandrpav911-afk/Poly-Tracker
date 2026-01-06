"""
מעקב אוטומטי אחר ארנק ב-Polymarket
הסקריפט רץ ברקע ומעדכן נתונים באופן אוטומטי
"""

import requests
import json
import time
import schedule
from datetime import datetime
import sys
import os

# תיקון encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WALLET_ADDRESS = "0x16b29c50f2439faf627209b2ac0c7bbddaa8a881"
DATA_API_BASE = "https://data-api.polymarket.com"
DATA_DIR = "tracking_data"

def ensure_data_dir():
    """וידוא שתיקיית הנתונים קיימת"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_user_activity(wallet_address):
    """קבלת פעילות משתמש"""
    try:
        url = f"{DATA_API_BASE}/activity"
        params = {'user': wallet_address}
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        
        response = session.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ שגיאה: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ שגיאה בקבלת נתונים: {e}")
        return []

def save_snapshot(wallet_address, activities):
    """שמירת snapshot של הנתונים"""
    ensure_data_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(DATA_DIR, f"snapshot_{wallet_address[:10]}_{timestamp}.json")
    
    data = {
        'wallet_address': wallet_address,
        'timestamp': datetime.now().isoformat(),
        'total_activities': len(activities),
        'activities': activities
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Snapshot נשמר: {filename}")
    return filename

def track_wallet():
    """פונקציה למעקב אחר הארנק"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] מעקב אחר {WALLET_ADDRESS}...")
    
    activities = get_user_activity(WALLET_ADDRESS)
    
    if activities:
        print(f"✓ נמצאו {len(activities)} פעילויות")
        
        # שמירת snapshot
        save_snapshot(WALLET_ADDRESS, activities)
        
        # חישוב סטטיסטיקות מהירות
        trades = [a for a in activities if a.get('type') == 'TRADE']
        total_volume = sum(float(a.get('size', 0)) for a in trades if a.get('size'))
        
        print(f"  - עסקאות: {len(trades)}")
        print(f"  - נפח מסחר: {total_volume:,.2f}")
    else:
        print("⚠️ לא נמצאו פעילויות")

def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("מעקב אוטומטי אחר ארנק ב-Polymarket")
    print("=" * 60)
    print(f"\nכתובת ארנק: {WALLET_ADDRESS}")
    print("\nהגדרות מעקב:")
    print("  - עדכון כל שעה")
    print(f"  - נתונים נשמרים ב-{DATA_DIR}/")
    print("\nלעצירה: Ctrl+C")
    print("=" * 60)
    
    # הרצה ראשונית
    track_wallet()
    
    # הגדרת לוח זמנים
    schedule.every(1).hours.do(track_wallet)
    
    # הרצה רציפה
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # בדיקה כל דקה
    except KeyboardInterrupt:
        print("\n\n⏹️ מעקב הופסק")

if __name__ == "__main__":
    main()
