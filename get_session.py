"""
اسکریپت ساخت Session String
این رو فقط یک بار اجرا کن
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = int(os.environ.get('API_ID', '1025357'))
api_hash = os.environ.get('API_HASH', 'cc7e65f06fb01b1d5fbba7838e2b4393')
phone_number = '+989379844274'


async def main():
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start(phone_number)

    session_str = client.session.save()
    print("\n" + "=" * 50)
    print("SESSION STRING ساخته شد:")
    print("=" * 50)
    print(session_str)
    print("=" * 50)
    print("\nاین رشته رو کپی کن و در Railway Variables بذار!")
    print("بعد Ctrl+C بزن تا بسته بشه!\n")

    await client.disconnect()


asyncio.run(main())
