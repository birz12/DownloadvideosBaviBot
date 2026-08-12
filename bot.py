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
    await message.answer("أهلاً بك يا صاحبي! أنا بوتك الشخصي للتحميل. أرسل لي أي رابط وسأكون جاهزاً لخدمتك كل يوم.")

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):
    url = message.text
    sent_msg = await message.answer(f"استلمت الرابط بنجاح!\n\n⏳ جاري تحميل الفيديو وإرساله لك...")
    
    output_filename = "downloaded_video.mp4"
    
    # إعدادات التحميل بواسطة yt-dlp
    ydl_opts = {
        'format': 'mp4/best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024, # حد أقصى 50 ميجابايت لتليجرام
    }
    
    try:
        # تنفيذ التحميل في الخلفية
        loop = asyncio.get_running_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        await loop.run_in_executor(None, download)
        
        # التأكد من تحميل الملف ثم إرساله
        if os.path.exists(output_filename):
            video_file = FSInputFile(output_filename)
            await message.answer_video(video_file, caption="✅ تفضل الفيديو يا بطل!")
            os.remove(output_filename) # حذف الملف من السيرفر بعد الإرسال لتنظيف المساحة
        else:
            await message.answer("❌ عذراً، لم أتمكن من تحميل الفيديو.")
            
    except Exception as e:
        await message.answer(f"❌ حدث خطأ أثناء التحميل: {str_err(e) if 'str_err' in globals() else str(e)}")
        if os.path.exists(output_filename):
            os.remove(output_filename)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("البوت يعمل الآن وجاهز لاستقبال الرسائل...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
