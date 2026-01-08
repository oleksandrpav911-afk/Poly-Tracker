"""
מערכת התראות בטלגרם למעקב אחר עסקאות ב-Polymarket
"""

import requests
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
import sys

# תיקון encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# רשימת ארנקים למעקב - ניתן להוסיף עוד ארנקים כאן
# פורמט: {'address': '0x...', 'name': 'שם הארנק'}
WALLETS = [
    {
        'address': '0x16b29c50f2439faf627209b2ac0c7bbddaa8a881',
        'name': 'SeriouslySirius'
    },
    {
        'address': '0x1bc0d88ca86b9049cf05d642e634836d5ddf4429',
        'name': '21212121'
    },
    {
        'address': '0x2c335066fe58fe9237c3d3dc7b275c2a034a0563',
        'name': '0x2c33'
    },
    {
        'address': '0x03524d9d00cffe5004d1d270edfea7b3109e3292',
        'name': 'Woyaofadacaila'
    },
    {
        'address': '0x9cb990f1862568a63d8601efeebe0304225c32f2',
        'name': 'jtwyslljy'
    },
    {
        'address': '0xe74a4446efd66a4de690962938f550d8921a40ee',
        'name': '0xe74A44'
    },
    {
        'address': '0x006cc834cc092684f1b56626e23bedb3835c16ea',
        'name': '0x006cc'
    },
]

# שמירת תאימות לאחור - הארנק הראשון
WALLET_ADDRESS = WALLETS[0]['address'] if WALLETS else ""
DATA_API_BASE = "https://data-api.polymarket.com"

# הגדרות טלגרם
TELEGRAM_BOT_TOKEN = "8577054844:AAEGWiSGPzJTA3Kt0ndwgelEK16iNU2G6yI"
TELEGRAM_CHAT_ID = "-5278382002"

# הגדרות סינון
MIN_TRADE_SIZE_USDC = 1500  # סכום מינימלי בדולרים להתראה
ALLOWED_SPORTS = ["NBA", "Soccer"]  # סוגי ספורט למעקב

def detect_sport_type(slug, event_slug, title):
    """זיהוי סוג ספורט מה-slug או title"""
    text = f"{slug or ''} {event_slug or ''} {title or ''}".lower()
    original_text = f"{slug or ''} {event_slug or ''} {title or ''}"  # שמירת טקסט מקורי לבדיקות רגישות לאותיות
    
    # בדיקה ספציפית לכדורגל - קודם כל
    soccer_keywords = [
        'soccer', 'premier league', 'champions league', 'mls', 'la liga', 'serie a', 
        'bundesliga', 'ligue 1', 'epl', 'uefa', 'fifa', 'world cup', 'euro',
        'manchester', 'liverpool', 'chelsea', 'arsenal', 'barcelona', 'real madrid',
        'psg', 'bayern', 'juventus', 'milan', 'inter', 'football match',
        'west bromwich', 'leicester', 'city fc', 'united', 'tottenham', 'newcastle',
        'will.*win', 'will.*fc', 'fc win', 'football club'
    ]
    
    for keyword in soccer_keywords:
        if keyword in text:
            return 'Soccer'
    
    # זיהוי "SC" (Soccer Club) - כמו "Pisa SC", "Como 1907"
    if re.search(r'\b\w+\s+sc\b', original_text, re.IGNORECASE):
        return 'Soccer'
    
    # זיהוי "vs." עם שמות קבוצות - נפוץ בכדורגל
    if ' vs. ' in original_text or ' vs ' in original_text.lower():
        # אם יש "vs" ולא NBA/NFL/NHL/MLB, כנראה כדורגל
        if 'nba' not in text and 'nfl' not in text and 'nhl' not in text and 'mlb' not in text:
            # בדיקה אם יש "O/U" או "Over/Under" - נפוץ בכדורגל
            if 'o/u' in text or 'over/under' in text or 'over' in text or 'under' in text:
                return 'Soccer'
            # בדיקה אם יש שמות קבוצות עם מספרים (כמו "Como 1907")
            if re.search(r'\b\w+\s+\d{4}\b', original_text):
                return 'Soccer'
            # בדיקה אם יש "SC" או "FC" בשם
            if re.search(r'\b\w+\s+(sc|fc)\b', original_text, re.IGNORECASE):
                return 'Soccer'
    
    # זיהוי "Will [שם קבוצה] win" - דפוס נפוץ בכדורגל
    if re.search(r'will\s+\w+.*win', text):
        # בדיקה אם זה לא NBA/NFL
        if 'nba' not in text and 'nfl' not in text and 'nhl' not in text:
            return 'Soccer'
    
    # זיהוי קבוצות איטלקיות נפוצות
    italian_teams = ['como', 'pisa', 'roma', 'napoli', 'atalanta', 'lazio', 'fiorentina', 
                     'torino', 'bologna', 'genoa', 'sampdoria', 'udinese', 'verona', 'empoli']
    for team in italian_teams:
        if team in text:
            return 'Soccer'
    
    if ('football' in text or ' fc' in text or 'fc ' in text) and 'nfl' not in text and 'american' not in text and 'college' not in text:
        return 'Soccer'
    
    sport_keywords = {
        'NBA': ['nba', 'basketball'],
        'NFL': ['nfl', 'american football'],
        'NHL': ['nhl', 'hockey'],
        'MLB': ['mlb', 'baseball'],
        'Tennis': ['tennis', 'atp', 'wta'],
        'Golf': ['golf', 'pga'],
        'UFC': ['ufc', 'mma'],
        'Boxing': ['boxing'],
        'College Football': ['college football', 'ncaa football', 'cfb'],
        'College Basketball': ['college basketball', 'ncaa basketball', 'march madness'],
    }
    
    for sport, keywords in sport_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return sport
    
    return 'Other'

