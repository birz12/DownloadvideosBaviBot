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
# CONFIG
# =========================================================

BOT_TOKEN = "8827366261:AAFyEyLN2evn77IEgqOG7ZnlIp3FEm8_B-Q"

# ضع Telegram ID الخاص بك
ADMIN_ID = 6970770664

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================================================
# MEMORY DATA
# =========================================================

user_urls = {}

users = set()

download_count = 0
active_jobs = 0
completed_jobs = 0
failed_jobs = 0

started_at = time.time()

# =========================================================
# FIXED MAIN KEYBOARD
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

    users.add(message.from_user.id)

    await message.answer(
        "╔══════════════════════════════╗\n"
        "║          ⚡ KARAM BOT         ║\n"
        "║       MEDIA DOWNLOADER        ║\n"
        "╚══════════════════════════════╝\n\n"

        "مرحباً بك 👋\n\n"

        "🎬 تحميل الفيديوهات\n"
        "🎵 استخراج الصوت MP3\n"
        "⚡ معالجة سريعة\n"
        "🎥 جودة عالية\n"
        "🛡️ نظام مستقر\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔗 أرسل رابط الفيديو للبدء\n"
        "━━━━━━━━━━━━━━━━━━━━",

        reply_markup=main_keyboard,
        parse_mode="HTML"
    )


# =========================================================
# START DOWNLOAD BUTTON
# =========================================================

@dp.message(F.text == "🚀 بدء التحميل")
async def start_download_button(message: Message):

    users.add(message.from_user.id)

    await message.answer(
        "🔗 <b>أرسل رابط الفيديو الآن</b>\n\n"
        "المنصات المدعومة حالياً:\n"
        "• TikTok\n"
        "• Instagram\n\n"
        "بعد إرسال الرابط ستظهر خيارات الجودة.",
        parse_mode="HTML"
    )


# =========================================================
# USER STATS
# =========================================================

@dp.message(F.text == "📊 إحصائياتي")
async def user_stats_button(message: Message):

    users.add(message.from_user.id)

    await message.answer(
        "╔════════════════════════════╗\n"
        "║       📊 إحصائياتك         ║\n"
        "╠════════════════════════════╣\n"
        f"║ 🆔 ID: {message.from_user.id}\n"
        f"║ 📥 إجمالي التحميلات: {download_count}\n"
        "╚════════════════════════════╝"
    )


# =========================================================
# SETTINGS
# =========================================================

