import asyncio
import logging
import os
import re
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
# ضع TOKEN الجديد هنا
# ==================================================

TOKEN = "PUT_YOUR_NEW_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# حفظ روابط المستخدمين مؤقتًا
user_urls = {}


# ==================================================
# التحقق من الرابط
# ==================================================

def is_supported_url(url):

    patterns = [
        r"https?://(www\.)?instagram\.com/",
        r"https?://(www\.)?tiktok\.com/",
        r"https?://vm\.tiktok\.com/",
        r"https?://vt\.tiktok\.com/",
    ]

    return any(
        re.search(pattern, url, re.IGNORECASE)
        for pattern in patterns
    )


# ==================================================
# /start
# ==================================================

@dp.message(Command("start"))
async def start_handler(message: Message):

    await message.answer(
        "👋 أهلاً بك!\n\n"
        "🎬 أرسل رابط فيديو من:\n"
        "• TikTok\n"
        "• Instagram\n\n"
        "⚡ وسأعطيك خيارات الجودة."
    )


# ==================================================
# استقبال الرابط
# ==================================================

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):

    url = message.text.strip()

    if not is_supported_url(url):

        await message.answer(
            "❌ هذا الرابط غير مدعوم.\n\n"
            "أرسل رابط TikTok أو Instagram."
        )

        return

    user_id = message.from_user.id

    # حفظ الرابط
    user_urls[user_id] = url

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔥 أفضل جودة",
                    callback_data="quality_best"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎥 720p",
                    callback_data="quality_720"
                ),
                InlineKeyboardButton(
                    text="📱 480p",
                    callback_data="quality_480"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 حجم صغير",
                    callback_data="quality_small"
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
        "🎬 تم استقبال الرابط.\n\n"
        "اختر جودة الفيديو:",
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

    # أفضل جودة
    if quality == "best":

        video_format = (
            "best[ext=mp4][filesize<49M]/"
            "best[filesize<49M]/"
            "best"
        )

    # 720p
    elif quality == "720":

        video_format = (
            "best[height<=720][ext=mp4][filesize<49M]/"
            "best[height<=720][filesize<49M]/"
            "best"
        )

    # 480p
    elif quality == "480":

        video_format = (
            "best[height<=480][ext=mp4][filesize<49M]/"
            "best[height<=480][filesize<49M]/"
            "best"
        )

    # حجم صغير
    else:

        video_format = (
            "best[height<=360][ext=mp4][filesize<30M]/"
            "best[height<=360][filesize<30M]/"
            "worst"
        )

    options = {
        "format": video_format,
        "outtmpl": output,
        "noplaylist": True,

        "socket_timeout": 20,
        "retries": 5,
        "fragment_retries": 5,

        "continuedl": True,

        "nocheckcertificate": True,

        "quiet": True,
        "no_warnings": True,

        "restrictfilenames": True,

        "http_headers": {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
        }
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)

    # البحث عن الملف
    possible_files = [
        filename,
        os.path.splitext(filename)[0] + ".mp4",
        os.path.splitext(filename)[0] + ".webm",
        os.path.splitext(filename)[0] + ".mkv",
    ]

    for file in possible_files:

        if os.path.exists(file):
            return file

    # بحث داخل المجلد
    for file in Path(folder).iterdir():

        if file.suffix.lower() in [
            ".mp4",
            ".webm",
            ".mkv",
            ".mov"
        ]:
            return str(file)

    raise FileNotFoundError(
        "لم يتم العثور على الفيديو"
    )


# ==================================================
# اختيار الجودة
# ==================================================

@dp.callback_query(F.data.startswith("quality_"))
async def quality_handler(callback: CallbackQuery):

    user_id = callback.from_user.id

    url = user_urls.get(user_id)

    if not url:

        await callback.answer(
            "❌ انتهت صلاحية الرابط.",
            show_alert=True
        )

        return

    quality = callback.data.replace(
        "quality_",
        ""
    )

    names = {
        "best": "🔥 أفضل جودة",
        "720": "🎥 720p",
        "480": "📱 480p",
        "small": "💾 حجم صغير"
    }

    quality_name = names.get(
        quality,
        "الجودة"
    )

    await callback.answer()

    # إزالة الأزرار
    try:

        await callback.message.edit_reply_markup(
            reply_markup=None
        )

    except Exception:
        pass

    status = await callback.message.answer(
        f"⏳ جاري تحميل {quality_name}..."
    )

    # مجلد مؤقت
    temp_dir = tempfile.mkdtemp(
        prefix=f"video_{user_id}_"
    )

    try:

        loop = asyncio.get_running_loop()

        video_path = await loop.run_in_executor(
            None,
            download_video,
            url,
            quality,
            temp_dir
        )

        # فحص حجم الملف
        max_size = 49 * 1024 * 1024

        if os.path.getsize(video_path) > max_size:

            await status.edit_text(
                "❌ الفيديو أكبر من الحجم المسموح."
            )

            return

        await status.edit_text(
            "📤 تم التحميل، جاري الإرسال..."
        )

        video_file = FSInputFile(
            video_path
        )

        await callback.message.answer_video(
            video=video_file,
            supports_streaming=True,
            caption=(
                f"✅ تم التحميل\n"
                f"{quality_name}"
            )
        )

        await status.delete()

    except yt_dlp.utils.DownloadError:

        await status.edit_text(
            "❌ لم أتمكن من تحميل الفيديو.\n\n"
            "قد يكون الرابط خاصًا أو غير متاح."
        )

    except Exception as e:

        logging.exception(
            "Download error: %s",
            e
        )

        await status.edit_text(
            "❌ حدث خطأ أثناء التحميل.\n"
            "جرّب الرابط مرة أخرى."
        )

    finally:

        # حذف الملفات المؤقتة
        try:

            for file in Path(temp_dir).glob("*"):

                try:
                    file.unlink()
                except Exception:
                    pass

            try:
                Path(temp_dir).rmdir()
            except Exception:
                pass

        except Exception:
            pass

        # حذف الرابط من الذاكرة
        user_urls.pop(
            user_id,
            None
        )


# ==================================================
# زر الإلغاء
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

    try:

        await callback.message.edit_text(
            "❌ تم إلغاء التحميل."
        )

    except Exception:
        pass


# ==================================================
# تشغيل البوت
# ==================================================

async def main():

    logging.basicConfig(
        level=logging.INFO
    )

    print(
        "🤖 البوت يعمل..."
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":
    asyncio.run(main())
