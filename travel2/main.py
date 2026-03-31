import config
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from base import SQL  # подключение класса SQL из файла base

db = SQL('db.db')  # соединение с БД

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

#inline клавиатура для пользователя
buttons2 = [
        [InlineKeyboardButton(text="Новый запрос", callback_data="requests")],
        [InlineKeyboardButton(text="История запросов ", callback_data="history")],
        [InlineKeyboardButton(text="Посмотреть все ", callback_data="all")]
    ]
kb2 = InlineKeyboardMarkup(inline_keyboard=buttons2)

#когда пользователь написал сообщение
@dp.message()
async def start(message):
    id = message.from_user.id
    if not db.user_exist(id):#если пользователя нет в бд
        db.add_user(id)#добавляем
    status = db.get_field("users", id, "status")  # получаем статус пользователя
    db.update_field("users", id, "status", 1) #изменяем статус пользователя
    await message.answer("Главное меню:", reply_markup=kb2)#отправка сообщения с клавиатурой


    if status == 1: #Откуда летит
        s = message.text
        db.update_field("users", id, "where_fly_from", s)
        db.update_field("users", id, "status", 2)
        await message.answer("Куда вы хотите полететь:")

    elif status == 2: #Куда летит
        s = message.text
        db.update_field("users", id, "where_to_fly", s)
        db.update_field("users", id, "status", 3)
        await message.answer("Укажите ваш бюджет на поездку (например: 50000 руб:")

    elif status == 3: #Бюджет
        s = message.text
        db.update_field("users", id, "budget", s)
        db.update_field("users", id, "status", 4)
        return_flight_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="return_flight_yes")],
            [InlineKeyboardButton(text="Нет", callback_data="return_flight_no")]
        ])
        await message.answer("Планируете ли вы обратный рейс?" , reply_markup=return_flight_keyboard)

    elif status == 4:  # Обратный рейс
        s = message.text

        db.update_field("users", id, "status", 5)
        await message.answer("Пожалуйста, выберите один из вариантов ниже.", reply_markup=return_flight_keyboard)

    elif status == 5:  # Количество звезд отеля
        s = message.text
        db.update_field("users", id, "hotel_stars", s)
        db.update_field("users", id, "status", 6)
        await message.answer("Пожалуйста, укажите дату вылета (число, месяц, год). Например: 15.03.2024")
    elif status == 6:  # Дата вылета (число, месяц, год)
        s = message.text
        db.update_field("users", id, "departure_date", s)
        db.update_field("users", id, "status", 7)
        await message.answer("Укажите примерное время вылета (например: 14:30).")
    elif status == 7:  # Время вылета
        departure_time = message.text
        db.update_field("users", id, "departure_time", departure_time)

        db.update_field("users", id, "status", 0)  # Сброс статуса после завершения ввода
        await message.answer(f"Ваш запрос принят!\n"
                             f"Откуда: {db.get_field('users', id, 'where_fly_from')}\n"
                             f"Куда: {db.get_field('users', id, 'where_to_fly')}\n"
                             f"Бюджет: {db.get_field('users', id, 'budget')}\n"
                             f"Обратный рейс: {'Да' if db.get_field('users', id, 'return_flight') == 1 else 'Нет'}\n"
                             f"Звездность отеля: {db.get_field('users', id, 'hotel_stars')}\n"
                             f"Дата вылета: {db.get_field('users', id, 'departure_date')}\n"
                             f"Время вылета: {db.get_field('users', id, 'departure_time')}\n",
                             reply_markup=kb2)

#когда пользователь нажал на inline кнопку
@dp.callback_query()
async def start_call(call):
    id = call.from_user.id
    if not db.user_exist(id):#если пользователя нет в бд
        db.add_user(id)#добавляем
    if call.data == "requests":
        await call.message.answer("Откуда вы хотите полететь?")
        await call.answer("Начинаем новый запрос!")  # Всплывающее уведомление

    elif call.data == "return_flight_yes":
        db.update_field("users", id, "return_flight", 1)  # 1 - Да
        db.update_field("users", id, "status", 5)  # Переход к следующему шагу - звезды отеля
        await call.message.answer("Укажите желаемую звездность отеля (например: 3 звезды):")
        await call.answer("Будет обратный рейс.")

    elif call.data == "return_flight_no":
        db.update_field("users", id, "return_flight", 0)  # 0 - Нет
        db.update_field("users", id, "status", 5)  # Переход к следующему шагу - звезды отеля
        await call.message.answer("Укажите желаемую звездность отеля (например: 3 звезды):")
        await call.answer("Обратного рейса не будет.")

        # if call.data == "yes": проверка нажатия на кнопку
        # await call.answer("Оповещение сверху")
        # await call.message.answer("Отправка сообщения")
        # await call.message.edit_text("Редактирование сообщения")
        # await call.message.delete()#удаление сообщения
    await bot.answer_callback_query(call.id)  # ответ на запрос, чтобы бот не зависал

    #if call.data == "yes": проверка нажатия на кнопку
    #await call.answer("Оповещение сверху")
    #await call.message.answer("Отправка сообщения")
    #await call.message.edit_text("Редактирование сообщения")
    #await call.message.delete()#удаление сообщения
    await bot.answer_callback_query(call.id)#ответ на запрос, чтобы бот не зависал

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
