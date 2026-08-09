import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonCallback
from datetime import datetime
import jdatetime
import pytz
import random

# تنظیمات API تلگرام
api_id = int(os.environ.get('API_ID', '1025357'))
api_hash = os.environ.get('API_HASH', 'cc7e65f06fb01b1d5fbba7838e2b4393')
phone_number = os.environ.get('PHONE_NUMBER', 'YOUR_PHONE_NUMBER')

# ذخیره سشن در Volume برای Railway
SESSION_DIR = os.environ.get('SESSION_DIR', '.')
SESSION_PATH = os.path.join(SESSION_DIR, 'mohammad_bot')

client = TelegramClient(SESSION_PATH, api_id, api_hash)

ADMIN_ID = 1110114019
SECRETARY_DELAY = 30

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

# متن‌های منشی
secretary_texts = [
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
clock_active = False
current_font = "معمولی"

# منشی
secretary_active = False
secretary_mode = "random"
secretary_custom_text = ""
pending_replies = {}

def format_time_with_font(time_str, font):
    font_mapping = {str(i): fonts[font][i] for i in range(10)}
    return ''.join([font_mapping.get(char, char) for char in time_str])

def get_secretary_text():
    if secretary_mode == "custom" and secretary_custom_text:
        return secretary_custom_text
    return random.choice(secretary_texts)


# ═══════════════════════════════
#   پنل شیشه‌ای
# ═══════════════════════════════

def get_panel_text():
    status = "🟢 آنلاین" if is_online else "🔴 آفلاین"
    clock = "🟢 فعال" if clock_active else "🔴 غیرفعال"
    sec = "🟢 فعال" if secretary_active else "🔴 غیرفعال"
    return (
        "┌──────────────────────┐\n"
        "│    🪟 پنل شیشه‌ای     │\n"
        "├──────────────────────┤\n"
        f"│  وضعیت: {status}   │\n"
        f"│  ساعت: {clock}      │\n"
        f"│  منشی: {sec}        │\n"
        f"│  فونت: {current_font}    │\n"
        "└──────────────────────┘"
    )

def get_panel_markup():
    online_text = "🔴 آفلاین شو" if is_online else "🟢 آنلاین شو"
    clock_text = "🔴 ساعت خاموش" if clock_active else "🟢 ساعت روشن"
    sec_text = "🔴 منشی خاموش" if secretary_active else "🟢 منشی روشن"
    return ReplyInlineMarkup(rows=[
        [KeyboardButtonCallback(text=online_text, data=b"toggle_online")],
        [KeyboardButtonCallback(text=clock_text, data=b"toggle_clock")],
        [KeyboardButtonCallback(text=sec_text, data=b"toggle_secretary")],
        [KeyboardButtonCallback(text="📝 تنظیم منشی", data=b"secretary_menu")],
        [KeyboardButtonCallback(text="🎨 فونت‌ها", data=b"show_fonts")],
        [KeyboardButtonCallback(text="📊 وضعیت", data=b"show_status")],
        [KeyboardButtonCallback(text="🤖 راهنما", data=b"show_help")],
    ])

def get_secretary_menu_markup():
    mode = "🎲 تصادفی" if secretary_mode == "random" else "✏️ دلخواه"
    return ReplyInlineMarkup(rows=[
        [KeyboardButtonCallback(text=f"حالت فعلی: {mode}", data=b"toggle_sec_mode")],
        [KeyboardButtonCallback(text="👁️ پیش‌نمایش متن‌ها", data=b"preview_texts")],
        [KeyboardButtonCallback(text="✏️ متن دلخواه", data=b"set_custom_text")],
        [KeyboardButtonCallback(text="🔙 بازگشت", data=b"back_panel")],
    ])

def get_fonts_markup():
    rows = []
    font_list = list(fonts.keys())
    for i in range(0, len(font_list), 3):
        row = []
        for j in range(3):
            if i + j < len(font_list):
                name = font_list[i + j]
                icon = "✅" if name == current_font else "🔹"
                row.append(KeyboardButtonCallback(text=f"{icon} {name}", data=f"font:{name}".encode()))
        rows.append(row)
    rows.append([KeyboardButtonCallback(text="🔙 بازگشت", data=b"back_panel")])
    return ReplyInlineMarkup(rows=rows)

def get_help_text():
    return (
        "🤖 راهنما:\n\n"
        "دستورات متنی:\n"
        "• پنل — باز کردن پنل شیشه‌ای\n"
        "• آنلاین شو — آنلاین + ساعت\n"
        "• آفلاین شو — همه چی خاموش\n"
        "• آنلاینی؟ — بررسی وضعیت\n"
        "• ساعت رو فعال کن / ساعت رو خاموش کن\n"
        "• منشی روشن / منشی خاموش\n"
        "• فونت [نام] — تغییر فونت\n"
        "• وضعیت — نمایش وضعیت\n"
        "• راهنما\n\n"
        "پنل شیشه‌ای:\n"
        "همه چیز با دکمه قابل کنترله! 🪟"
    )


# ═══════════════════════════════
#   آپدیت ساعت
# ═══════════════════════════════

async def update_name():
    global clock_active
    timezone = pytz.timezone('Asia/Tehran')
    while clock_active:
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


# ═══════════════════════════════
#   منشی — پاسخ خودکار با تاخیر
# ═══════════════════════════════

async def secretary_reply(chat_id):
    await asyncio.sleep(SECRETARY_DELAY)
    if chat_id in pending_replies:
        del pending_replies[chat_id]
        return
    try:
        text = get_secretary_text()
        await client.send_message(chat_id, text)
        print(f"Secretary replied to chat {chat_id}: {text}")
    except Exception as e:
        print(f"Secretary error: {e}")


# ═══════════════════════════════
#   دستورات متنی
# ═══════════════════════════════

@client.on(events.NewMessage())
async def handle_message(event):
    global is_online, current_font, clock_active, secretary_active, secretary_mode, secretary_custom_text
    if event.sender_id != ADMIN_ID:
        return

    msg = event.message.message.strip()

    if msg == "پنل":
        await event.reply(get_panel_text(), buttons=get_panel_markup())

    elif msg == "سلام":
        await event.reply("سلام! 😊 چطور می‌تونم کمکتون کنم سرورم؟")

    elif msg == "غلام":
        await event.reply("جونم! 😊 چطور می‌تونم کمکتون کنم سرورم؟")

    elif msg == "آنلاینی؟":
        if is_online and clock_active:
            await event.reply("✅ اره! کاملاً آنلاینم. ساعت هم فعاله! 🟢")
        elif is_online:
            await event.reply("🟢 آنلاینم ولی ساعت غیرفعاله.")
        else:
            await event.reply("❌ نه! آفلاینم سرورم.")

    elif msg == "آنلاین شو":
        if not is_online:
            is_online = True
            if not clock_active:
                clock_active = True
                asyncio.create_task(update_name())
            await event.reply("✅ آنلاین شدم! ساعت هم فعال شد. ⏰🟢")
        else:
            await event.reply("⚠️ از قبل آنلاینم!")

    elif msg == "آفلاین شو":
        if is_online:
            is_online = False
            clock_active = False
            secretary_active = False
            await event.reply("❌ آفلاین شدم! همه چی خاموش شد.")
        else:
            await event.reply("⚠️ از قبل آفلاینم!")

    elif msg in ["ساعت رو فعال کن", "ساعت روشن"]:
        if not clock_active:
            clock_active = True
            asyncio.create_task(update_name())
            await event.reply("🟢 ساعت فعال شد! هر 2 دقیقه آپدیت میشه.")
        else:
            await event.reply("⚠️ ساعت از قبل فعاله!")

    elif msg in ["ساعت رو خاموش کن", "ساعت خاموش"]:
        if clock_active:
            clock_active = False
            await event.reply("🔴 ساعت خاموش شد!")
        else:
            await event.reply("⚠️ ساعت از قبل خاموشه!")

    elif msg in ["منشی روشن", "منشی روشن کن"]:
        if not secretary_active:
            secretary_active = True
            await event.reply("🟢 منشی فعال شد!")
        else:
            await event.reply("⚠️ منشی از قبل فعاله!")

    elif msg in ["منشی خاموش", "منشی خاموش کن"]:
        if secretary_active:
            secretary_active = False
            pending_replies.clear()
            await event.reply("🔴 منشی خاموش شد!")
        else:
            await event.reply("⚠️ منشی از قبل خاموشه!")

    elif msg.startswith("فونت"):
        parts = msg.split(maxsplit=1)
        if len(parts) < 2 or parts[1] not in fonts:
            await event.reply("⚠️ نام فونت رو وارد کنید. مثال: فونت بلولد")
        else:
            current_font = parts[1]
            await event.reply(f"✅ فونت به '{current_font}' تغییر کرد.")

    elif msg == "وضعیت":
        status = "🟢 آنلاین" if is_online else "🔴 آفلاین"
        clock = "🟢 فعال" if clock_active else "🔴 غیرفعال"
        sec = "🟢 فعال" if secretary_active else "🔴 غیرفعال"
        await event.reply(f"📊 وضعیت:\n\n• {status}\n• ساعت: {clock}\n• منشی: {sec}\n• فونت: {current_font}")

    elif msg == "راهنما":
        await event.reply(get_help_text())


# ═══════════════════════════════
#   منشی — دریافت پیام بقیه
# ═══════════════════════════════

@client.on(events.NewMessage())
async def handle_secretary(event):
    if event.sender_id == ADMIN_ID:
        return
    if not secretary_active:
        return
    if event.is_group or event.is_channel:
        return

    chat_id = event.sender_id
    if chat_id in pending_replies:
        pending_replies[chat_id].cancel()

    task = asyncio.create_task(secretary_reply(chat_id))
    pending_replies[chat_id] = task


@client.on(events.NewMessage())
async def handle_admin_reply(event):
    if event.sender_id != ADMIN_ID:
        return
    if not event.is_private:
        return

    chat_id = event.chat_id
    if chat_id in pending_replies:
        pending_replies[chat_id].cancel()
        del pending_replies[chat_id]
        print(f"Admin replied to {chat_id}, secretary cancelled.")


# ═══════════════════════════════
#   کلیک روی دکمه‌ها
# ═══════════════════════════════

@client.on(events.CallbackQuery())
async def handle_callback(event):
    global is_online, current_font, clock_active, secretary_active, secretary_mode, secretary_custom_text
    if event.sender_id != ADMIN_ID:
        return

    data = event.data.decode()

    # ─── پنل اصلی ───
    if data == "toggle_online":
        if is_online:
            is_online = False
            clock_active = False
            secretary_active = False
            await event.answer("❌ آفلاین شدم!", alert=False)
        else:
            is_online = True
            if not clock_active:
                clock_active = True
                asyncio.create_task(update_name())
            await event.answer("✅ آنلاین شدم!", alert=False)
        await event.edit(get_panel_text(), buttons=get_panel_markup())

    elif data == "toggle_clock":
        if clock_active:
            clock_active = False
            await event.answer("🔴 ساعت خاموش شد!", alert=False)
        else:
            clock_active = True
            asyncio.create_task(update_name())
            await event.answer("🟢 ساعت فعال شد!", alert=False)
        await event.edit(get_panel_text(), buttons=get_panel_markup())

    elif data == "toggle_secretary":
        if secretary_active:
            secretary_active = False
            pending_replies.clear()
            await event.answer("🔴 منشی خاموش شد!", alert=False)
        else:
            secretary_active = True
            await event.answer("🟢 منشی فعال شد!", alert=False)
        await event.edit(get_panel_text(), buttons=get_panel_markup())

    # ─── منوی منشی ───
    elif data == "secretary_menu":
        mode = "🎲 تصادفی" if secretary_mode == "random" else "✏️ دلخواه"
        sec = "🟢 فعال" if secretary_active else "🔴 غیرفعال"
        await event.reply(
            f"📝 تنظیمات منشی:\n\n"
            f"• وضعیت: {sec}\n"
            f"• حالت: {mode}\n"
            f"• تاخیر: {SECRETARY_DELAY} ثانیه",
            buttons=get_secretary_menu_markup()
        )

    elif data == "toggle_sec_mode":
        if secretary_mode == "random":
            secretary_mode = "custom"
            await event.answer("حالت: دلخواه ✏️", alert=False)
        else:
            secretary_mode = "random"
            await event.answer("حالت: تصادفی 🎲", alert=False)
        mode = "🎲 تصادفی" if secretary_mode == "random" else "✏️ دلخواه"
        sec = "🟢 فعال" if secretary_active else "🔴 غیرفعال"
        await event.reply(
            f"📝 تنظیمات منشی:\n\n"
            f"• وضعیت: {sec}\n"
            f"• حالت: {mode}\n"
            f"• تاخیر: {SECRETARY_DELAY} ثانیه",
            buttons=get_secretary_menu_markup()
        )

    elif data == "preview_texts":
        texts = "\n".join([f"{i+1}. {t}" for i, t in enumerate(secretary_texts)])
        await event.reply(f"📝 متن‌های منشی (تصادفی):\n\n{texts}")

    elif data == "set_custom_text":
        secretary_mode = "custom"
        await event.reply("✏️ متن دلخواه رو بنویسید:\nمثال: متن منشی: سلام عزیزم")

    # ─── فونت‌ها ───
    elif data == "show_fonts":
        await event.reply("🎨 انتخاب فونت:", buttons=get_fonts_markup())

    elif data.startswith("font:"):
        font_name = data.split(":", 1)[1]
        if font_name in fonts:
            current_font = font_name
            await event.answer(f"✅ فونت '{current_font}' اعمال شد!", alert=False)
            await event.reply(f"✅ فونت به '{current_font}' تغییر کرد.", buttons=get_fonts_markup())
        else:
            await event.answer("⚠️ فونت پیدا نشد!", alert=True)

    # ─── وضعیت ───
    elif data == "show_status":
        status = "🟢 آنلاین" if is_online else "🔴 آفلاین"
        clock = "🟢 فعال" if clock_active else "🔴 غیرفعال"
        sec = "🟢 فعال" if secretary_active else "🔴 غیرفعال"
        mode = "🎲 تصادفی" if secretary_mode == "random" else "✏️ دلخواه"
        await event.reply(
            f"📊 وضعیت:\n\n"
            f"• {status}\n"
            f"• ساعت: {clock}\n"
            f"• منشی: {sec}\n"
            f"• حالت منشی: {mode}\n"
            f"• فونت: {current_font}"
        )

    # ─── راهنما ───
    elif data == "show_help":
        await event.reply(get_help_text())

    # ─── بازگشت ───
    elif data == "back_panel":
        await event.reply(get_panel_text(), buttons=get_panel_markup())


# ═══════════════════════════════
#   اجرا
# ═══════════════════════════════

async def main():
    await client.start(phone_number)
    print("Robot started!")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
