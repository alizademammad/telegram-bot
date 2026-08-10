import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.sessions import StringSession
from datetime import datetime
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
    "معمولی": "0123456789"
}

# وضعیت‌ها
is_online = False
current_font = "معمولی"
secretary_active = False


def format_time_with_font(time_str, font):
    font_mapping = {str(i): fonts[font][i] for i in range(10)}
    return ''.join([font_mapping.get(char, char) for char in time_str])


def get_panel_text():
    """متن پنل اصلی"""
    return (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "     🤖 **پنل مدیریت ربات**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🟢 وضعیت: **{'آنلاین' if is_online else 'آفلاین'}**\n"
        f"🕐 ساعت: **به‌روزرسانی خودکار**\n"
        f"✍️ فونت: **{current_font}**\n"
        f"💬 منشی: **{'فعال' if secretary_active else 'غیرفعال'}**"
    )


def get_panel_markup():
    """دکمه‌های پنل اصلی"""
    return [
        [Button.inline("🟢 آنلاین شو", data=b"toggle_online")],
        [Button.inline("🔴 آفلاین شو", data=b"toggle_offline")],
        [Button.inline("📊 وضعیت", data=b"show_status")],
        [Button.inline("⚙️ تنظیمات فونت", data=b"font_menu")],
        [Button.inline("💬 منشی خودکار", data=b"secretary_menu")],
        [Button.inline("📝 راهنما", data=b"show_help")],
    ]


def get_font_menu_text():
    """متن منوی فونت"""
    return "📝 **انتخاب فونت:**\n\nفونت فعلی: " + current_font


def get_font_menu_markup():
    """دکمه‌های منوی فونت"""
    buttons = []
    row = []
    for i, name in enumerate(fonts.keys()):
        row.append(Button.inline(name, data=f"font_{name}".encode()))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([Button.inline("🔙 بازگشت", data=b"back_panel")])
    return buttons


def get_secretary_menu_text():
    """متن منوی منشی"""
    status = "🟢 فعال" if secretary_active else "🔴 غیرفعال"
    return (
        "💬 **منشی خودکار**\n\n"
        f"وضعیت فعلی: {status}\n\n"
        "وقتی منشی فعال باشه، به پیام‌های دیگران یه پیام خودکار ارسال میشه."
    )


def get_secretary_menu_markup():
    """دکمه‌های منوی منشی"""
    return [
        [Button.inline("🟢 فعال‌سازی منشی", data=b"secretary_on")],
        [Button.inline("🔴 غیرفعال‌سازی منشی", data=b"secretary_off")],
        [Button.inline("🔙 بازگشت", data=b"back_panel")],
    ]


async def update_name():
    """به‌روزرسانی نام پروفایل هر دو دقیقه"""
    global is_online
    timezone = pytz.timezone('Asia/Tehran')
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
            await asyncio.sleep(120)


# ===== هندلر پیام‌های متنی =====
@client.on(events.NewMessage())
async def handle_message(event):
    global is_online, current_font, secretary_active

    if event.sender_id != ADMIN_ID:
        return

    message_text = event.message.message.strip()

    if message_text == "پنل":
        await client.send_message(event.chat_id, get_panel_text(), buttons=get_panel_markup())

    elif message_text == "سلام":
        await event.reply("سلام! 😊 چطور می‌تونم کمکتون کنم؟")

    elif message_text == "آنلاینی؟":
        status = "🟢 آنلاینم" if is_online else "🔴 آفلاینم"
        await event.reply(status)

    else:
        return


# ===== هندلر کلیک روی دکمه‌ها =====
@client.on(events.CallbackQuery())
async def handle_callback(event):
    global is_online, current_font, secretary_active

    if event.sender_id != ADMIN_ID:
        await event.answer("❌ دسترسی ندارید!", alert=True)
        return

    data = event.data.decode()

    # پنل اصلی
    if data == "back_panel":
        await event.edit(get_panel_text(), buttons=get_panel_markup())

    # آنلاین شو
    elif data == "toggle_online":
        if not is_online:
            is_online = True
            asyncio.create_task(update_name())
            await event.answer("✅ آنلاین شدم!", alert=False)
            await event.edit(get_panel_text(), buttons=get_panel_markup())
        else:
            await event.answer("⚠️ از قبل آنلاینم!", alert=False)

    # آفلاین شو
    elif data == "toggle_offline":
        if is_online:
            is_online = False
            await event.answer("❌ آفلاین شدم!", alert=False)
            await event.edit(get_panel_text(), buttons=get_panel_markup())
        else:
            await event.answer("⚠️ از قبل آفلاینم!", alert=False)

    # وضعیت
    elif data == "show_status":
        status = "🟢 آنلاین" if is_online else "🔴 آفلاین"
        sec = "🟢 فعال" if secretary_active else "🔴 غیرفعال"
        text = (
            f"📊 **وضعیت ربات:**\n\n"
            f"• وضعیت: {status}\n"
            f"• فونت فعلی: {current_font}\n"
            f"• منشی: {sec}"
        )
        await event.answer()
        await event.edit(text, buttons=[[Button.inline("🔙 بازگشت", data=b"back_panel")]])

    # منوی فونت
    elif data == "font_menu":
        await event.answer()
        await event.edit(get_font_menu_text(), buttons=get_font_menu_markup())

    # تغییر فونت
    elif data.startswith("font_"):
        font_name = data[5:]  # حذف "font_"
        if font_name in fonts:
            current_font = font_name
            await event.answer(f"✅ فونت به '{current_font}' تغییر کرد!", alert=False)
            await event.edit(get_font_menu_text(), buttons=get_font_menu_markup())
        else:
            await event.answer("❌ فونت نامعتبر!", alert=True)

    # منوی منشی
    elif data == "secretary_menu":
        await event.answer()
        await event.edit(get_secretary_menu_text(), buttons=get_secretary_menu_markup())

    # فعال‌سازی منشی
    elif data == "secretary_on":
        secretary_active = True
        await event.answer("✅ منشی فعال شد!", alert=False)
        await event.edit(get_secretary_menu_text(), buttons=get_secretary_menu_markup())

    # غیرفعال‌سازی منشی
    elif data == "secretary_off":
        secretary_active = False
        await event.answer("❌ منشی غیرفعال شد!", alert=False)
        await event.edit(get_secretary_menu_text(), buttons=get_secretary_menu_markup())

    # راهنما
    elif data == "show_help":
        help_text = (
            "📝 **راهنما:**\n\n"
            "• **پنل**: باز کردن پنل مدیریت\n"
            "• **آنلاین شو**: فعال کردن به‌روزرسانی خودکار ساعت\n"
            "• **آفلاین شو**: غیرفعال کردن به‌روزرسانی\n"
            "• **تغییر فونت**: از منوی پنل انتخاب کنید\n"
            "• **منشی**: فعال/غیرفعال کردن منشی خودکار\n"
        )
        await event.answer()
        await event.edit(help_text, buttons=[[Button.inline("🔙 بازگشت", data=b"back_panel")]])


async def main():
    if SESSION_STRING:
        await client.start()
    else:
        await client.start(phone_number)
    print("Robot started with Panel!")
    await client.run_until_disconnected()


asyncio.run(main())
