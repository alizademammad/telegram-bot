import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from datetime import datetime
import jdatetime
import pytz

# تنظیمات API تلگرام
api_id = '1025357'  # جایگزین کنید با API ID خود
api_hash = 'cc7e65f06fb01b1d5fbba7838e2b4393'  # جایگزین کنید با API Hash خود
phone_number = 'YOUR_PHONE_NUMBER'  # جایگزین کنید با شماره تلفن خود

# ایجاد کلاینت تلگرام
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
    "معمولی": "0123456789"
}

# وضعیت آنلاین/آفلاین
is_online = False
current_font = "معمولی"  # فونت پیش‌فرض

def format_time_with_font(time_str, font):
    """فرمت‌بندی ساعت و تاریخ با فونت مورد نظر"""
    font_mapping = {str(i): fonts[font][i] for i in range(10)}
    return ''.join([font_mapping.get(char, char) for char in time_str])

async def update_name():
    """به‌روزرسانی نام پروفایل هر دو دقیقه یکبار"""
    global is_online
    timezone = pytz.timezone('Asia/Tehran')  # تنظیم منطقه زمانی
    while is_online:
        try:
            now = datetime.now(timezone)
            jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
            formatted_time = format_time_with_font(jalali_now.strftime('%H:%M'), current_font)
            formatted_date = format_time_with_font(jalali_now.strftime('%Y/%m/%d'), current_font)
            await client(UpdateProfileRequest(first_name=f"{formatted_time} | {formatted_date}"))
            print(f"Updated name: {formatted_time} | {formatted_date}")
        except Exception as e:
            print(f"Error updating name: {e}")
        finally:
            await asyncio.sleep(120)  # منتظر ماندن برای دو دقیقه

@client.on(events.NewMessage())
async def handle_message(event):
    """مدیریت پیام‌ها و تنظیمات ربات"""
    global is_online, current_font
    # تنها به پیام‌های مدیر واکنش بده
    if event.sender_id != 1110114019:  # جایگزین کنید با ID کاربری خود
        return

    message_text = event.message.message.strip()
    # پاسخ به پیام‌های خاص
    if message_text == "سلام":    
        await event.reply("سلام! 😊 چطور می‌تونم کمکتون کنم سرورم؟")
        return

    if message_text == "غلام":    
        await event.reply("جونم! 😊 چطور می‌تونم کمکتون کنم سرورم؟")
        return

    if message_text == "آنلاینی؟":
        await event.reply("✅ اره! سرورم آنلاینم و من آماده‌ام که به دستورات شما پاسخ بدم.")
        return
    # بررسی دستورات معتبر
    if message_text == "آنلاین شو":
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
        if len(parts) < 2 or parts[1] not in fonts:
            await event.reply("⚠️ لطفاً نام فونت را بعد از `فونت` وارد کنید. مثال: `فونت بلولد`")
        else:
            current_font = parts[1]
            await event.reply(f"✅ فونت به '{current_font}' تغییر کرد.")
    elif message_text == "وضعیت":
        status_message = (
            f"📊 **وضعیت ربات:**\n\n"
            f"• وضعیت: {'🟢 آنلاین' if is_online else '🔴 آفلاین'}\n"
            f"• فونت فعلی: `{current_font}`"
        )
        await event.reply(status_message)
    elif message_text == "راهنما":
        help_message = (
            "🤖 **راهنما:**\n\n"
            "• `آنلاین شو`: فعال کردن به‌روزرسانی ساعت و تاریخ (24 ساعته).\n"
            "• `آفلاین شو`: غیرفعال کردن به‌روزرسانی ساعت و تاریخ.\n"
            "• `فونت [نام_فونت]`: تغییر فونت به فونت مورد نظر.\n"
            "• `وضعیت`: نمایش وضعیت آنلاین/آفلاین و فونت فعلی.\n"
            "• `راهنما`: نمایش این پیام راهنما.\n\n"
            "**لیست فونت‌ها:**\n" +
            ", ".join(fonts.keys())
        )
        await event.reply(help_message)
    # اگر پیام با دستورات معتبر مطابقت نداشت، ربات جواب نمی‌ده
    else:
        return  # <<<<--- ربات به پیام‌های غیرمرتبط واکنش نشان نمی‌دهد

async def main():
    await client.start(phone_number)
    print("Robot started!")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())