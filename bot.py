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
    await message.answer("أهلاً بك يا صاحبي! البوت يعمل بالسرعة القصوى 🚀⚡")

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):
    url = message.text
    sent_msg = await message.answer("⚡ جاري جلب الفيديو بأقصى سرعة...")
    
    output_filename = f"video_{message.from_user.id}.mp4"
    
    # خيارات السرعة الخارقة والتجاوز السريع
    ydl_opts = {
        'format': 'b[filesize<45M]/b',
        'outtmpl': output_filename,
        'noplaylist': True,
        'socket_timeout': 10,
        'retries': 3,
        'fragment_retries': 3,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
    }
    
    try:
        loop = asyncio.get_running_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        await loop.run_in_executor(None, download)
        
        if os.path.exists(output_filename):
            video_file = FSInputFile(output_filename)
            await message.answer_video(video_file, caption="🔥 تفضل الفيديو بأعلى سرعة يا بطل!")
            os.remove(output_filename)
        else:
            await message.answer("❌ عذراً، لم أتمكن من تحميل الفيديو.")
            
    except Exception as e:
        await message.answer("❌ حدث خطأ مؤقت، أرسل الرابط مرة أخرى وسيعمل فوراً.")
        if os.path.exists(output_filename):
            os.remove(output_filename)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("البوت يعمل بالسرعة القصوى...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