@dp.message(F.text == "⚙️ الإعدادات")
async def settings_button(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔥 أفضل جودة",
                    callback_data="setting_best"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎥 720p",
                    callback_data="setting_720"
                ),
                InlineKeyboardButton(
                    text="📱 480p",
                    callback_data="setting_480"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎵 MP3",
                    callback_data="setting_mp3"
                )
            ]
        ]
    )

    await message.answer(
        "⚙️ <b>إعدادات KARAM BOT</b>\n\n"
        "اختر الإعداد الذي تريده:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# =========================================================
# SETTINGS CALLBACK
# =========================================================

@dp.callback_query(F.data.startswith("setting_"))
async def settings_callback(callback: CallbackQuery):

    setting = callback.data.replace(
        "setting_",
        ""
    )

    names = {
        "best": "🔥 أفضل جودة",
        "720": "🎥 720p",
        "480": "📱 480p",
        "mp3": "🎵 MP3",
    }

    selected = names.get(
        setting,
        "غير معروف"
    )

    await callback.answer(
        "تم اختيار الإعداد"
    )

    await callback.message.edit_text(
        "✅ <b>تم حفظ الإعداد</b>\n\n"
        f"الإعداد: {selected}",
        parse_mode="HTML"
    )


# =========================================================
# HELP
# =========================================================

@dp.message(F.text == "❓ المساعدة")
async def help_button(message: Message):

    await message.answer(
        "╔════════════════════════════╗\n"
        "║          ❓ المساعدة        ║\n"
        "╚════════════════════════════╝\n\n"

        "1️⃣ اضغط 🚀 بدء التحميل\n"
        "2️⃣ أرسل رابط الفيديو\n"
        "3️⃣ اختر الجودة\n"
        "4️⃣ انتظر اكتمال التحميل\n\n"

        "📌 المنصات المدعومة:\n"
        "• TikTok\n"
        "• Instagram\n\n"

        "🎵 يمكن استخراج الصوت بصيغة MP3."
    )


# =========================================================
# ERROR RATE
# =========================================================

def get_error_rate():

    total = completed_jobs + failed_jobs

    if total == 0:
        return 0.0

    return (
        failed_jobs /
        total
    ) * 100


# =========================================================
# SYSTEM INFO
# =========================================================

def get_system_info():

    cpu = psutil.cpu_percent(
        interval=None
    )

    ram = psutil.virtual_memory().percent

    disk = psutil.disk_usage(
        "/"
    ).percent

    return cpu, ram, disk


# =========================================================
# DASHBOARD TEXT
# =========================================================

def dashboard_text():

    cpu, ram, disk = get_system_info()

    total_jobs = (
        completed_jobs +
        failed_jobs +
        active_jobs
    )

    if total_jobs > 0:

        progress = int(
            (
                completed_jobs /
                total_jobs
            ) * 100
        )

    else:

        progress = 0

    bars = 20

    filled = int(
        (progress / 100) *
        bars
    )

    progress_bar = (
        "█" * filled +
        "░" * (
            bars - filled
        )
    )

    error_rate = get_error_rate()

    return (
        "╔══════════════════════════════════╗\n"
        "║       🖥️ <b>LIVE DASHBOARD</b>       ║\n"
        "╠══════════════════════════════════╣\n"
        f"║ 👥 USERS        {len(users):>8}           ║\n"
        f"║ 📥 DOWNLOADS   {download_count:>8}           ║\n"
        f"║ 🟢 ACTIVE JOBS {active_jobs:>8}           ║\n"
        f"║ ❌ ERROR RATE   {error_rate:>7.2f}%          ║\n"
        "╠══════════════════════════════════╣\n"
        "║        ⚡ <b>REALTIME JOBS</b>       ║\n"
        f"║ {progress_bar} {progress:>3}%      ║\n"
        "╠══════════════════════════════════╣\n"
        f"║ 🧠 CPU          {cpu:>5.1f}%             ║\n"
        f"║ 🧮 RAM          {ram:>5.1f}%             ║\n"
        f"║ 💾 DISK         {disk:>5.1f}%             ║\n"
        "║ ⚙️ WORKERS       1 / 1             ║\n"
        "╠══════════════════════════════════╣\n"
        "║ 🟢 SYSTEM STATUS: ONLINE          ║\n"
        "╚══════════════════════════════════╝"
    )


# =========================================================
# DASHBOARD KEYBOARD
# =========================================================

def dashboard_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 REFRESH",
                    callback_data="dashboard_refresh"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧵 JOBS",
                    callback_data="dashboard_jobs"
                ),
                InlineKeyboardButton(
                    text="⚙️ WORKERS",
                    callback_data="dashboard_workers"
                )
            ]
        ]
    )


# =========================================================
# DASHBOARD
# =========================================================

@dp.message(Command("dashboard"))
async def dashboard_handler(message: Message):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "⛔ هذا الأمر مخصص للإدارة فقط."
        )

        return

    await message.answer(
        dashboard_text(),
        reply_markup=dashboard_keyboard(),
        parse_mode="HTML"
    )


# =========================================================
# DASHBOARD REFRESH
# =========================================================

@dp.callback_query(
    F.data == "dashboard_refresh"
)
async def dashboard_refresh(
    callback: CallbackQuery
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "⛔ غير مصرح.",
            show_alert=True
        )

        return

    await callback.answer(
        "🔄 تم تحديث البيانات"
    )

    try:

        await callback.message.edit_text(
            dashboard_text(),
            reply_markup=dashboard_keyboard(),
            parse_mode="HTML"
        )

    except Exception:

        pass


# =========================================================
# DASHBOARD JOBS
# =========================================================

@dp.callback_query(
    F.data == "dashboard_jobs"
)
async def dashboard_jobs(
    callback: CallbackQuery
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "⛔ غير مصرح.",
            show_alert=True
        )

        return

    await callback.answer()

    text = (
        "╔══════════════════════════════╗\n"
        "║       🧵 <b>ACTIVE JOBS</b>       ║\n"
        "╠══════════════════════════════╣\n"
        f"║ 🟡 Processing: <b>{active_jobs}</b>        ║\n"
        "║ 🔵 Queued: <b>0</b>                ║\n"
        f"║ 🟢 Completed: <b>{completed_jobs}</b>      ║\n"
        f"║ ❌ Failed: <b>{failed_jobs}</b>            ║\n"
        "╚══════════════════════════════╝"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Refresh",
                    callback_data="dashboard_jobs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Dashboard",
                    callback_data="dashboard_refresh"
                )
            ]
        ]
    )

    try:

        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception:

        pass


# =========================================================
# WORKERS
# =========================================================

