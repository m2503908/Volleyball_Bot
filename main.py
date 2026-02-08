import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm import state
from aiogram.fsm.state import default_state, State, StatesGroup

from work_with_users_data import add_user, check_username, check_surname_name, update_username, update_surname_name, find_admin
from create_database import init_db

init_db()
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = find_admin()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class FSMFill(StatesGroup):
    fill_link = State()
    fill_name = State()


@dp.message(Command(commands="start"), StateFilter(default_state))
async def process_start_command(message: Message):
    user_username = message.from_user.username
    user_surname, user_name = check_username(user_username)
    if user_name:
        await message.answer(
            f'Здравствуйте! Убедитесь, что ваше имя было правильно распознанно:\n{user_surname} {user_name} \n\n'
            f'Если имя (или фамилия) распознаны неверно, то воспользуйтесь следующей командой: \n/register')
    else:
        await message.answer(f'Здравствуйте! Перед началом работы воспользуйтесь командой /register')


@dp.message(Command(commands='register'), StateFilter(default_state))
async def register_command(message: Message, state: FSMContext):
    await message.answer("Введите имя в формате Фамилия Имя. \n\nПример: \nИванов Иван")
    await state.set_state(FSMFill.fill_name)


@dp.message(StateFilter(FSMFill.fill_name))
async def process_register(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_surname, user_name = message.text.split(' ')
    user_username = check_surname_name(user_surname, user_name)
    if user_username:
        update_username(user_surname, user_name, user_username)
        #print("PAM PAM", user_surname, user_name, message.from_user.username)
    else:
        if check_username(message.from_user.username)[0]:
            update_surname_name(user_surname, user_name, message.from_user.username)
            #print("PIM PIM")
        else:
            add_user(message.from_user.username, user_surname, user_name, message.from_user.id, subscribe=0)
    await state.clear()


@dp.message(Command(commands="add_link"), StateFilter(default_state))
async def add_link_command(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас нет доступа к этой команде!")
    else:
        await message.answer("Введите ссылку на следующее голосование в гугл формах:")
        await state.set_state(FSMFill.fill_link)


@dp.message(StateFilter(FSMFill.fill_link))
async def process_add_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer('Ссылка сохранена ' + message.text)
    await state.clear()


@dp.message(Command(commands="add_subscribe"), StateFilter(default_state))
async def add_subscribe_command(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас нет доступа к этой команде!")
    else:
        pass


if __name__ == '__main__':
    dp.run_polling(bot)
