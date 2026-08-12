import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# قراءة التوكن بأمان من متغيرات البيئة في ريلواي
BOT_TOKEN = os.getenv("8827366261:AAFjunnspR2UP2L4cwsoERJTTGQtWN5wKJQ")

if not BOT_TOKEN:
    raise RuntimeError("8827366261:AAFjunnspR2UP2L4cwsoERJTTGQtWN5wKJQ is missing. 8827366261:AAFjunnspR2UP2L4cwsoERJTTGQtWN5wKJQ in Railway Variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("أهلاً بك يا إبراهيم! البوت يعمل الآن 24/7 بنجاح 🚀")

@dp.message()
async def handle_message(message: types.Message):
    url = message.text
    if url and "http" in url:
        await message.answer("جاري معالجة الطلب... ⏳")
    else:
        await message.answer("الرجاء إرسال رابط صحيح.")

async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
