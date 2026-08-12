import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = os.getenv("8827366261:AAEq5IQCNq76skF8qERwYv6JGJN7j8ep06g")

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN غير موجود في Railway Variables")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "✅ البوت يعمل بنجاح!\n\n"
        "⚡ KARAM BOT"
    )


async def main():
    print("🚀 Starting bot...")

    me = await bot.get_me()

    print(f"✅ Connected: @{me.username}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
