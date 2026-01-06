"""
מעקב אחר שינויים בפוזיציות ושליחת התראות
"""

import json
import os
import sys
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# תיקון encoding - רק אם stdout פתוח
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        import io
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# ייבוא פונקציות
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_notifier import TelegramNotifier, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, get_user_activity, WALLET_ADDRESS as WALLET_ADDR
from collections import Counter

WALLET_ADDRESS = WALLET_ADDR

# העתקת פונקציות נדרשות מ-dashboard (ללא streamlit)
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

def calculate_current_positions(df):
    """חישוב פוזיציות נוכחיות"""
    if df.empty or 'conditionId' not in df.columns:
        return pd.DataFrame()
    
    trades_df = df[df['type'] == 'TRADE'].copy()
    if trades_df.empty:
        return pd.DataFrame()
    
    trades_df['position_key'] = trades_df['conditionId'].astype(str) + '_' + trades_df['outcomeIndex'].astype(str)
    positions = []
    
    for key, group in trades_df.groupby('position_key'):
        buy_size = group[group['side'] == 'BUY']['size'].sum()
        sell_size = group[group['side'] == 'SELL']['size'].sum()
        net_position = buy_size - sell_size
        
        if abs(net_position) > 0.01:
            buy_trades = group[group['side'] == 'BUY']
            avg_buy_price = buy_trades['price'].mean() if not buy_trades.empty and 'price' in buy_trades.columns else 0
            sell_trades = group[group['side'] == 'SELL']
            avg_sell_price = sell_trades['price'].mean() if not sell_trades.empty and 'price' in sell_trades.columns else 0
            current_price = group['price'].iloc[-1] if 'price' in group.columns else avg_buy_price
            total_buy_usdc = buy_trades['usdcSize'].sum() if 'usdcSize' in buy_trades.columns else 0
            total_sell_usdc = sell_trades['usdcSize'].sum() if 'usdcSize' in sell_trades.columns else 0
            
            first_row = group.iloc[0]
            decimal_odds_buy = 1 / avg_buy_price if avg_buy_price > 0 else 0
            decimal_odds_current = 1 / current_price if current_price > 0 else 0
            
            positions.append({
                'conditionId': first_row.get('conditionId', ''),
                'outcomeIndex': first_row.get('outcomeIndex', ''),
                'title': first_row.get('title', 'N/A'),
                'outcome': first_row.get('outcome', 'N/A'),
                'sport_type': first_row.get('sport_type', 'Unknown'),
                'total_invested_usdc': total_buy_usdc,
                'net_position': net_position,
                'avg_buy_price': avg_buy_price,
                'decimal_odds_buy': decimal_odds_buy,
                'current_price': current_price,
                'decimal_odds_current': decimal_odds_current,
                'last_trade_time': group['datetime'].max() if 'datetime' in group.columns else None,
            })
    
    positions_df = pd.DataFrame(positions)
    if not positions_df.empty:
        positions_df = positions_df.sort_values('net_position', key=abs, ascending=False)
    return positions_df

def process_activities(activities):
    """עיבוד פעילויות לנתונים נוחים"""
    if not activities:
        return pd.DataFrame(), {}, pd.DataFrame()
    
    df = pd.DataFrame(activities)
    
    if 'slug' in df.columns or 'eventSlug' in df.columns or 'title' in df.columns:
        df['sport_type'] = df.apply(
            lambda row: detect_sport_type(
                row.get('slug', ''),
                row.get('eventSlug', ''),
                row.get('title', '')
            ),
            axis=1
        )
    
    if 'timestamp' in df.columns:
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
    
    if 'size' in df.columns:
        df['size'] = pd.to_numeric(df['size'], errors='coerce')
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    if 'usdcSize' in df.columns:
        df['usdcSize'] = pd.to_numeric(df['usdcSize'], errors='coerce')
    
    positions_df = calculate_current_positions(df)
    
    stats = {
        'total_trades': len(df),
        'total_volume': df['size'].sum() if 'size' in df.columns else 0,
        'total_usdc': df['usdcSize'].sum() if 'usdcSize' in df.columns else 0,
        'avg_price': df['price'].mean() if 'price' in df.columns else 0,
        'outcomes': dict(Counter(df['outcome'].dropna())) if 'outcome' in df.columns else {},
        'sports': dict(Counter(df['sport_type'].dropna())) if 'sport_type' in df.columns else {},
        'total_positions': len(positions_df) if not positions_df.empty else 0,
        'total_position_value': positions_df['net_position'].abs().sum() if not positions_df.empty else 0,
    }
    
    return df, stats, positions_df

