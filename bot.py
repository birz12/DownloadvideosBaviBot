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
# 8827366261:AAG4qJnXspJKL85ASQmbOICahz5W_duGw90
# ==================================================

TOKEN = "8827366261:AAG4qJnXspJKL85ASQmbOICahz5W_duGw90"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_urls = {}
download_count = 0


# ==================================================
# START
# ==================================================

@dp.message(Command("start"))
async def start_handler(message: Message):

    await message.answer(
        "━━━━━━━━━━━━━━━━━━\n"
        "        👑 <b>KARAM BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🇬🇧 <b>Welcome to Karam Bot</b>\n"
        "Download your videos quickly and easily. 🎬\n\n"
        "🇦🇪 <b>أهلاً بك في بوت Karam</b>\n"
        "حمّل فيديوهاتك بسرعة وسهولة. 🎥\n\n"
        "⚡ Fast • Simple • High Quality\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )


# ==================================================
# STATS
# ==================================================

@dp.message(Command("stats"))
async def stats_handler(message: Message):

    await message.answer(
        f"📊 <b>KARAM BOT Statistics</b>\n\n"
        f"📥 Downloads: <b>{download_count}</b>",
        parse_mode="HTML"
    )


# ==================================================
# استقبال الرابط
# ==================================================

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):

    url = message.text.strip()
    user_id = message.from_user.id

    if (
        "tiktok.com" not in url.lower()
        and "instagram.com" not in url.lower()
    ):
        await message.answer(
            "❌ <b>رابط غير مدعوم</b>\n\n"
            "🇬🇧 Please send a TikTok or Instagram link.\n"
            "🇦🇪 أرسل رابط TikTok أو Instagram.",
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
        "━━━━━━━━━━━━━━━━━━\n"
        "        👑 <b>KARAM BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🇬🇧 <b>Welcome to Karam Bot</b>\n"
        "Your video link has been received successfully. 🎬\n\n"
        "🇦🇪 <b>أهلاً بك في بوت Karam</b>\n"
        "تم استلام رابط الفيديو بنجاح.\n"
        "اختر الجودة التي تريدها من الأسفل. 🎥\n\n"
        "⚡ Fast • Simple • High Quality\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# ==================================================
# تحميل الفيديو / MP3
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

        filename = ydl.prepare_filename(info)

    if quality == "mp3":
        filename = os.path.splitext(filename)[0] + ".mp3"

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


# ==================================================
# اختيار الجودة
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
        "best": "🔥 أفضل جودة",
        "720": "🎥 720p",
        "480": "📱 480p",
        "small": "💾 حجم صغير",
        "mp3": "🎵 MP3",
    }

    await callback.answer()

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    status = await callback.message.answer(
        f"⏳ <b>KARAM BOT</b>\n\n"
        f"جاري التحميل...\n"
        f"{names[quality]}",
        parse_mode="HTML"
    )

    folder = tempfile.mkdtemp(
        prefix="karam_bot_"
    )

    try:

        loop = asyncio.get_running_loop()

        file_path, title = await loop.run_in_executor(
            None,
            download_media,
            url,
            quality,
            folder
        )

        max_size = 49 * 1024 * 1024

        if os.path.getsize(file_path) > max_size:

            await status.edit_text(
                "❌ الملف أكبر من الحد المسموح."
            )
            return

        await status.edit_text(
            "📤 جاري إرسال الملف..."
        )

        caption = (
            f"👑 <b>KARAM BOT</b>\n\n"
            f"🎬 {title}\n"
            f"📌 {names[quality]}\n\n"
            f"⚡ Fast • Simple • High Quality"
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
                        text="🔄 تحميل رابط آخر",
                        callback_data="retry"
                    )
                ]
            ]
        )

        await callback.message.answer(
            "━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>KARAM BOT</b>\n\n"
            "🇬🇧 <b>Download completed successfully!</b> ✅\n"
            "🇦🇪 <b>تم تحميل الفيديو بنجاح!</b> ✅\n"
            "━━━━━━━━━━━━━━━━━━",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        await status.delete()

    except Exception as error:

        logging.exception(
            "Download error: %s",
            error
        )

        await status.edit_text(
            "❌ <b>حدث خطأ أثناء التحميل</b>\n\n"
            "🇬🇧 Please try another link.\n"
            "🇦🇪 جرّب إرسال الرابط مرة أخرى.",
            parse_mode="HTML"
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
# تحميل رابط آخر
# ==================================================

@dp.callback_query(F.data == "retry")
async def retry_handler(
    callback: CallbackQuery
):

    await callback.answer()

    await callback.message.answer(
        "👑 <b>KARAM BOT</b>\n\n"
        "🇬🇧 <b>Welcome back!</b>\n"
        "Send your TikTok or Instagram link again. 🎬\n\n"
        "🇦🇪 <b>أهلاً بك مجددًا!</b>\n"
        "أرسل رابط TikTok أو Instagram مرة أخرى. 🎥",
        parse_mode="HTML"
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
        "❌ <b>تم إلغاء العملية.</b>\n\n"
        "👑 KARAM BOT",
        parse_mode="HTML"
    )


# ==================================================
# تشغيل البوت
# ==================================================

async def main():

    logging.basicConfig(
        level=logging.INFO
    )

    print(
        "🤖 KARAM BOT is running..."
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(main())
