import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8827366261:AAHfOT0tTQr-XdY1_J1BNUtU8exsA1CjgPU"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("أهلاً بك يا صاحبي! أنا بوتك الشخصي للتحميل. أرسل لي أي رابط وسأكون جاهزاً لخدمتك كل يوم.")

@dp.message(F.text.startswith("http"))
async def link_handler(message: Message):
    await message.answer(f"استلمت الرابط بنجاح: {message.text}\n\n(جاري إعداد محرك التحميل الكامل لك...)")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("البوت يعمل الآن وجاهز لاستقبال الرسائل...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