class TelegramNotifier:
    """מחלקה לשליחת התראות בטלגרם"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.processed_trades = set()  # מעקב אחר עסקאות שכבר נשלחו
    
    def send_message(self, text: str) -> bool:
        """שליחת הודעה בטלגרם"""
        if not self.bot_token or not self.chat_id:
            print("⚠️ טלגרם לא מוגדר - יש למלא TELEGRAM_BOT_TOKEN ו-TELEGRAM_CHAT_ID")
            return False
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"שגיאה בשליחת הודעה: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"שגיאה בשליחת הודעה: {e}")
            return False
    
    def format_trade_message(self, trade: Dict) -> str:
        """פורמט הודעה על עסקה"""
        side_emoji = "🟢" if trade.get('side') == 'BUY' else "🔴"
        side_text = "קנייה" if trade.get('side') == 'BUY' else "מכירה"
        
        title = trade.get('title', 'N/A')
        outcome = trade.get('outcome', 'N/A')
        price = trade.get('price', 0)
        usdc_size = trade.get('usdcSize', 0)
        event_slug = trade.get('eventSlug', '')
        slug = trade.get('slug', '')
        
        # חישוב decimal odds
        decimal_odds = 1 / price if price > 0 else 0
        
        # עיבוד כותרת - אם יש Spread, ננסה לחלץ את שתי הקבוצות
        display_title = title
        if 'Spread:' in title:
            # ננסה לחלץ את שתי הקבוצות מה-eventSlug או slug
            # דוגמה: "nba-tor-atl-2026-01-05" -> "Raptors vs. Hawks"
            # או: "nba-phx-hou-2026-01-05" -> "Suns vs. Rockets"
            if event_slug:
                # חילוץ קיצורי קבוצות מה-eventSlug
                parts = event_slug.split('-')
                if len(parts) >= 3:
                    # מחפש קיצורי קבוצות (tor, atl, phx, hou, וכו')
                    team_codes = []
                    for part in parts[1:]:  # מדלג על "nba"
                        if len(part) == 3 and part.isalpha():
                            team_codes.append(part)
                        elif len(part) > 3 and not part.isdigit():
                            # אם זה לא מספר, יכול להיות שם קבוצה
                            if part not in ['nba', 'nfl', 'nhl']:
                                team_codes.append(part)
                    
                    if len(team_codes) >= 2:
                        # מיפוי קיצורים לשמות קבוצות NBA
                        team_names = {
                            'tor': 'Raptors', 'atl': 'Hawks', 'phx': 'Suns', 'hou': 'Rockets',
                            'bos': 'Celtics', 'chi': 'Bulls', 'nyk': 'Knicks', 'det': 'Pistons',
                            'gsw': 'Warriors', 'lac': 'Clippers', 'min': 'Timberwolves', 'lak': 'Lakers',
                            'nyr': 'Rangers', 'utah': 'Utah', 'mia': 'Heat', 'mil': 'Bucks',
                            'phi': '76ers', 'was': 'Wizards', 'orl': 'Magic', 'cha': 'Hornets',
                            'ind': 'Pacers', 'cle': 'Cavaliers', 'den': 'Nuggets', 'por': 'Trail Blazers',
                            'okc': 'Thunder', 'dal': 'Mavericks', 'mem': 'Grizzlies', 'nop': 'Pelicans',
                            'sac': 'Kings', 'sas': 'Spurs'
                        }
                        team1 = team_names.get(team_codes[0].lower(), team_codes[0].upper())
                        team2 = team_names.get(team_codes[1].lower(), team_codes[1].upper())
                        # שמירת החלק של ה-Spread או O/U
                        spread_part = title.split(':', 1)[1].strip() if ':' in title else ''
                        display_title = f"{team1} vs. {team2}: {spread_part}" if spread_part else f"{team1} vs. {team2}"
        
        timestamp = trade.get('timestamp', 0)
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp)
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = str(timestamp)
        
        # עיגול הסכום למספר שלם
        rounded_amount = int(round(usdc_size))
        
        # זיהוי סוג ספורט
        sport_type = detect_sport_type(slug, event_slug, title)
        
        # זיהוי שם הארנק מהעסקה (אם יש)
        wallet_name = trade.get('wallet_name', 'SeriouslySirius')
        
        message = f"""
{side_emoji} <b>{side_text} - {sport_type}</b>

