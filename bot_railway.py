import asyncio
import random
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.sessions import StringSession
from datetime import datetime, timedelta
import os
import jdatetime
import pytz

# تنظیمات API تلگرام از متغیرهای محیطی
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
phone_number = os.environ.get('PHONE_NUMBER', '')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 1110114019))
SESSION_STRING = os.environ.get('SESSION_STRING', '')

# ایجاد کلاینت تلگرام
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), api_id, api_hash)
else:
    client = TelegramClient('session_name', api_id, api_hash)

# لیست فونت‌ها
fonts = {
    "بلولد": "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",
    "دابل استروک": "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡",
    "مونواسپیس": "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫",
    "سانس بلولد": "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵",
    "سانس": "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿",
    "فولویدث": "０１２３４５６７８９",
    "زیرنویس": "₀₁₂₃₄₅₆₇₈₉",
    "بالانویس": "⁰¹²³⁴⁵⁶⁷⁸⁹",
    "معمولی": "0123456789",
}

# لیست پاسخ‌های منشی
secretary_replies = [
    "💤 صاحب اکانت فعلاً مشغوله، من مراقبم 😂",
    "🤖 ارباب هنوز پاسخ نداده، لطفاً منتظر بمانید",
    "👀 پیام ثبت شد، وقتی رئیس برگشت جواب می‌گیره",
    "سرورم داره یه لحظه رفرش میشه، صبر کن 😂",
    "🤖 سرورم رفت یه دور با خودش مشورت کنه، الان برمی‌گرده",
    "⚙️ سیستم در حال پردازش جواب خفن... لطفاً صبر کنید 😎",
    "🧠 مغز سرورم هنگ کرده، دارم ریستش می‌کنم 😂",
    "🚀 سرورم داره توربو می‌زنه، جواب الان میاد",
    "☕️ سرورم رفته قهوه بخوره، برمی‌گرده",
    "📡 ارتباط با مغز اصلی برقرار شد، چند ثانیه صبر کن",
    "🔥 سرورم داره جواب رو از آرشیو کهکشان پیدا می‌کنه",
]

# وضعیت‌ها
is_online = False
current_font = "معمولی"
font_random = False  # حالت رندوم فونت
secretary_active = False

# لیست کسانی که قبلاً جواب گرفتن با زمان
replied_users = {}


def cleanup_expired_users():
    """پاک کردن کاربرانی که بیشتر از ۲ ساعت پیش جواب گرفتن"""
    now = datetime.now()
    expired = [uid for uid, ts in replied_users.items() if now - ts > timedelta(hours=2)]
    for uid in expired:
        del replied_users[uid]


def get_current_font():
    """اگه حالت رندوم فعال باشه، فونت رندوم انتخاب کن"""
    if font_random:
        return random.choice(list(fonts.keys()))
    return current_font


def format_time_with_font(time_str, font):
    """فرمت‌بندی ساعت و تاریخ با فونت مورد نظر"""
    font_mapping = {str(i): fonts[font][i] for i in range(10)}
    return ''.join([font_mapping.get(char, char) for char in time_str])


async def update_name():
    """به‌روزرسانی نام پروفایل هر دو دقیقه یکبار"""
    global is_online
    timezone = pytz.timezone('Asia/Tehran')
    while is_online:
        try:
            now = datetime.now(timezone)
            jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
            # هر بار فونت متفاوت انتخاب بشه (چه رندوم چه ثابت)
            font_name = get_current_font()
            formatted_time = format_time_with_font(jalali_now.strftime('%H:%M'), font_name)
            formatted_date = format_time_with_font(jalali_now.strftime('%Y/%m/%d'), font_name)
            await client(UpdateProfileRequest(first_name=f"{formatted_time} | {formatted_date}"))
            print(f"Updated name: {formatted_time} | {formatted_date} (font: {font_name})")
        except Exception as e:
            print(f"Error updating name: {e}")
        finally:
            await asyncio.sleep(120)


