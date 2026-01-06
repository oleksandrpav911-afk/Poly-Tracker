"""
ניתוח מפורט של ארנק ב-Polymarket
"""

import json
import sys
from collections import Counter
from datetime import datetime

# תיקון encoding ל-Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WALLET_ADDRESS = "0x16b29c50f2439faf627209b2ac0c7bbddaa8a881"
DATA_FILE = f"wallet_{WALLET_ADDRESS[:10]}_data.json"

def load_data():
    """טעינת נתונים מקובץ"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"קובץ {DATA_FILE} לא נמצא. הרץ קודם את quick_track.py")
        return None

def analyze_trades(data):
    """ניתוח מפורט של עסקאות"""
    activities = data.get('activities', [])
    trades = [a for a in activities if a.get('type') == 'TRADE']
    
    if not trades:
        print("לא נמצאו עסקאות")
        return
    
    print(f"\nסה\"כ עסקאות: {len(trades)}")
    
    # ניתוח לפי תוצאות
    outcomes = Counter([t.get('outcome', 'Unknown') for t in trades])
    print(f"\nעסקאות לפי תוצאה:")
    for outcome, count in outcomes.most_common():
        print(f"  {outcome}: {count}")
    
    # ניתוח לפי מחירים
    prices = [float(t.get('price', 0)) for t in trades if t.get('price')]
    if prices:
        print(f"\nמחירים:")
        print(f"  ממוצע: {sum(prices)/len(prices):.4f}")
        print(f"  מינימום: {min(prices):.4f}")
        print(f"  מקסימום: {max(prices):.4f}")
    
    # ניתוח לפי גודל
    sizes = [float(t.get('size', 0)) for t in trades if t.get('size')]
    if sizes:
        total_volume = sum(sizes)
        print(f"\nנפח מסחר:")
        print(f"  סה\"כ: {total_volume:.2f}")
        print(f"  ממוצע לעסקה: {total_volume/len(sizes):.2f}")
        print(f"  עסקה קטנה ביותר: {min(sizes):.2f}")
        print(f"  עסקה גדולה ביותר: {max(sizes):.2f}")
    
    # ניתוח לפי זמן
    timestamps = []
    for t in trades:
        ts = t.get('timestamp')
        if ts:
            if isinstance(ts, (int, float)):
                dt = datetime.fromtimestamp(ts / 1000) if ts > 1e10 else datetime.fromtimestamp(ts)
                timestamps.append(dt)
    
    if timestamps:
        timestamps.sort()
        print(f"\nטווח זמן:")
        print(f"  עסקה ראשונה: {timestamps[0].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  עסקה אחרונה: {timestamps[-1].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  טווח: {(timestamps[-1] - timestamps[0]).days} ימים")

def main():
    print("=" * 60)
    print("ניתוח מפורט - ארנק ב-Polymarket")
    print("=" * 60)
    print(f"\nכתובת ארנק: {WALLET_ADDRESS}\n")
    
    data = load_data()
    if not data:
        return
    
    print(f"סה\"כ פעילויות: {data.get('total_activities', 0)}")
    print(f"נוצר ב: {data.get('timestamp', 'N/A')}")
    
    analyze_trades(data)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
