"""
اسکریپت ساخت Session String
این رو فقط یک بار اجرا کن تا Session String بسازی
"""

import os
from telethon import TelegramClient
from telethon.sessions import StringSession

# تنظیمات
api_id = int(os.environ.get('API_ID', '1025357'))
api_hash = os.environ.get('API_HASH', 'cc7e65f06fb01b1d5fbba7838e2b4393')
phone_number = os.environ.get('PHONE_NUMBER', 'YOUR_PHONE_NUMBER')

# ایجاد کلاینت
client = StringSession()

async def main():
    print("در حال اتصال...")
    await client.start(phone_number, api_hash=api_hash, api_id=api_id)
    
    # ذخیره Session String
    session_string = client.session.save()
    
    print("\n" + "="*50)
    print("✅ Session String ساخته شد!")
    print("="*50)
    print(f"\nSESSION_STRING = {session_string}")
    print("\nاین مقدار رو در Railway Variables اضافه کن!")
    print("="*50)

with client:
    client.loop.run_until_complete(main())