@client.on(events.NewMessage())
async def handle_message(event):
    """مدیریت پیام‌ها و تنظیمات ربات"""
    global is_online, current_font, font_random, secretary_active

    sender_id = event.sender_id

    # پیام‌های غیر از مدیر → منشی خودکار (فقط آدم‌ها + فقط خصوصی + فقط یکبار در ۲ ساعت)
    if sender_id != ADMIN_ID:
        if secretary_active and event.is_private:
            sender = await event.get_sender()
            if sender and not sender.bot:
                cleanup_expired_users()
                if sender_id not in replied_users:
                    replied_users[sender_id] = datetime.now()
                    reply_text = random.choice(secretary_replies)
                    await event.reply(reply_text)
        return

    # دستورات مدیر → فقط در چت خصوصی با خودش (پیام‌های ذخیره‌شده)
    if event.chat_id != ADMIN_ID:
        return

    message_text = event.message.message.strip()

    if message_text == "سلام":
        await event.reply("سلام! 😊 چطور می‌تونم کمکتون کنم سرورم؟")

    elif message_text == "غلام":
        await event.reply("جونم! 😊 چطور می‌تونم کمکتون کنم سرورم؟")

    elif message_text == "آنلاینی؟":
        await event.reply("✅ اره! سرورم آنلاینم و من آماده‌ام که به دستورات شما پاسخ بدم.")

    elif message_text == "آنلاین شو":
        if not is_online:
            is_online = True
            await event.reply("✅ آنلاین شدم! حالا ساعت و تاریخ رو هر دو دقیقه یکبار به‌روزرسانی می‌کنم (24 ساعته).")
            asyncio.create_task(update_name())
        else:
            await event.reply("⚠️ من از قبل آنلاینم سرورم!")

    elif message_text == "آفلاین شو":
        if is_online:
            is_online = False
            await event.reply("❌ آفلاین شدم! دیگه ساعت و تاریخ رو برات به‌روزرسانی نمیکنم.")
        else:
            await event.reply("⚠️ من از قبل آفلاینم سرورم!")

    elif message_text.startswith("فونت"):
        parts = message_text.split(maxsplit=1)
        if len(parts) < 2:
            await event.reply("⚠️ لطفاً نام فونت را بعد از فونت وارد کنید.\nمثال: فونت بلولد\nیا: فونت رندوم")
        elif parts[1] == "رندوم":
            font_random = True
            await event.reply("🎲 فونت رندوم فعال شد! هر ۲ دقیقه فونت عوض میشه.")
        elif parts[1] in fonts:
            font_random = False
            current_font = parts[1]
            await event.reply(f"✅ فونت به '{current_font}' تغییر کرد.")
        else:
            await event.reply("⚠️ فونت نامعتبر!\nلیست فونت‌ها:\n" + ", ".join(fonts.keys()) + "\nیا بنویس: فونت رندوم")

    elif message_text == "منشی روشن":
        if not secretary_active:
            secretary_active = True
            await event.reply("✅ منشی روشن شد! حالا به پیام‌های بقیه خودکار جواب میدم.")
        else:
            await event.reply("⚠️ منشی از قبل روشن هست!")

    elif message_text == "منشی خاموش":
        if secretary_active:
            secretary_active = False
            await event.reply("❌ منشی خاموش شد! دیگه به پیام‌های بقیه جواب نمیدم.")
        else:
            await event.reply("⚠️ منشی از قبل خاموش هست!")

    elif message_text == "وضعیت":
        cleanup_expired_users()
        status_message = (
            f"📊 **وضعیت ربات:**\n\n"
            f"• وضعیت: {'🟢 آنلاین' if is_online else '🔴 آفلاین'}\n"
            f"• فونت فعلی: {'🎲 رندوم' if font_random else current_font}\n"
            f"• منشی: {'🟢 روشن' if secretary_active else '🔴 خاموش'}\n"
            f"• تعداد جواب‌های منشی: {len(replied_users)} نفر"
        )
        await event.reply(status_message)

    elif message_text == "راهنما":
        help_message = (
            "🤖 **راهنما:**\n\n"
            "• **آنلاین شو**: فعال کردن به‌روزرسانی ساعت و تاریخ.\n"
            "• **آفلاین شو**: غیرفعال کردن به‌روزرسانی.\n"
            "• **فونت [نام]**: تغییر فونت (مثال: فونت بلولد).\n"
            "• **فونت رندوم**: هر ۲ دقیقه فونت عوض بشه.\n"
            "• **منشی روشن**: فعال کردن پاسخ خودکار.\n"
            "• **منشی خاموش**: غیرفعال کردن پاسخ خودکار.\n"
            "• **وضعیت**: نمایش وضعیت کامل.\n\n"
            "**لیست فونت‌ها:**\n" +
            ", ".join(fonts.keys())
        )
        await event.reply(help_message)

    else:
        return


async def main():
    if SESSION_STRING:
        await client.start()
    else:
        await client.start(phone_number)
    print("Robot started!")
    await client.run_until_disconnected()


asyncio.run(main())
