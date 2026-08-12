import asyncio
import logging
import os
import tempfile
import time
from pathlib import Path

import psutil
import yt_dlp

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

# =========================================================
# CONFIG - BOT TOKEN (تم دمج التوكن الجديد بنجاح)
# =========================================================

BOT_TOKEN = "8827366261:AAFVfdvFreUBSwwY70DcM4zUFXSFxw0kydc"

# Telegram ID الخاص بك
ADMIN_ID = 6970770664

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================================================
# MEMORY
# =========================================================

user_urls = {}
user_downloads = {}

users = set()

download_count = 0
active_jobs = 0
completed_jobs = 0
failed_jobs = 0

started_at = time.time()

# =========================================================
# MAIN KEYBOARD
# =========================================================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🚀 بدء التحميل"),
            KeyboardButton(text="📊 إحصائياتي"),
        ],
        [
            KeyboardButton(text="⚙️ الإعدادات"),
            KeyboardButton(text="❓ المساعدة"),
        ],
    ],
    resize_keyboard=True,
    is_persistent=True,
    input_field_placeholder="أرسل رابط الفيديو..."
)

# =========================================================
# START
# =========================================================

@dp.message(Command("start"))
async def start_handler(message: Message):

    user_id = message.from_user.id
    users.add(user_id)

    await message.answer(
        "╔══════════════════════════════╗\n"
        "║          ⚡ KARAM BOT         ║\n"
        "║       MEDIA DOWNLOADER        ║\n"
        "╚══════════════════════════════╝\n\n"

        "مرحباً بك يا عزيزي 👋\n\n"

        "🎬 تحميل الفيديوهات\n"
        "🎵 استخراج الصوت MP3\n"
        "🎥 جودة عالية\n"
        "⚡ معالجة سريعة\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔗 أرسل رابط الفيديو للبدء\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=main_keyboard,
        parse_mode="HTML"
    )

# =========================================================
# START DOWNLOAD
# =========================================================

@dp.message(F.text == "🚀 بدء التحميل")
async def start_download_handler(message: Message):

    users.add(message.from_user.id)

    await message.answer(
        "🔗 <b>أرسل رابط الفيديو الآن</b>\n\n"
        "المدعوم حالياً:\n"
        "• TikTok\n"
        "• Instagram\n\n"
        "بعد إرسال الرابط ستظهر خيارات الجودة.",
        parse_mode="HTML"
    )

# =========================================================
# USER STATS
# =========================================================

@dp.message(F.text == "📊 إحصائياتي")
async def user_stats_handler(message: Message):

    user_id = message.from_user.id
    users.add(user_id)
    count = user_downloads.get(user_id, 0)

    await message.answer(
        "╔════════════════════════════╗\n"
        "║       📊 إحصائياتك         ║\n"
        "╠════════════════════════════╣\n"
        f"║ 🆔 ID: {user_id}\n"
        f"║ 📥 تحميلاتك: {count}\n"
        "╚════════════════════════════╝"
    )

# =========================================================
# SETTINGS
# =========================================================