@dp.callback_query(
    F.data == "dashboard_workers"
)
async def dashboard_workers(
    callback: CallbackQuery
):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "⛔ غير مصرح.",
            show_alert=True
        )

        return

    cpu, ram, disk = get_system_info()

    await callback.answer()

    text = (
        "╔══════════════════════════════╗\n"
        "║       ⚙️ <b>WORKERS</b>          ║\n"
        "╠══════════════════════════════╣\n"
        "║ 🟢 Worker-01   ONLINE         ║\n"
        f"║ 🧠 CPU         {cpu:.1f}%          ║\n"
        f"║ 🧮 RAM         {ram:.1f}%          ║\n"
        f"║ 💾 Storage     {disk:.1f}%          ║\n"
        "║                              ║\n"
        "║ ⚙️ Workers: 1 / 1            ║\n"
        "╚══════════════════════════════╝"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Refresh",
                    callback_data="dashboard_workers"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Dashboard",
                    callback_data="dashboard_refresh"
                )
            ]
        ]
    )

    try:

        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception:

        pass


# =========================================================
# URL HANDLER
# =========================================================

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):

    users.add(
        message.from_user.id
    )

    url = message.text.strip()

    user_id = message.from_user.id

    lower_url = url.lower()

    if (
        "tiktok.com" not in lower_url
        and
        "instagram.com" not in lower_url
    ):

        await message.answer(
            "❌ <b>رابط غير مدعوم</b>\n\n"
            "أرسل رابط TikTok أو Instagram.",
            parse_mode="HTML"
        )

        return

    user_urls[user_id] = url

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔥 أفضل جودة",
                    callback_data="best"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎥 720p",
                    callback_data="720"
                ),
                InlineKeyboardButton(
                    text="📱 480p",
                    callback_data="480"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 حجم صغير",
                    callback_data="small"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎵 MP3",
                    callback_data="mp3"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ إلغاء",
                    callback_data="cancel"
                )
            ]
        ]
    )

    await message.answer(
        "╔══════════════════════════════╗\n"
        "║          ⚡ KARAM BOT         ║\n"
        "╚══════════════════════════════╝\n\n"

        "✅ تم استلام الرابط بنجاح.\n\n"

        "اختر جودة التحميل:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# =========================================================
# DOWNLOAD FUNCTION
# =========================================================

def download_media(
    url,
    quality,
    folder
):

    output = os.path.join(
        folder,
        "%(title).80s.%(ext)s"
    )

    if quality == "mp3":

        options = {

            "format":
                "bestaudio/best",

            "outtmpl":
                output,

            "noplaylist":
                True,

            "socket_timeout":
                20,

            "retries":
                5,

            "fragment_retries":
                5,

            "quiet":
                True,

            "no_warnings":
                True,

            "nocheckcertificate":
                True,

            "restrictfilenames":
                True,

            "postprocessors": [
                {
                    "key":
                        "FFmpegExtractAudio",

                    "preferredcodec":
                        "mp3",

                    "preferredquality":
                        "192",
                }
            ],
        }

    else:

        formats = {

            "best":
                "best[ext=mp4][filesize<49M]/"
                "best[filesize<49M]/best",

            "720":
                "best[height<=720][ext=mp4][filesize<49M]/"
                "best[height<=720][filesize<49M]/best",

            "480":
                "best[height<=480][ext=mp4][filesize<49M]/"
                "best[height<=480][filesize<49M]/best",

            "small":
                "best[height<=360][ext=mp4][filesize<30M]/"
                "best[height<=360][filesize<30M]/worst",
        }

        options = {

            "format":
                formats[quality],

            "outtmpl":
                output,

            "noplaylist":
                True,

            "socket_timeout":
                20,

            "retries":
                5,

            "fragment_retries":
                5,

            "quiet":
                True,

            "no_warnings":
                True,

            "nocheckcertificate":
                True,

            "restrictfilenames":
                True,
        }

    with yt_dlp.YoutubeDL(
        options
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        title = info.get(
            "title",
            "Video"
        )

        filename = ydl.prepare_filename(
            info
        )

    if quality == "mp3":

        filename = (
            os.path.splitext(filename)[0]
            + ".mp3"
        )

    if os.path.exists(filename):

        return filename, title

    for file in Path(folder).iterdir():

        if quality == "mp3":

            if file.suffix.lower() == ".mp3":

                return str(file), title

        else:

            if file.suffix.lower() in (
                ".mp4",
                ".webm",
                ".mkv",
                ".mov"
            ):

                return str(file), title

    raise FileNotFoundError(
        "لم يتم العثور على الملف"
    )


# =========================================================
# DOWNLOAD HANDLER
# =========================================================

@dp.callback_query(
    F.data.in_(
        [
            "best",
            "720",
            "480",
            "small",
            "mp3"
        ]
    )
)
async def download_handler(
    callback: CallbackQuery
):

    global download_count
    global active_jobs
    global completed_jobs
    global failed_jobs

    user_id = callback.from_user.id

    url = user_urls.get(
        user_id
    )

    if not url:

        await callback.answer(
            "❌ أرسل الرابط من جديد.",
            show_alert=True
        )

        return

    quality = callback.data

    names = {

        "best":
            "🔥 أفضل جودة",

        "720":
            "🎥 720p",

        "480":
            "📱 480p",

        "small":
            "💾 حجم صغير",

        "mp3":
            "🎵 MP3",
    }

    await callback.answer()

    try:

        await callback.message.edit_reply_markup(
            reply_markup=None
        )

    except Exception:

        pass

    status = await callback.message.answer(
        "⏳ <b>KARAM BOT</b>\n\n"
        "جاري التحميل...\n\n"
        f"📌 {names[quality]}",
        parse_mode="HTML"
    )

    folder = tempfile.mkdtemp(
        prefix="karam_bot_"
    )

    active_jobs += 1

    try:

        loop = asyncio.get_running_loop()

        file_path, title = (
            await loop.run_in_executor(
                None,
                download_media,
                url,
                quality,
                folder
            )
        )

        max_size = (
            49 *
            1024 *
            1024
        )

        if os.path.getsize(
            file_path
        ) > max_size:

            failed_jobs += 1

            await status.edit_text(
                "❌ الملف أكبر من الحد المسموح."
            )

            return

        await status.edit_text(
            "📤 <b>جاري إرسال الملف...</b>",
            parse_mode="HTML"
        )

        caption = (
            "⚡ <b>KARAM BOT</b>\n\n"
            f"🎬 {title}\n"
            f"📌 {names[quality]}\n\n"
            "━━━━━━━━━━━━━━━━━━"
        )

        if quality == "mp3":

            await callback.message.answer_audio(
                audio=FSInputFile(
                    file_path
                ),
                caption=caption,
                parse_mode="HTML"
            )

        else:

            await callback.message.answer_video(
                video=FSInputFile(
                    file_path
                ),
                caption=caption,
                supports_streaming=True,
                parse_mode="HTML"
            )

        download_count += 1
        completed_jobs += 1

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 تحميل رابط آخر",
                        callback_data="retry"
                    )
                ]
            ]
        )

        await callback.message.answer(
            "━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>KARAM BOT</b>\n\n"
            "✅ تم التحميل بنجاح\n\n"
            "يمكنك إرسال رابط جديد.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        try:

            await status.delete()

        except Exception:

            pass

    except Exception as error:

        failed_jobs += 1

        logging.exception(
            "Download error: %s",
            error
        )

        try:

            await status.edit_text(
                "❌ <b>حدث خطأ أثناء التحميل</b>\n\n"
                "جرّب إرسال رابط آخر.",
                parse_mode="HTML"
            )

        except Exception:

            pass

    finally:

        active_jobs -= 1

        try:

            for file in Path(
                folder
            ).glob("*"):

                try:
                    file.unlink()

                except Exception:
                    pass

            try:
                Path(folder).rmdir()

            except Exception:
                pass

        except Exception:

            pass

        user_urls.pop(
            user_id,
            None
        )


# =========================================================
# RETRY
# =========================================================

@dp.callback_query(
    F.data == "retry"
)
async def retry_handler(
    callback: CallbackQuery
):

    await callback.answer()

    await callback.message.answer(
        "🔗 <b>أرسل الرابط الجديد الآن</b>\n\n"
        "يدعم TikTok وInstagram.",
        parse_mode="HTML"
    )


# =========================================================
# CANCEL
# =========================================================

@dp.callback_query(
    F.data == "cancel"
)
async def cancel_handler(
    callback: CallbackQuery
):

    user_urls.pop(
        callback.from_user.id,
        None
    )

    await callback.answer(
        "تم الإلغاء"
    )

    await callback.message.edit_text(
        "❌ <b>تم إلغاء العملية.</b>\n\n"
        "⚡ KARAM BOT",
        parse_mode="HTML"
    )


# =========================================================
# RUN
# =========================================================

async def main():

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        )
    )

    print(
        "================================"
    )

    print(
        "⚡ KARAM BOT"
    )

    print(
        "🚀 Bot is running..."
    )

    print(
        "================================"
    )

    await dp.start_polling(
        bot
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
