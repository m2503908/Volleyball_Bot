# подключаем нужные библиотеки
import os
from datetime import timezone

from dotenv import load_dotenv
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm import state
from aiogram.fsm.state import default_state, State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from work_with_users_data import *
from create_database import init_db

# так скажем "стартовая конфигурация"
init_db() # инициализация бд
load_dotenv() # подгружаем скрытый от гита файл
BOT_TOKEN = os.getenv("BOT_TOKEN") # берем из этого файла токен бота
ADMINS = find_admin() # переменная, хранящая

# инициализируем бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# инициализируем отправку по времени
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# класс FSMFill отвечает за ответы на некоторые сообщения бота
class FSMFill(StatesGroup):
    fill_link1 = State()
    fill_link2 = State()
    fill_name = State()
    fill_surname = State()
    fill_role = State()
    fill_flag = State()
    fill_form_answer = State()


# описание команды /start
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


# описание команды /register
@dp.message(Command(commands='register'), StateFilter(default_state))
async def register_command(message: Message, state: FSMContext):
    await message.answer("Введите имя в формате Фамилия Имя. \n\nПример: \nИванов Иван")
    await state.set_state(FSMFill.fill_name) # ставим FSMFill в состояние ожидания ответа


# процесс регистрации
@dp.message(StateFilter(FSMFill.fill_name))
async def process_register(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    user_surname, user_name = message.text.split(' ')
    user_username = check_surname_name(user_surname, user_name)
    if user_username: # проверяем есть ли какие-то данные о пользователе в бд
        update_username(user_surname, user_name, user_username)
        #print("PAM PAM", user_surname, user_name, message.from_user.username)
    else:
        if check_username(message.from_user.username)[0]:
            update_surname_name(user_surname, user_name, message.from_user.username)
            #print("PIM PIM")
        else:
            add_user(message.from_user.username, user_surname, user_name, message.from_user.id, subscribe=0) # добавляем пользователя в бд
    await message.answer("Регистрация прошла успешно! Ожидайте ссылку на google-форму!")
    await state.clear()


# описание команды /add_link, доступна только админам
@dp.message(Command(commands="add_link"), StateFilter(default_state))
async def add_link_command(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS: # проверка является ли пользователь админом
        await message.answer("У вас нет доступа к этой команде!")
    else:
        await message.answer("Введите ссылку на следующее голосование в гугл формах:")
        await state.set_state(FSMFill.fill_link1)

 #вспомогательная функция6 для обработки ответа после использования комнады /add_link
@dp.message(StateFilter(FSMFill.fill_link1))
async def process_add_link1(message: Message, state: FSMContext):
    await state.update_data(link1=message.text)
    #await message.answer('Ссылка сохранена ' + message.text)
    add_link_db("date", message.text, 0, 0) # заносим ссылку в базу данных
    await message.answer(f'Ссылка на гугл форму сохранена!')
    await state.clear()
    #await state.set_state(FSMFill.fill_link2)


#вторая вспомогательная функция /add_link. пока не используется, но возможно это временно
"""@dp.message(StateFilter(FSMFill.fill_link2))
async def process_add_link2(message: Message, state: FSMContext):
    await state.update_data(link2=message.text)
    #await message.answer('Ссылка сохранена ' + message.text)
    await message.answer(f'Ссылка на ответы сохранена! {message.text}')
    await state.clear()"""


# функция для формирования внутренней клавиатуры, в которой можно будет выбрать фамилию и имя пользователя, права которого мы хоти м изменить
def surname_name_keyboard(surnames_names, role):
    keyboard = []

    for surname_name in surnames_names:
        keyboard.append([
            InlineKeyboardButton(
                text=surname_name,
                callback_data=f"{surname_name} {role}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# определяем команду /change_rights, она доступна только админам и служит для изменения прав остальных пользователей
@dp.message(Command(commands="change_rights"), StateFilter(default_state))
async def change_rights_command(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас нет доступа к этой команде!")
    else:
        #surnames_names = get_surname_name()
        keyboard = [ #создание шаблона инлайн клавиатуры
            [InlineKeyboardButton(
                text="Админ",
                callback_data="admin"
            )],
            [InlineKeyboardButton(
                text="Абонимент",
                callback_data="subscribe"
            )]
        ]
        await state.set_state(FSMFill.fill_role)
        await message.answer("Выберите какую роль вы хотите добавить/убрать:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
        #await message.answer("Выберите фамилию и имя пользователя, которому хотите добавить абонимент:", reply_markup=surname_name_keyboard(surnames_names))


# вспомогательная функция для изменения прав пользователя
@dp.callback_query(StateFilter(FSMFill.fill_role))
async def process_change_rights1(callback: CallbackQuery, state: FSMContext):
    keyboard = [ # создание шаблона инлайн клавиатуры
        [InlineKeyboardButton(
            text="Добавить роль",
            callback_data=f"{callback.data} 1"
        )],
        [InlineKeyboardButton(
            text="Убрать роль",
            callback_data=f"{callback.data} 0"
        )]
    ]
    await state.set_state(FSMFill.fill_flag)
    await callback.message.edit_text("Выберите что вы хотите сделать с ролью: добавить или убрать", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


# вспомогательная функция для изменения прав пользователя
@dp.callback_query(StateFilter(FSMFill.fill_flag))
async def process_change_rights2(callback: CallbackQuery, state: FSMContext):
    surnames_names = get_surname_name()
    await callback.message.edit_text("Выберите фамилию и имя пользователя, которому хотите добавить роль:", reply_markup=surname_name_keyboard(surnames_names, callback.data))
    await state.set_state(FSMFill.fill_surname)


# вспомогательная функция для изменения прав пользователя
@dp.callback_query(StateFilter(FSMFill.fill_surname))
async def process_change_rights3(callback: CallbackQuery, state: FSMContext):
    surname, name, role, flag = callback.data.split()
    change_rights(surname, name, role, flag)
    try: # используем try except на случай, если пользователь заблокировал бота
        await bot.send_message(chat_id=get_id_by_name(surname, name), text=f"Ваши права изменены! \nВам {'добавили' if flag == "1" else 'удалили'} роль {'"Админ"' if role == 'admin' else '"Абонимент"'}!")
        await callback.message.edit_text(
            f"Вы выбрали: {surname} {name}. \nРоль {'"Админ"' if role == 'admin' else '"Абонимент"'} {'добавлена' if flag == "1" else 'удалена'} для этого пользователя.")
    except Exception:
        await callback.message.edit_text(f"Пользователь {surname} {name} заблокировал бота, но изменения прошли успешно и нужные данные зафиксированы в базе данных.")
    global ADMINS
    ADMINS = find_admin() # обновление списка админов, в случае если права какого-то пользователя были изменены


# функция, отвечающая за отправку сообщения с ссылкой на гугл форму
async def send_link():
    for user_id in find_subscribe():
        try: # try-except на случай, если какой-то пользователь заблокировал бота
            keyboard = [ # создание шаблона инлайн клавиатуры
                [InlineKeyboardButton(
                    text="Буду в пт",
                    callback_data="answer 1 0"
                )],
                [InlineKeyboardButton(
                    text="Буду в сб",
                    callback_data="answer 0 1"
                )],
                [InlineKeyboardButton(
                    text="Буду и в пт, и в сб",
                    callback_data="answer 1 1"
                )],
                [InlineKeyboardButton(
                    text="Меня не будет",
                    callback_data="answer 0 0"
                )]
            ]
            await bot.send_message(chat_id=user_id, text=f"Ссылка на форму: \n\n{get_last_link()}", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
        except Exception as e:
            print("пользователь заблокировал бота")
            print(e)


# ответ, получаемый пользователем после взаимодействия с инлайн клавиатурой
@dp.callback_query(F.data.startswith("answer"))
async def form_answer(callback: CallbackQuery):
    await callback.message.edit_text(f"Ссылка на форму: \n\n{get_last_link()}. \n\n Вы выбрали вариант: {callback.data}")


# главная функция
async def main():
    scheduler.add_job(send_link, trigger='cron', day_of_week='fri', hour='9', minute='13', timezone='Europe/Moscow') #устанавливаем время, в которое срабатывает функция отправки ссылки
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