@dp.message(F.text == "⚙️ الإعدادات")
async def settings_handler(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 أفضل جودة", callback_data="setting_best")],
            [
                InlineKeyboardButton(text="🎥 720p", callback_data="setting_720"),
                InlineKeyboardButton(text="📱 480p", callback_data="setting_480")
            ],
            [InlineKeyboardButton(text="🎵 MP3", callback_data="setting_mp3")]
        ]
    )

    await message.answer(
        "⚙️ <b>KARAM BOT SETTINGS</b>\n\nاختر الإعداد المفضل:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("setting_"))
async def settings_callback(callback: CallbackQuery):
    setting = callback.data.replace("setting_", "")
    names = {"best": "🔥 أفضل جودة", "720": "🎥 720p", "480": "📱 480p", "mp3": "🎵 MP3"}
    selected = names.get(setting, "غير معروف")

    await callback.answer("✅ تم الحفظ")
    await callback.message.edit_text(
        "╔════════════════════════════╗\n"
        "║       ⚙️ SETTINGS          ║\n"
        "╚════════════════════════════╝\n\n"
        f"✅ الإعداد الحالي:\n<b>{selected}</b>",
        parse_mode="HTML"
    )

# =========================================================
# HELP
# =========================================================

@dp.message(F.text == "❓ المساعدة")
async def help_handler(message: Message):
    await message.answer(
        "╔════════════════════════════╗\n"
        "║          ❓ HELP            ║\n"
        "╚════════════════════════════╝\n\n"
        "1️⃣ اضغط 🚀 بدء التحميل\n"
        "2️⃣ أرسل رابط الفيديو\n"
        "3️⃣ اختر الجودة\n"
        "4️⃣ انتظر المعالجة\n"
        "5️⃣ سيصل الملف تلقائياً\n\n"
        "📌 TikTok | Instagram | MP3",
        parse_mode="HTML"
    )

# =========================================================
# URL HANDLER & DOWNLOAD
# =========================================================

@dp.message(F.text.startswith("http"))
async def url_handler(message: Message):
    user_id = message.from_user.id
    users.add(user_id)
    url = message.text.strip()
    lower_url = url.lower()

    if not ("tiktok.com" in lower_url or "instagram.com" in lower_url or "youtu" in lower_url):
        await message.answer("❌ <b>الرابط غير مدعوم حالياً</b>", parse_mode="HTML")
        return

    user_urls[user_id] = url

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔥 أفضل جودة", callback_data="best")],
            [
                InlineKeyboardButton(text="🎥 720p", callback_data="720"),
                InlineKeyboardButton(text="📱 480p", callback_data="480")
            ],
            [InlineKeyboardButton(text="💾 حجم صغير", callback_data="small")],
            [InlineKeyboardButton(text="🎵 MP3", callback_data="mp3")],
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel")]
        ]
    )

    await message.answer(
        "✅ تم استلام الرابط بنجاح\nاختر جودة التحميل:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

def download_media(url, quality, folder):
    output = os.path.join(folder, "%(title).80s.%(ext)s")
    if quality == "mp3":
        options = {
            "format": "bestaudio/best",
            "outtmpl": output,
            "noplaylist": True,
            "quiet": True,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }
    else:
        formats = {
            "best": "best[ext=mp4][filesize<49M]/best[filesize<49M]/best",
            "720": "best[height<=720][ext=mp4][filesize<49M]/best",
            "480": "best[height<=480][ext=mp4][filesize<49M]/best",
            "small": "best[height<=360][ext=mp4][filesize<30M]/worst",
        }
        options = {"format": formats[quality], "outtmpl": output, "noplaylist": True, "quiet": True}

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Video")
        filename = ydl.prepare_filename(info)

    if quality == "mp3":
        filename = os.path.splitext(filename)[0] + ".mp3"

    if os.path.exists(filename):
        return filename, title

    for file in Path(folder).iterdir():
        if quality == "mp3" and file.suffix.lower() == ".mp3":
            return str(file), title
        elif quality != "mp3" and file.suffix.lower() in (".mp4", ".webm", ".mkv", ".mov"):
            return str(file), title

    raise FileNotFoundError("Downloaded file was not found.")

@dp.callback_query(F.data.in_(["best", "720", "480", "small", "mp3"]))
async def download_handler(callback: CallbackQuery):
    global download_count, active_jobs, completed_jobs, failed_jobs
    user_id = callback.from_user.id
    url = user_urls.get(user_id)

    if not url:
        await callback.answer("❌ أرسل الرابط من جديد.", show_alert=True)
        return

    quality = callback.data
    names = {"best": "🔥 أفضل جودة", "720": "🎥 720p", "480": "📱 480p", "small": "💾 حجم صغير", "mp3": "🎵 MP3"}
    await callback.answer()

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    status = await callback.message.answer("⏳ <b>جاري التحميل... يرجى الانتظار</b>", parse_mode="HTML")
    folder = tempfile.mkdtemp(prefix="karam_")
    active_jobs += 1

    try:
        loop = asyncio.get_running_loop()
        file_path, title = await loop.run_in_executor(None, download_media, url, quality, folder)

        if os.path.getsize(file_path) > 49 * 1024 * 1024:
            failed_jobs += 1
            await status.edit_text("❌ الملف أكبر من الحد المسموح في تليجرام.")
            return

        await status.edit_text("📤 <b>جاري إرسال الملف إليك...</b>", parse_mode="HTML")
        caption = f"⚡ <b>KARAM BOT</b>\n🎬 {str(title)[:100]}\n📌 {names[quality]}"

        if quality == "mp3":
            await callback.message.answer_audio(audio=FSInputFile(file_path), caption=caption, parse_mode="HTML")
        else:
            await callback.message.answer_video(video=FSInputFile(file_path), caption=caption, supports_streaming=True, parse_mode="HTML")

        download_count += 1
        completed_jobs += 1
        user_downloads[user_id] = user_downloads.get(user_id, 0) + 1
        await status.delete()
        await callback.message.answer("✅ اكتمل التحميل بنجاح! يمكنك إرسال رابط جديد.", reply_markup=main_keyboard)

    except Exception as error:
        failed_jobs += 1
        logging.exception("Download error: %s", error)
        try:
            await status.edit_text("❌ تعذر تحميل هذا الرابط، جرّب رابطاً آخر.")
        except Exception:
            pass
    finally:
        active_jobs = max(0, active_jobs - 1)
        user_urls.pop(user_id, None)

@dp.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery):
    user_urls.pop(callback.from_user.id, None)
    await callback.answer("تم الإلغاء")
    await callback.message.edit_text("❌ تم إلغاء العملية.")

@dp.message()
async def unknown_handler(message: Message):
    users.add(message.from_user.id)
    if message.text:
        await message.answer("أهلاً بك! أرسل رابط الفيديو للتحميل أو استخدم الأزرار بالأسفل.", reply_markup=main_keyboard)

# =========================================================
# STARTUP
# =========================================================

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    print("⚡ KARAM BOT Starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped.")