📊 <b>{display_title}</b>
🎯 Bet: {outcome}
💰 {rounded_amount:,}
📊 Odds: {decimal_odds:.3f}

⏰ זמן: {time_str}
🔗 ארנק: {wallet_name}
"""
        return message.strip()
    
    def should_notify(self, trade: Dict) -> bool:
        """בדיקה אם צריך לשלוח התראה"""
        # בדיקת סוג
        if trade.get('type') != 'TRADE':
            return False
        
        # זיהוי סוג ספורט
        sport_type = detect_sport_type(
            trade.get('slug', ''),
            trade.get('eventSlug', ''),
            trade.get('title', '')
        )
        
        # בדיקת ספורט - רק NBA ו-Soccer
        if sport_type not in ALLOWED_SPORTS:
            return False
        
        # בדיקת סכום
        usdc_size = float(trade.get('usdcSize', 0))
        if usdc_size < MIN_TRADE_SIZE_USDC:
            return False
        
        # בדיקה אם כבר נשלחה התראה על העסקה הזו
        # שימוש ב-wallet_address אם יש (לתמיכה במספר ארנקים)
        wallet_address = trade.get('wallet_address', '')
        if wallet_address:
            trade_id = f"{wallet_address}_{trade.get('transactionHash', '')}_{trade.get('timestamp', '')}"
        else:
            trade_id = f"{trade.get('transactionHash', '')}_{trade.get('timestamp', '')}"
        if trade_id in self.processed_trades:
            return False
        
        return True
    
    def process_new_trades(self, activities: List[Dict]) -> int:
        """עיבוד עסקאות חדשות ושליחת התראות"""
        notified_count = 0
        
        for activity in activities:
            if self.should_notify(activity):
                message = self.format_trade_message(activity)
                if self.send_message(message):
                    # שימוש ב-wallet_address אם יש (לתמיכה במספר ארנקים)
                    wallet_address = activity.get('wallet_address', '')
                    if wallet_address:
                        trade_id = f"{wallet_address}_{activity.get('transactionHash', '')}_{activity.get('timestamp', '')}"
                    else:
                        trade_id = f"{activity.get('transactionHash', '')}_{activity.get('timestamp', '')}"
                    self.processed_trades.add(trade_id)
                    notified_count += 1
                    time.sleep(0.5)  # מניעת spam
        
        return notified_count

def get_user_activity(wallet_address: str) -> List[Dict]:
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
            return []
    except Exception as e:
        print(f"שגיאה בקבלת נתונים: {e}")
        return []

def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("מערכת התראות טלגרם - Polymarket")
    print("=" * 60)
    print(f"\nכתובת ארנק: {WALLET_ADDRESS}")
    print(f"סוגי ספורט: {', '.join(ALLOWED_SPORTS)}")
    print(f"סכום מינימלי: ${MIN_TRADE_SIZE_USDC} USDC")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n⚠️ יש להגדיר טלגרם:")
        print("1. צור בוט בטלגרם דרך @BotFather")
        print("2. קבל את ה-BOT_TOKEN")
        print("3. קבל את ה-CHAT_ID (שלח הודעה ל-@userinfobot)")
        print("4. עדכן את TELEGRAM_BOT_TOKEN ו-TELEGRAM_CHAT_ID בקובץ")
        return
    
    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    print("\n🔍 בודק עסקאות חדשות...")
    activities = get_user_activity(WALLET_ADDRESS)
    
    if not activities:
        print("לא נמצאו פעילויות")
        return
    
    # מיון לפי זמן (החדשות ביותר ראשונות)
    activities.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # עיבוד עסקאות חדשות
    notified = notifier.process_new_trades(activities)
    
    print(f"\n✓ נשלחו {notified} התראות")

if __name__ == "__main__":
    main()