# הגדרות
WALLET_ADDRESS = "0x16b29c50f2439faf627209b2ac0c7bbddaa8a881"
POSITIONS_FILE = "positions_snapshot.json"
MIN_POSITION_VALUE_USDC = 5000  # סכום מינימלי לפוזיציה להתראה
ALLOWED_SPORTS = ["NBA", "Soccer"]  # סוגי ספורט למעקב

class PositionTracker:
    """מעקב אחר שינויים בפוזיציות"""
    
    def __init__(self):
        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID) if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else None
        self.positions_file = POSITIONS_FILE
    
    def load_previous_positions(self) -> Dict:
        """טעינת פוזיציות קודמות"""
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_positions(self, positions_df, timestamp: str):
        """שמירת פוזיציות נוכחיות"""
        positions_dict = {}
        if not positions_df.empty:
            for _, row in positions_df.iterrows():
                key = f"{row.get('conditionId', '')}_{row.get('outcomeIndex', '')}"
                positions_dict[key] = {
                    'conditionId': row.get('conditionId', ''),
                    'outcomeIndex': row.get('outcomeIndex', ''),
                    'title': row.get('title', 'N/A'),
                    'outcome': row.get('outcome', 'N/A'),
                    'sport_type': row.get('sport_type', 'Unknown'),
                    'net_position': float(row.get('net_position', 0)),
                    'total_invested_usdc': float(row.get('total_invested_usdc', 0)),
                    'current_price': float(row.get('current_price', 0)),
                    'avg_buy_price': float(row.get('avg_buy_price', 0)),
                    'decimal_odds_buy': float(row.get('decimal_odds_buy', 0)),
                }
        
        data = {
            'timestamp': timestamp,
            'positions': positions_dict
        }
        
        with open(self.positions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def format_position_change_message(self, change_type: str, position: Dict, old_position: Optional[Dict] = None) -> str:
        """פורמט הודעה על שינוי בפוזיציה"""
        title = position.get('title', 'N/A')
        outcome = position.get('outcome', 'N/A')
        sport_type = position.get('sport_type', 'Unknown')
        net_position = position.get('net_position', 0)
        invested = position.get('total_invested_usdc', 0)
        avg_buy_price = position.get('avg_buy_price', 0)
        # שימוש ב-decimal_odds_buy (היחס שבו קנה) - אם יש ישירות, אחרת מחשבים
        decimal_odds = position.get('decimal_odds_buy', 0)
        if decimal_odds == 0 and avg_buy_price > 0:
            decimal_odds = 1 / avg_buy_price
        
        if change_type == 'new':
            emoji = "🆕"
            change_text = "פוזיציה חדשה"
        elif change_type == 'closed':
            emoji = "🔒"
            change_text = "פוזיציה נסגרה"
        elif change_type == 'increased':
            emoji = "📈"
            change_text = "פוזיציה גדלה"
            if old_position:
                old_invested = old_position.get('total_invested_usdc', 0)
                change_amount = invested - old_invested
                change_text += f" (+${change_amount:,.0f})"
        elif change_type == 'decreased':
            emoji = "📉"
            change_text = "פוזיציה קטנה"
            if old_position:
                old_invested = old_position.get('total_invested_usdc', 0)
                change_amount = old_invested - invested
                change_text += f" (-${change_amount:,.0f})"
        else:
            emoji = "📊"
            change_text = "שינוי בפוזיציה"
        
        message = f"""
{emoji} <b>{change_text} - {sport_type}</b>

📊 <b>{title}</b>
🎯 Bet: {outcome}
💰 ${int(round(invested)):,}
📊 Odds: {decimal_odds:.3f}

⏰ זמן: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 ארנק: SeriouslySirius
"""
        return message.strip()
    
    def detect_significant_changes(self, current_positions: Dict, previous_positions: Dict) -> List[Dict]:
        """זיהוי שינויים משמעותיים בפוזיציות - מעקב אחר פוזיציות מעל $5,000"""
        changes = []
        threshold = MIN_POSITION_VALUE_USDC
        
        # יצירת sets של מפתחות
        current_keys = set(current_positions.keys())
        previous_keys = set(previous_positions.get('positions', {}).keys())
        
        # פוזיציות חדשות מעל $5,000
        new_keys = current_keys - previous_keys
        for key in new_keys:
            pos = current_positions[key]
            sport_type = pos.get('sport_type', 'Unknown')
            if pos['total_invested_usdc'] >= threshold and sport_type in ALLOWED_SPORTS:
                changes.append({
                    'type': 'new_above_threshold',
                    'position': pos,
                    'old_position': None
                })
        
        # פוזיציות שנסגרו (שהיו מעל $5,000)
        closed_keys = previous_keys - current_keys
        for key in closed_keys:
            old_pos = previous_positions['positions'][key]
            sport_type = old_pos.get('sport_type', 'Unknown')
            if old_pos.get('total_invested_usdc', 0) >= threshold and sport_type in ALLOWED_SPORTS:
                changes.append({
                    'type': 'closed',
                    'position': old_pos,
                    'old_position': None
                })
        
        # שינויים בפוזיציות קיימות
        common_keys = current_keys & previous_keys
        for key in common_keys:
            current_pos = current_positions[key]
            old_pos = previous_positions['positions'][key]
            
            current_invested = current_pos['total_invested_usdc']
            old_invested = old_pos.get('total_invested_usdc', 0)
            
            current_above = current_invested >= threshold
            old_above = old_invested >= threshold
            
            # סינון לפי סוג ספורט
            sport_type = current_pos.get('sport_type', 'Unknown')
            if sport_type not in ALLOWED_SPORTS:
                continue
            
            # מעבר מעל $5,000 (היה מתחת, עכשיו מעל)
            if not old_above and current_above:
                changes.append({
                    'type': 'crossed_above',
                    'position': current_pos,
                    'old_position': old_pos
                })
            # מעבר מתחת $5,000 (היה מעל, עכשיו מתחת)
            elif old_above and not current_above:
                changes.append({
                    'type': 'crossed_below',
                    'position': current_pos,
                    'old_position': old_pos
                })
            # עדכון בפוזיציה שכבר מעל $5,000 (גם לפני וגם עכשיו)
            elif old_above and current_above:
                # רק אם יש שינוי משמעותי של לפחות $5,000
                invested_change = abs(current_invested - old_invested)
                if invested_change >= 5000:  # שינוי של לפחות $5,000
                    changes.append({
                        'type': 'updated_above',
                        'position': current_pos,
                        'old_position': old_pos
                    })
        
        return changes
    
    def check_and_notify(self):
        """בדיקת שינויים ושליחת התראות"""
        print("🔍 בודק שינויים בפוזיציות...")
        
        # טעינת פוזיציות קודמות
        previous_positions = self.load_previous_positions()
        
        # קבלת פעילות נוכחית
        activities = get_user_activity(WALLET_ADDRESS)
        if not activities:
            print("לא נמצאו פעילויות")
            return
        
        # עיבוד נתונים
        df, stats, positions_df = process_activities(activities)
        
        # המרת פוזיציות ל-dict
        current_positions = {}
        if not positions_df.empty:
            for _, row in positions_df.iterrows():
                key = f"{row.get('conditionId', '')}_{row.get('outcomeIndex', '')}"
                current_positions[key] = {
                    'conditionId': row.get('conditionId', ''),
                    'outcomeIndex': row.get('outcomeIndex', ''),
                    'title': row.get('title', 'N/A'),
                    'outcome': row.get('outcome', 'N/A'),
                    'sport_type': row.get('sport_type', 'Unknown'),
                    'net_position': float(row.get('net_position', 0)),
                    'total_invested_usdc': float(row.get('total_invested_usdc', 0)),
                    'current_price': float(row.get('current_price', 0)),
                    'avg_buy_price': float(row.get('avg_buy_price', 0)),
                    'decimal_odds_buy': float(row.get('decimal_odds_buy', 0)),
                }
        
        # זיהוי שינויים
        if previous_positions:
            changes = self.detect_significant_changes(current_positions, previous_positions)
            
            if changes:
                print(f"✓ נמצאו {len(changes)} שינויים משמעותיים")
                
                # שליחת התראות
                if self.notifier:
                    sent_count = 0
                    for i, change in enumerate(changes, 1):
                        message = self.format_position_change_message(
                            change['type'],
                            change['position'],
                            change['old_position']
                        )
                        result = self.notifier.send_message(message)
                        if result:
                            sent_count += 1
                            print(f"  ✓ נשלחה הודעה {i}/{len(changes)}")
                        else:
                            print(f"  ❌ שגיאה בשליחת הודעה {i}/{len(changes)}")
                        import time
                        time.sleep(0.5)  # מניעת spam
                    print(f"✓ סה\"כ נשלחו {sent_count}/{len(changes)} התראות")
                else:
                    print("⚠️ טלגרם לא מוגדר - לא נשלחו התראות")
            else:
                print("אין שינויים משמעותיים")
        else:
            print("אין פוזיציות קודמות - זהו הריצה הראשונה")
            # בפעם הראשונה - שליחת כל הפוזיציות מעל $5,000 (רק NBA ו-Soccer)
            threshold = MIN_POSITION_VALUE_USDC
            positions_above_threshold = [
                pos for pos in current_positions.values() 
                if pos['total_invested_usdc'] >= threshold and pos.get('sport_type', 'Unknown') in ALLOWED_SPORTS
            ]
            
            if positions_above_threshold:
                print(f"✓ נמצאו {len(positions_above_threshold)} פוזיציות מעל ${threshold:,}")
                
                if self.notifier:
                    sent_count = 0
                    for i, pos in enumerate(positions_above_threshold, 1):
                        message = self.format_position_change_message(
                            'new_above_threshold',
                            pos,
                            None
                        )
                        result = self.notifier.send_message(message)
                        if result:
                            sent_count += 1
                            print(f"  ✓ נשלחה הודעה {i}/{len(positions_above_threshold)}")
                        else:
                            print(f"  ❌ שגיאה בשליחת הודעה {i}/{len(positions_above_threshold)}")
                        import time
                        time.sleep(0.5)  # מניעת spam
                    print(f"✓ סה\"כ נשלחו {sent_count}/{len(positions_above_threshold)} התראות")
                else:
                    print("⚠️ טלגרם לא מוגדר - לא נשלחו התראות")
        
        # שמירת פוזיציות נוכחיות
        timestamp = datetime.now().isoformat()
        self.save_positions(positions_df, timestamp)
        print(f"✓ פוזיציות נשמרו")

def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("מעקב אחר שינויים בפוזיציות")
    print("=" * 60)
    print(f"\nכתובת ארנק: {WALLET_ADDRESS}")
    print(f"סף מינימלי: ${MIN_POSITION_VALUE_USDC:,}")
    print(f"סוגי ספורט: {', '.join(ALLOWED_SPORTS)}")
    print("=" * 60)
    
    tracker = PositionTracker()
    tracker.check_and_notify()
    
    print("\n✓ סיום בדיקה")

if __name__ == "__main__":
    main()
