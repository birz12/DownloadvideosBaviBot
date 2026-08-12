import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# التوكن مثبت هنا مباشرة لكي يعمل البوت فوراً بدون أخطاء
BOT_TOKEN = "8827366261:AAHC2NIScYTOWZmDt0_VFxacTMuY-KaOq8w"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("أهلاً بك يا إبراهيم! البوت شغال الآن بفضل الله وبدون أي مشاكل 🚀🔥")

@dp.message()
async def handle_message(message: types.Message):
    url = message.text
    if url and "http" in url:
        await message.answer("جاري معالجة الرابط وتحميل الفيديو... ⏳")
    else:
        await message.answer("الرجاء إرسال رابط صحيح لتحميله.")

async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
