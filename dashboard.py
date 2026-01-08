"""
דשבורד אונליין למעקב אחר ארנק ב-Polymarket
"""

import streamlit as st
import requests
import json
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from collections import Counter

# הגדרת דף
st.set_page_config(
    page_title="Polymarket Wallet Tracker",
    page_icon="📊",
    layout="wide"
)

# ייבוא רשימת ארנקים מ-telegram_notifier.py (מקור אמת אחד)
from telegram_notifier import WALLETS

# שמירת תאימות לאחור - הארנק הראשון
WALLET_ADDRESS = WALLETS[0]['address'] if WALLETS else ""
DATA_API_BASE = "https://data-api.polymarket.com"

@st.cache_data(ttl=60)  # Cache לדקה אחת בלבד
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
        
        response = session.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"שגיאה בקבלת נתונים: {e}")
        return []

def detect_sport_type(slug, event_slug, title):
    """זיהוי סוג ספורט מה-slug או title"""
    text = f"{slug or ''} {event_slug or ''} {title or ''}".lower()
    original_text = f"{slug or ''} {event_slug or ''} {title or ''}"  # שמירת טקסט מקורי לבדיקות רגישות לאותיות
    
    # בדיקה ספציפית לכדורגל - קודם כל (לפני הכל)
    soccer_keywords = [
        'soccer', 'premier league', 'champions league', 'mls', 'la liga', 'serie a', 
        'bundesliga', 'ligue 1', 'epl', 'uefa', 'fifa', 'world cup', 'euro',
        'manchester', 'liverpool', 'chelsea', 'arsenal', 'barcelona', 'real madrid',
        'psg', 'bayern', 'juventus', 'milan', 'inter', 'football match',
        'west bromwich', 'leicester', 'city fc', 'united', 'tottenham', 'newcastle',
        'brighton', 'crystal palace', 'fulham', 'wolves', 'everton', 'burnley',
        'sheffield', 'norwich', 'watford', 'southampton', 'aston villa', 'leeds',
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
    
    # בדיקה נוספת - אם יש "football" או "fc" אבל לא "nfl" או "american", זה כנראה כדורגל
    if ('football' in text or ' fc' in text or 'fc ' in text) and 'nfl' not in text and 'american' not in text and 'college' not in text:
        return 'Soccer'
    
    # מיפוי סוגי ספורט אחרים
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
    
    # בדיקה לפי סדר עדיפות
    for sport, keywords in sport_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return sport
    
    return 'Other'

def calculate_current_positions(df):
    """חישוב פוזיציות נוכחיות - נטו לכל שוק ותוצאה"""
    if df.empty or 'conditionId' not in df.columns:
        return pd.DataFrame()
    
    # סינון רק עסקאות (TRADE)
    trades_df = df[df['type'] == 'TRADE'].copy()
    
    if trades_df.empty:
        return pd.DataFrame()
    
    # יצירת מפתח ייחודי: conditionId + outcomeIndex
    trades_df['position_key'] = trades_df['conditionId'].astype(str) + '_' + trades_df['outcomeIndex'].astype(str)
    
    # חישוב נטו לכל פוזיציה
    positions = []
    
    for key, group in trades_df.groupby('position_key'):
        # חישוב נטו: BUY - SELL
        buy_size = group[group['side'] == 'BUY']['size'].sum()
        sell_size = group[group['side'] == 'SELL']['size'].sum()
        net_position = buy_size - sell_size
        
        # רק פוזיציות שאינן 0
        if abs(net_position) > 0.01:  # threshold קטן לדיוק
            # ממוצע מחיר קנייה
            buy_trades = group[group['side'] == 'BUY']
            avg_buy_price = buy_trades['price'].mean() if not buy_trades.empty and 'price' in buy_trades.columns else 0
            
            # ממוצע מחיר מכירה
            sell_trades = group[group['side'] == 'SELL']
            avg_sell_price = sell_trades['price'].mean() if not sell_trades.empty and 'price' in sell_trades.columns else 0
            
            # ערך נוכחי (אם יש מחיר נוכחי)
            current_price = group['price'].iloc[-1] if 'price' in group.columns else avg_buy_price
            
            # P&L משוער (אם מכר חלקית)
            total_buy_usdc = buy_trades['usdcSize'].sum() if 'usdcSize' in buy_trades.columns else 0
            total_sell_usdc = sell_trades['usdcSize'].sum() if 'usdcSize' in sell_trades.columns else 0
            
            # נתונים מהשורה הראשונה של הקבוצה
            first_row = group.iloc[0]
            
            # חישוב decimal odds
            decimal_odds_buy = 1 / avg_buy_price if avg_buy_price > 0 else 0
            decimal_odds_current = 1 / current_price if current_price > 0 else 0
            
            positions.append({
                'conditionId': first_row.get('conditionId', ''),
                'outcomeIndex': first_row.get('outcomeIndex', ''),
                'title': first_row.get('title', 'N/A'),
                'outcome': first_row.get('outcome', 'N/A'),
                'sport_type': first_row.get('sport_type', 'Unknown'),
                'slug': first_row.get('slug', ''),
                'total_invested_usdc': total_buy_usdc,
                'net_position': net_position,
                'buy_size': buy_size,
                'sell_size': sell_size,
                'avg_buy_price': avg_buy_price,
                'decimal_odds_buy': decimal_odds_buy,
                'avg_sell_price': avg_sell_price,
                'current_price': current_price,
                'decimal_odds_current': decimal_odds_current,
                'total_sold_usdc': total_sell_usdc,
                'unrealized_pnl_usdc': (net_position * current_price * 100) - (net_position * avg_buy_price * 100) if net_position > 0 else 0,
                'last_trade_time': group['datetime'].max() if 'datetime' in group.columns else None,
            })
    
    positions_df = pd.DataFrame(positions)
    
    # מיון לפי נפח
    if not positions_df.empty:
        positions_df = positions_df.sort_values('net_position', key=abs, ascending=False)
    
    return positions_df

def process_activities(activities):
    """עיבוד פעילויות לנתונים נוחים"""
    if not activities:
        return pd.DataFrame(), {}, pd.DataFrame()
    
    # המרה ל-DataFrame
    df = pd.DataFrame(activities)
    
    # זיהוי סוג ספורט
    if 'slug' in df.columns or 'eventSlug' in df.columns or 'title' in df.columns:
        df['sport_type'] = df.apply(
            lambda row: detect_sport_type(
                row.get('slug', ''),
                row.get('eventSlug', ''),
                row.get('title', '')
            ),
            axis=1
        )
    
    # המרת timestamps - בדיקה אם זה milliseconds או seconds
    # והמרה ל-timezone מקומי (ישראל UTC+2)
    if 'timestamp' in df.columns:
        # בדיקה אם הטיימסטמפ הוא ב-milliseconds (יותר מ-1e10) או seconds
        sample_timestamp = df['timestamp'].iloc[0] if len(df) > 0 else 0
        if sample_timestamp > 1e10:
            # זה milliseconds - צריך לחלק ב-1000
            df['datetime'] = pd.to_datetime(df['timestamp'] / 1000, unit='s', errors='coerce', utc=True)
        else:
            # זה seconds
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce', utc=True)
        
        # המרה ל-timezone מקומי (ישראל UTC+2)
        # ישראל היא UTC+2 (או UTC+3 בקיץ, אבל pandas מטפל בזה אוטומטית)
        israel_offset = timedelta(hours=2)
        israel_tz = timezone(israel_offset)
        
        if df['datetime'].dt.tz is not None:
            # המרה מ-UTC לישראל
            df['datetime'] = df['datetime'].dt.tz_convert(israel_tz)
        else:
            # אם אין timezone, נניח שזה UTC ונמיר לישראל
            df['datetime'] = df['datetime'].dt.tz_localize(timezone.utc).dt.tz_convert(israel_tz)
        
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
    
    # חישוב ערכים
    if 'size' in df.columns:
        df['size'] = pd.to_numeric(df['size'], errors='coerce')
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    if 'usdcSize' in df.columns:
        df['usdcSize'] = pd.to_numeric(df['usdcSize'], errors='coerce')
    
    # חישוב פוזיציות נוכחיות
    positions_df = calculate_current_positions(df)
    
    # סטטיסטיקות
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

def main():
    st.title("📊 Polymarket Wallet Tracker")
    # Updated: 2026-01-06 - Added colors, filters, and UI improvements
    st.markdown("---")
    
    # בחירת ארנק
    if len(WALLETS) > 1:
        wallet_names = [f"{w['name']} ({w['address'][:10]}...)" for w in WALLETS]
        wallet_names.append("כל הארנקים")
        selected_wallet_idx = st.selectbox("בחר ארנק:", range(len(wallet_names)), format_func=lambda x: wallet_names[x])
        
        if selected_wallet_idx < len(WALLETS):
            # ארנק ספציפי
            selected_wallet = WALLETS[selected_wallet_idx]
            wallet_address = selected_wallet['address']
            wallet_name = selected_wallet['name']
            show_all = False
        else:
            # כל הארנקים
            wallet_address = None
            wallet_name = "כל הארנקים"
            show_all = True
    else:
        # רק ארנק אחד
        selected_wallet = WALLETS[0]
        wallet_address = selected_wallet['address']
        wallet_name = selected_wallet['name']
        show_all = False
    
    # הצגת כתובת הארנק
    col1, col2 = st.columns([3, 1])
    with col1:
        if show_all:
            st.markdown(f"**מעקב אחר {len(WALLETS)} ארנקים:**")
            for w in WALLETS:
                st.markdown(f"- `{w['address']}` ({w['name']})")
        else:
            st.markdown(f"**כתובת ארנק:** `{wallet_address}` ({wallet_name})")
    with col2:
        if st.button("🔄 רענון נתונים"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # טעינת נתונים
    with st.spinner("מביא נתונים..."):
        if show_all:
            # איסוף נתונים מכל הארנקים
            all_activities = []
            for wallet in WALLETS:
                wallet_activities = get_user_activity(wallet['address'])
                # הוספת שם הארנק לכל פעילות
                for activity in wallet_activities:
                    activity['wallet_name'] = wallet['name']
                    activity['wallet_address'] = wallet['address']
                all_activities.extend(wallet_activities)
            activities = all_activities
        else:
            activities = get_user_activity(wallet_address)
    
    if not activities:
        st.warning("לא נמצאו פעילויות עבור ארנק זה")
        return
    
    # עיבוד נתונים
    df, stats, positions_df = process_activities(activities)
    
    # כרטיסי סטטיסטיקה
    st.subheader("📈 סטטיסטיקות כלליות")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("סה\"כ עסקאות", f"{stats['total_trades']:,}")
    with col2:
        st.metric("נפח מסחר", f"{stats['total_volume']:,.2f}")
    with col3:
        st.metric("ערך USDC", f"${stats['total_usdc']:,.2f}")
    with col4:
        st.metric("פוזיציות פעילות", f"{stats['total_positions']:,}")
    with col5:
        st.metric("ערך פוזיציות", f"{stats['total_position_value']:,.2f}")
    
    st.markdown("---")
    
    # פוזיציות נוכחיות
    st.subheader("💼 פוזיציות נוכחיות")
    
    if not positions_df.empty:
        # סינון לפי סוג ספורט
        col1, col2 = st.columns(2)
        with col1:
            filter_sport_positions = st.selectbox(
                "סינון לפי סוג ספורט (פוזיציות)",
                ["הכל"] + sorted(positions_df['sport_type'].unique().tolist()),
                key="sport_filter_positions"
            )
        
        display_positions = positions_df.copy()
        if filter_sport_positions != "הכל":
            display_positions = display_positions[display_positions['sport_type'] == filter_sport_positions]
        
        # סינון רק פוזיציות עם total_invested_usdc מעל $500
        original_count = len(display_positions)
        if 'total_invested_usdc' in display_positions.columns:
            display_positions = display_positions[display_positions['total_invested_usdc'] > 500]
        
        # סינון רק פוזיציות עם last_trade_time מהיום
        before_date_filter = len(display_positions)
        if 'last_trade_time' in display_positions.columns:
            # קבלת תאריך היום (ישראל timezone)
            israel_offset = timedelta(hours=2)
            israel_tz = timezone(israel_offset)
            today = datetime.now(israel_tz).date()
            
            # סינון רק פוזיציות עם last_trade_time מהיום
            def is_today(trade_time):
                if pd.isna(trade_time):
                    return False
                try:
                    # המרה ל-timezone מקומי אם צריך
                    if isinstance(trade_time, pd.Timestamp):
                        if trade_time.tz is None:
                            local_time = trade_time.tz_localize(timezone.utc).tz_convert(israel_tz)
                        else:
                            local_time = trade_time.tz_convert(israel_tz)
                        return local_time.date() == today
                    else:
                        # אם זה datetime רגיל
                        if hasattr(trade_time, 'tzinfo') and trade_time.tzinfo is not None:
                            local_time = trade_time.astimezone(israel_tz)
                        else:
                            local_time = trade_time.replace(tzinfo=timezone.utc).astimezone(israel_tz)
                        return local_time.date() == today
                except:
                    return False
            
            display_positions = display_positions[display_positions['last_trade_time'].apply(is_today)]
        
        # הודעה אם יש סינון
        if original_count > len(display_positions):
            messages = []
            if before_date_filter > len(display_positions):
                messages.append(f"עם עסקאות מהיום")
            if original_count > before_date_filter:
                messages.append(f"עם השקעה מעל $500")
            
            filter_msg = " ו-".join(messages) if messages else ""
            st.info(f"📊 מוצגות רק פוזיציות {filter_msg} ({len(display_positions)} מתוך {original_count})")
        
        # הצגת סיכום
        if not display_positions.empty:
            total_net = display_positions['net_position'].sum()
            total_invested = display_positions['total_invested_usdc'].sum()
            total_sold = display_positions['total_sold_usdc'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("סה\"כ נטו", f"${int(round(total_net))}")
            with col2:
                st.metric("סה\"כ הושקע", f"${int(round(total_invested))}")
            with col3:
                st.metric("סה\"כ נמכר", f"${int(round(total_sold))}")
        
        # טבלת פוזיציות - סדר העמודות: title, outcome, sport_type, total_invested_usdc, net_position, avg_buy_price, decimal_odds_buy, current_price, decimal_odds_current, last_trade_time
        display_cols = ['title', 'outcome', 'sport_type', 'total_invested_usdc', 'net_position', 
                       'avg_buy_price', 'decimal_odds_buy', 'current_price', 'decimal_odds_current', 'last_trade_time']
        available_cols = [col for col in display_cols if col in display_positions.columns]
        
        display_positions_table = display_positions[available_cols].copy()
        
        # עיצוב ופורמט
        if 'net_position' in display_positions_table.columns:
            display_positions_table['net_position'] = display_positions_table['net_position'].apply(
                lambda x: f"${int(round(x))}" if pd.notna(x) else "$0"
            )
        
        if 'total_invested_usdc' in display_positions_table.columns:
            display_positions_table['total_invested_usdc'] = display_positions_table['total_invested_usdc'].apply(
                lambda x: f"${int(round(x))}" if pd.notna(x) else "$0"
            )
        
        if 'avg_buy_price' in display_positions_table.columns:
            display_positions_table['avg_buy_price'] = display_positions_table['avg_buy_price'].apply(
                lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%"
            )
        
        if 'current_price' in display_positions_table.columns:
            display_positions_table['current_price'] = display_positions_table['current_price'].apply(
                lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%"
            )
        
        if 'decimal_odds_buy' in display_positions_table.columns:
            display_positions_table['decimal_odds_buy'] = display_positions_table['decimal_odds_buy'].apply(
                lambda x: f"{x:.3f}" if pd.notna(x) and x > 0 else "N/A"
            )
        
        if 'decimal_odds_current' in display_positions_table.columns:
            display_positions_table['decimal_odds_current'] = display_positions_table['decimal_odds_current'].apply(
                lambda x: f"{x:.3f}" if pd.notna(x) and x > 0 else "N/A"
            )
        
        if 'last_trade_time' in display_positions_table.columns:
            display_positions_table['last_trade_time'] = display_positions_table['last_trade_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # הוספת styling - צבעי רקע
        def style_outcome(val):
            """צבע רקע לעמודת outcome"""
            if pd.isna(val):
                return ''
            val_str = str(val).upper()
            if val_str in ['OVER', 'YES']:
                return 'background-color: #90EE90; color: #000;'  # ירוק בהיר
            elif val_str in ['UNDER', 'NO']:
                return 'background-color: #FFB6C1; color: #000;'  # אדום בהיר
            return ''
        
        def style_sport_type(val):
            """צבע רקע לעמודת sport_type"""
            if pd.isna(val):
                return ''
            val_str = str(val).upper()
            if val_str == 'NHL':
                return 'background-color: #87CEEB; color: #000;'  # תכלת
            elif val_str == 'NBA':
                return 'background-color: #FFA500; color: #000;'  # כתום
            elif val_str == 'NFL':
                return 'background-color: #191970; color: #FFF;'  # כחול כהה
            elif val_str in ['SOCCER', 'FOOTBALL']:
                return 'background-color: #9370DB; color: #000;'  # סגול
            return ''
        
        # יצירת Styler
        styled_table = display_positions_table.style
        
        # החלת צבעים על עמודות
        if 'outcome' in display_positions_table.columns:
            styled_table = styled_table.applymap(style_outcome, subset=['outcome'])
        if 'sport_type' in display_positions_table.columns:
            styled_table = styled_table.applymap(style_sport_type, subset=['sport_type'])
        
        # הצגת הטבלה עם styling
        st.dataframe(
            styled_table,
            width='stretch',
            height=400,
            use_container_width=True
        )
        
        # הורדת פוזיציות
        csv_positions = display_positions.to_csv(index=False, encoding='utf-8-sig')
        wallet_id = wallet_name if not show_all else "all_wallets"
        st.download_button(
            label="📥 הורד פוזיציות CSV",
            data=csv_positions,
            file_name=f"positions_{wallet_id}.csv",
            mime="text/csv",
            key="download_positions"
        )
    else:
        st.info("אין פוזיציות פעילות כרגע")
    
    st.markdown("---")
    
    # טבלת עסקאות - Activity Feed
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.subheader("📋 Activity Feed")
    with col_header2:
        if st.button("🔄 רענון Activity Feed", key="refresh_activity"):
            st.cache_data.clear()
            st.rerun()
    
    # סינון
    col1, col2, col3 = st.columns(3)
    with col1:
        show_count = st.slider("מספר עסקאות להצגה", 10, 100, 20)
    with col2:
        filter_sport = st.selectbox("סינון לפי סוג ספורט", 
                                    ["הכל"] + sorted(list(stats.get('sports', {}).keys())))
    with col3:
        filter_outcome = st.selectbox("סינון לפי תוצאה", 
                                      ["הכל"] + list(stats['outcomes'].keys()))
    
    # הכנת טבלה
    display_df = df.copy()
    if filter_sport != "הכל" and 'sport_type' in display_df.columns:
        display_df = display_df[display_df['sport_type'] == filter_sport]
    if filter_outcome != "הכל":
        display_df = display_df[display_df['outcome'] == filter_outcome]
    
    # מיון לפי זמן (החדשות ביותר ראשונות) - לפי timestamp במקום datetime
    if 'timestamp' in display_df.columns:
        display_df = display_df.sort_values('timestamp', ascending=False)
    elif 'datetime' in display_df.columns:
        display_df = display_df.sort_values('datetime', ascending=False)
    display_df = display_df.head(show_count)
    
    # הצגת זמן עדכון אחרון - עם timezone מקומי
    if not display_df.empty and 'datetime' in display_df.columns:
        latest_time = display_df['datetime'].max()
        if pd.notna(latest_time):
            # המרה ל-timezone מקומי אם צריך
            israel_offset = timedelta(hours=2)
            israel_tz = timezone(israel_offset)
            
            # טיפול ב-pandas Timestamp
            if isinstance(latest_time, pd.Timestamp):
                if latest_time.tz is None:
                    local_latest = latest_time.tz_localize(timezone.utc).tz_convert(israel_tz)
                else:
                    local_latest = latest_time.tz_convert(israel_tz)
                # המרה ל-datetime רגיל להצגה
                local_latest_dt = local_latest.to_pydatetime().replace(tzinfo=None)
            else:
                if hasattr(latest_time, 'tzinfo') and latest_time.tzinfo is not None:
                    local_latest_dt = latest_time.astimezone(israel_tz).replace(tzinfo=None)
                else:
                    local_latest_dt = latest_time.replace(tzinfo=timezone.utc).astimezone(israel_tz).replace(tzinfo=None)
            
            st.caption(f"⏰ עדכון אחרון: {local_latest_dt.strftime('%Y-%m-%d %H:%M:%S')} (שעון ישראל)")
    
    # הצגה בטבלה קומפקטית (כמו פוזיציות)
    if not display_df.empty:
        # יצירת טבלה לעיבוד
        activity_table = display_df.copy()
        
        # הוספת עמודת Side עם emoji
        activity_table['Side'] = activity_table['side'].apply(
            lambda x: "🟢 Buy" if x == 'BUY' else "🔴 Sell"
        )
        
        # עיבוד Title - קיצור אם ארוך מדי
        if 'title' in activity_table.columns:
            activity_table['Title'] = activity_table['title'].apply(
                lambda x: x[:60] + "..." if len(str(x)) > 60 else str(x)
            )
        
        # עיבוד Outcome
        if 'outcome' in activity_table.columns:
            activity_table['Outcome'] = activity_table['outcome']
        
        # עיבוד Sport Type
        if 'sport_type' in activity_table.columns:
            activity_table['Sport'] = activity_table['sport_type']
        
        # עיבוד Price (בפורמט cents)
        if 'price' in activity_table.columns:
            activity_table['Price'] = activity_table['price'].apply(
                lambda x: f"{int(x * 100)}¢" if pd.notna(x) else "N/A"
            )
        
        # עיבוד Size
        if 'size' in activity_table.columns:
            activity_table['Size'] = activity_table['size'].apply(
                lambda x: f"{x:,.1f}" if pd.notna(x) else "0"
            )
        
        # עיבוד USDC Size
        if 'usdcSize' in activity_table.columns:
            activity_table['Amount'] = activity_table['usdcSize'].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "$0"
            )
        
        # עיבוד זמן - המרה ל-timezone מקומי והצגה
        if 'datetime' in activity_table.columns:
            israel_offset = timedelta(hours=2)
            israel_tz = timezone(israel_offset)
            
            def format_datetime(dt_val):
                if pd.isna(dt_val):
                    return "N/A"
                try:
                    if isinstance(dt_val, pd.Timestamp):
                        if dt_val.tz is None:
                            local_dt = dt_val.tz_localize(timezone.utc).tz_convert(israel_tz)
                        else:
                            local_dt = dt_val.tz_convert(israel_tz)
                        return local_dt.to_pydatetime().replace(tzinfo=None).strftime('%Y-%m-%d %H:%M')
                    else:
                        if hasattr(dt_val, 'tzinfo') and dt_val.tzinfo is not None:
                            local_dt = dt_val.astimezone(israel_tz)
                        else:
                            local_dt = dt_val.replace(tzinfo=timezone.utc).astimezone(israel_tz)
                        return local_dt.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M')
                except:
                    return "N/A"
            
            activity_table['Time'] = activity_table['datetime'].apply(format_datetime)
        
        # בחירת עמודות להצגה - סדר מותאם
        display_cols = ['Side', 'Time', 'Title', 'Outcome', 'Sport', 'Price', 'Size', 'Amount']
        available_display_cols = [col for col in display_cols if col in activity_table.columns]
        
        activity_display = activity_table[available_display_cols].copy()
        
        # הוספת styling - צבעי רקע
        def style_outcome_activity(val):
            """צבע רקע לעמודת outcome"""
            if pd.isna(val):
                return ''
            val_str = str(val).upper()
            if val_str in ['OVER', 'YES']:
                return 'background-color: #90EE90; color: #000;'  # ירוק בהיר
            elif val_str in ['UNDER', 'NO']:
                return 'background-color: #FFB6C1; color: #000;'  # אדום בהיר
            return ''
        
        def style_sport_activity(val):
            """צבע רקע לעמודת sport"""
            if pd.isna(val):
                return ''
            val_str = str(val).upper()
            if val_str == 'NHL':
                return 'background-color: #87CEEB; color: #000;'  # תכלת
            elif val_str == 'NBA':
                return 'background-color: #FFA500; color: #000;'  # כתום
            elif val_str == 'NFL':
                return 'background-color: #191970; color: #FFF;'  # כחול כהה
            elif val_str in ['SOCCER', 'FOOTBALL']:
                return 'background-color: #9370DB; color: #000;'  # סגול
            return ''
        
        # יצירת Styler
        styled_activity = activity_display.style
        
        # החלת צבעים על עמודות
        if 'Outcome' in activity_display.columns:
            styled_activity = styled_activity.applymap(style_outcome_activity, subset=['Outcome'])
        if 'Sport' in activity_display.columns:
            styled_activity = styled_activity.applymap(style_sport_activity, subset=['Sport'])
        
        # הצגת הטבלה - קומפקטית כמו פוזיציות
        st.dataframe(
            styled_activity,
            width='stretch',
            height=400,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("אין עסקאות להצגה")
    
    # הורדת נתונים
    st.markdown("---")
    st.subheader("💾 הורדת נתונים")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        wallet_id = wallet_name if not show_all else "all_wallets"
        st.download_button(
            label="📥 הורד CSV",
            data=csv,
            file_name=f"wallet_{wallet_id}_data.csv",
            mime="text/csv"
        )
    with col2:
        json_str = json.dumps(activities, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 הורד JSON",
            data=json_str,
            file_name=f"wallet_{wallet_id}_data.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
