import asyncio
import logging
import os
import tempfile
from pathlib import Path

import yt_dlp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# ==================================================
# 8827366261:AAEoY-zpvmL_eacowM2OjAJaRXpcGce2D6Y
# ==================================================

TOKEN = "8827366261:AAEoY-zpvmL_eacowM2OjAJaRXpcGce2D6Y"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_urls = {}


# ==================================================
# START
# ==================================================

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "👋 أهلاً بك!\n\n"
        "🎬 أرسل رابط TikTok أو Instagram\n"
        "ثم اختر جودة الفيديو."
    )


# ==================================================
# استقبال الرابط
# ==================================================

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):

    url = message.text.strip()
    user_id = message.from_user.id

    if not (
        "tiktok.com" in url.lower()
        or "instagram.com" in url.lower()
    ):
        await message.answer(
            "❌ أرسل رابط TikTok أو Instagram فقط."
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
                    text="❌ إلغاء",
                    callback_data="cancel"
                )
            ],
        ]
    )

    await message.answer(
        "🎬 تم استلام الرابط.\n\n"
        "اختر الجودة:",
        reply_markup=keyboard
    )


# ==================================================
# تحميل الفيديو
# ==================================================

def download_video(url, quality, folder):

    output = os.path.join(
        folder,
        "%(id)s.%(ext)s"
    )

    formats = {

        "best":
            "best[ext=mp4][filesize<49M]/best[filesize<49M]/best",

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
        "format": formats[quality],
        "outtmpl": output,
        "noplaylist": True,
        "socket_timeout": 20,
        "retries": 5,
        "fragment_retries": 5,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "restrictfilenames": True,
        "http_headers": {
            "User-Agent":
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
        },
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)

    if os.path.exists(filename):
        return filename

    base = os.path.splitext(filename)[0]

    for extension in [".mp4", ".webm", ".mkv", ".mov"]:

        file = base + extension

        if os.path.exists(file):
            return file

    for file in Path(folder).iterdir():

        if file.suffix.lower() in (
            ".mp4",
            ".webm",
            ".mkv",
            ".mov"
        ):
            return str(file)

    raise FileNotFoundError(
        "Video file not found"
    )


# ==================================================
# أزرار الجودة
# ==================================================

@dp.callback_query(F.data.in_(
    ["best", "720", "480", "small"]
))
async def quality_handler(callback: CallbackQuery):

    user_id = callback.from_user.id
    url = user_urls.get(user_id)

    if not url:

        await callback.answer(
            "❌ أرسل الرابط من جديد.",
            show_alert=True
        )
        return

    quality = callback.data

    names = {
        "best": "🔥 أفضل جودة",
        "720": "🎥 720p",
        "480": "📱 480p",
        "small": "💾 حجم صغير",
    }

    await callback.answer()

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    status = await callback.message.answer(
        f"⏳ جاري التحميل...\n{names[quality]}"
    )

    folder = tempfile.mkdtemp(
        prefix="telegram_video_"
    )

    try:

        loop = asyncio.get_running_loop()

        video_path = await loop.run_in_executor(
            None,
            download_video,
            url,
            quality,
            folder
        )

        max_size = 49 * 1024 * 1024

        if os.path.getsize(video_path) > max_size:

            await status.edit_text(
                "❌ حجم الفيديو أكبر من الحد المسموح."
            )
            return

        await status.edit_text(
            "📤 جاري إرسال الفيديو..."
        )

        await callback.message.answer_video(
            FSInputFile(video_path),
            supports_streaming=True,
            caption=f"✅ تم التحميل\n{names[quality]}"
        )

        await status.delete()

    except Exception as error:

        logging.exception(error)

        await status.edit_text(
            "❌ لم أستطع تحميل الفيديو.\n"
            "جرّب رابطًا آخر."
        )

    finally:

        try:

            for file in Path(folder).glob("*"):
                file.unlink()

            Path(folder).rmdir()

        except Exception:
            pass

        user_urls.pop(
            user_id,
            None
        )


# ==================================================
# إلغاء
# ==================================================

@dp.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery):

    user_urls.pop(
        callback.from_user.id,
        None
    )

    await callback.answer("تم الإلغاء")

    await callback.message.edit_text(
        "❌ تم إلغاء التحميل."
    )


# ==================================================
# تشغيل البوت
# ==================================================

async def main():

    logging.basicConfig(
        level=logging.INFO
    )

    print("🤖 البوت يعمل...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
