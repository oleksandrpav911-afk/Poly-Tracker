"""
סקריפט מהיר למעקב אחר ארנק ב-Polymarket
"""

import requests
import json
import sys
from datetime import datetime

# תיקון encoding ל-Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# כתובת הארנק למעקב
WALLET_ADDRESS = "0x16b29c50f2439faf627209b2ac0c7bbddaa8a881"
DATA_API_BASE = "https://data-api.polymarket.com"

def get_user_activity(wallet_address):
    """קבלת פעילות משתמש דרך Polymarket Data API"""
    try:
        url = f"{DATA_API_BASE}/activity"
        params = {'user': wallet_address}
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        
        print(f"מביא נתונים עבור {wallet_address}...")
        response = session.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            activity_data = response.json()
            print(f"✓ התקבלו {len(activity_data)} פעילויות\n")
            return activity_data
        else:
            print(f"⚠️ שגיאה: {response.status_code}")
            if response.status_code == 404:
                print("  משתמש לא נמצא או אין פעילות")
            else:
                print(f"  תגובה: {response.text[:200]}")
            return []
    except Exception as e:
        print(f"שגיאה: {e}")
        return []

def analyze_activity(activity_data):
    """ניתוח פעילות"""
    if not activity_data:
        return {}
    
    activity_types = {}
    markets = set()
    total_volume = 0
    
    for act in activity_data:
        act_type = act.get('type', 'unknown')
        activity_types[act_type] = activity_types.get(act_type, 0) + 1
        
        if 'market' in act:
            markets.add(act.get('market', 'unknown'))
        
        if 'size' in act:
            try:
                total_volume += float(act['size'])
            except:
                pass
    
    return {
        'total_activities': len(activity_data),
        'activity_types': activity_types,
        'markets_count': len(markets),
        'total_volume': total_volume
    }

def main():
    print("=" * 60)
    print("מעקב אחר ארנק ב-Polymarket")
    print("=" * 60)
    print(f"\nכתובת ארנק: {WALLET_ADDRESS}\n")
    
    # קבלת פעילות
    activity = get_user_activity(WALLET_ADDRESS)
    
    if activity:
        print("=" * 60)
        print("10 פעילויות אחרונות:")
        print("=" * 60)
        
        for i, act in enumerate(activity[:10], 1):
            print(f"\n{i}. סוג: {act.get('type', 'N/A')}")
            if 'timestamp' in act:
                ts = act['timestamp']
                if isinstance(ts, (int, float)):
                    dt = datetime.fromtimestamp(ts / 1000) if ts > 1e10 else datetime.fromtimestamp(ts)
                    print(f"   זמן: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"   זמן: {ts}")
            if 'market' in act:
                print(f"   שוק: {act.get('market', 'N/A')}")
            if 'size' in act:
                print(f"   גודל: {act.get('size', 'N/A')}")
            if 'price' in act:
                print(f"   מחיר: {act.get('price', 'N/A')}")
            if 'outcome' in act:
                print(f"   תוצאה: {act.get('outcome', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("ניתוח:")
        print("=" * 60)
        
        analysis = analyze_activity(activity)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        
        # שמירת נתונים
        filename = f"wallet_{WALLET_ADDRESS[:10]}_data.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'wallet_address': WALLET_ADDRESS,
                'timestamp': datetime.now().isoformat(),
                'total_activities': len(activity),
                'activities': activity,
                'analysis': analysis
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ נתונים נשמרו ב-{filename}")
    else:
        print("\nלא נמצאו פעילויות")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
