"""
סקריפט לקבלת Chat ID מטלגרם
"""

import requests
import sys

# תיקון encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BOT_TOKEN = "8577054844:AAEGWiSGPzJTA3Kt0ndwgelEK16iNU2G6yI"

def get_chat_id():
    """קבלת Chat ID מהבוט"""
    print("=" * 60)
    print("קבלת Chat ID מטלגרם")
    print("=" * 60)
    print("\n📝 הוראות:")
    print("1. פתח טלגרם וחפש את הבוט שלך: @PolyNBA2026Bot")
    print("2. שלח לו הודעה כלשהי (למשל: /start או שלום)")
    print("3. המתן 2-3 שניות ואז הרץ את הסקריפט שוב")
    print("\n🔍 בודק הודעות חדשות...")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                updates = data['result']
                
                if updates:
                    # לוקח את ההודעה האחרונה
                    last_update = updates[-1]
                    if 'message' in last_update:
                        chat_id = last_update['message']['chat']['id']
                        chat_type = last_update['message']['chat']['type']
                        first_name = last_update['message']['chat'].get('first_name', '')
                        username = last_update['message']['chat'].get('username', '')
                        
                        print("\n✅ נמצא Chat ID!")
                        print("=" * 60)
                        print(f"Chat ID: {chat_id}")
                        print(f"סוג: {chat_type}")
                        if first_name:
                            print(f"שם: {first_name}")
                        if username:
                            print(f"Username: @{username}")
                        print("=" * 60)
                        print(f"\n📋 העתק את המספר הזה: {chat_id}")
                        print("\nעכשיו עדכן את telegram_notifier.py:")
                        print(f'TELEGRAM_CHAT_ID = "{chat_id}"')
                        
                        return chat_id
                    else:
                        print("⚠️ לא נמצאו הודעות. ודא ששלחת הודעה לבוט.")
                else:
                    print("⚠️ לא נמצאו הודעות. ודא ששלחת הודעה לבוט.")
            else:
                print("⚠️ שגיאה בקבלת נתונים מהבוט")
                print(f"תגובה: {data}")
        else:
            print(f"❌ שגיאה: {response.status_code}")
            print(f"תגובה: {response.text}")
            
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    
    return None

if __name__ == "__main__":
    get_chat_id()
