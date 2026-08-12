import asyncio
import logging
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

TOKEN = "8827366261:AAHfOT0tTQr-XdY1_J1BNUtU8exsA1CjgPU"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("أهلاً بك يا صاحبي! البوت جاهز وبأقصى سرعة 🚀")

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):
    url = message.text
    sent_msg = await message.answer("⚡ جاري التحميل بسرعة صاروخية...")
    
    output_filename = f"video_{message.from_user.id}.mp4"
    
    # إعدادات السرعة: اختيار صيغة سريعة وخفيفة لتجنب التعليق
    ydl_opts = {
        'format': 'best[filesize<40M]/best',
        'outtmpl': output_filename,
        'noplaylist': True,
    }
    
    try:
        loop = asyncio.get_running_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        await loop.run_in_executor(None, download)
        
        if os.path.exists(output_filename):
            video_file = FSInputFile(output_filename)
            await message.answer_video(video_file, caption="🔥 تفضل الفيديو يا بطل!")
            os.remove(output_filename)
        else:
            await message.answer("❌ عذراً، لم أتمكن من تحميل الفيديو.")
            
    except Exception as e:
        await message.answer(("❌ حدث خطأ أثناء التحميل"))
        if os.path.exists(output_filename):
            os.remove(output_filename)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("البوت يعمل بأقصى سرعة...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
