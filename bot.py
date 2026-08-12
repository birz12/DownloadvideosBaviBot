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
# 8827366261:AAFOl4TjyYGRKK4D7KJUT1ZkNZV4ZfOjkEE
# ==================================================

TOKEN = "8827366261:AAFOl4TjyYGRKK4D7KJUT1ZkNZV4ZfOjkEE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==================================================
# بيانات مؤقتة
# ==================================================

user_urls = {}
download_count = 0


# ==================================================
# /start
# ==================================================

@dp.message(Command("start"))
async def start_handler(message: Message):

    await message.answer(
        "🎬 <b>Video Downloader</b>\n\n"
        "أرسل رابط فيديو من:\n"
        "• TikTok\n"
        "• Instagram\n\n"
        "⚡ وبعدها اختر الجودة أو MP3.",
        parse_mode="HTML"
    )


# ==================================================
# /stats
# ==================================================

@dp.message(Command("stats"))
async def stats_handler(message: Message):

    await message.answer(
        f"📊 <b>إحصائيات البوت</b>\n\n"
        f"📥 عدد التحميلات: <b>{download_count}</b>",
        parse_mode="HTML"
    )


# ==================================================
# استقبال الرابط
# ==================================================

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):

    url = message.text.strip()

    if (
        "tiktok.com" not in url.lower()
        and "instagram.com" not in url.lower()
    ):
        await message.answer(
            "❌ الرابط غير مدعوم.\n\n"
            "أرسل رابط TikTok أو Instagram."
        )
        return

    user_id = message.from_user.id

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
        "🎬 <b>تم استقبال الرابط</b>\n\n"
        "اختر ماذا تريد:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# تحميل الفيديو / الصوت
# ==================================================

def download_media(url, quality, folder):

    if quality == "mp3":

        output = os.path.join(
            folder,
            "%(title).80s.%(ext)s"
        )

        options = {
            "format": "bestaudio/best",
            "outtmpl": output,
            "noplaylist": True,
            "socket_timeout": 20,
            "retries": 5,
            "fragment_retries": 5,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "restrictfilenames": True,

            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],

            "http_headers": {
                "User-Agent":
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
            },
        }

    else:

        output = os.path.join(
            folder,
            "%(title).80s.%(ext)s"
        )

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

        title = info.get(
            "title",
            "Video"
        )

        thumbnail = info.get(
            "thumbnail"
        )

        filename = ydl.prepare_filename(info)

    if quality == "mp3":

        filename = os.path.splitext(
            filename
        )[0] + ".mp3"

    if os.path.exists(filename):

        return filename, title, thumbnail

    for file in Path(folder).iterdir():

        if quality == "mp3":

            if file.suffix.lower() == ".mp3":
                return str(file), title, thumbnail

        else:

            if file.suffix.lower() in (
                ".mp4",
                ".webm",
                ".mkv",
                ".mov"
            ):
                return str(file), title, thumbnail

    raise FileNotFoundError(
        "لم يتم العثور على الملف."
    )


# ==================================================
# أزرار الجودة
# ==================================================

@dp.callback_query(
    F.data.in_(
        ["best", "720", "480", "small", "mp3"]
    )
)
async def download_handler(
    callback: CallbackQuery
):

    global download_count

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
        f"⏳ جاري التحميل...\n"
        f"{names[quality]}"
    )

    folder = tempfile.mkdtemp(
        prefix="video_bot_"
    )

    try:

        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(
            None,
            download_media,
            url,
            quality,
            folder
        )

        file_path, title, thumbnail = result

        max_size = 49 * 1024 * 1024

        if os.path.getsize(file_path) > max_size:

            await status.edit_text(
                "❌ الملف أكبر من الحد المسموح به."
            )
            return

        await status.edit_text(
            "📤 جاري إرسال الملف..."
        )

        caption = (
            f"✅ <b>تم التحميل</b>\n\n"
            f"🎬 {title}\n"
            f"📌 {names[quality]}"
        )

        if quality == "mp3":

            await callback.message.answer_audio(
                audio=FSInputFile(file_path),
                caption=caption,
                parse_mode="HTML"
            )

        else:

            await callback.message.answer_video(
                video=FSInputFile(file_path),
                caption=caption,
                supports_streaming=True,
                parse_mode="HTML"
            )

        download_count += 1

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 تحميل مرة أخرى",
                        callback_data="retry"
                    )
                ]
            ]
        )

        await callback.message.answer(
            "✨ ماذا تريد أن تفعل؟",
            reply_markup=keyboard
        )

        await status.delete()

    except Exception as error:

        logging.exception(
            "Download error: %s",
            error
        )

        await status.edit_text(
            "❌ حدث خطأ أثناء التحميل.\n\n"
            "تأكد أن الرابط عام وحاول مرة أخرى."
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
# إعادة التحميل
# ==================================================

@dp.callback_query(F.data == "retry")
async def retry_handler(
    callback: CallbackQuery
):

    await callback.answer()

    await callback.message.answer(
        "📎 أرسل الرابط مرة أخرى لتحميله."
    )


# ==================================================
# إلغاء
# ==================================================

@dp.callback_query(F.data == "cancel")
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
        "❌ تم إلغاء العملية."
    )


# ==================================================
# تشغيل البوت
# ==================================================

async def main():

    logging.basicConfig(
        level=logging.INFO
    )

    print(
        "🤖 البوت المطوّر يعمل..."
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(main())
