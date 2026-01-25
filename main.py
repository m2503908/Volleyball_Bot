import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands="start"))
async def process_start_command(message: Message):
    await message.answer('Здравствуйте! Убедитесь, что мы правильно распознали ваше имя: Имя1')


if __name__ == '__main__':
    dp.run_polling(bot)