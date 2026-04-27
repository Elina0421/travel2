import logging
import asyncio
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from base import SQL

# ===== НАСТРОЙКИ =====
TOKEN = "8768017671:AAGoRXpBgFir1wP177qPzBVvtVmcxa-Utm8"
TRAVELPAYOUTS_TOKEN = "4e7197b9501327a4a08e0d4469461e83"

db = SQL('db.db')
bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Словарь городов IATA для билетов
CITIES = {
    "москва": "MOW",
    "санкт-петербург": "LED",
    "спб": "LED",
    "сочи": "AER",
    "казань": "KZN",
    "екатеринбург": "SVX",
    "новосибирск": "OVB",
    "красноярск": "KJA",
    "иркутск": "IKT",
    "владивосток": "VVO",
    "стамбул": "IST",
    "анталья": "AYT",
    "лондон": "LON",
    "париж": "PAR",
    "берлин": "BER"
}

# Клавиатуры
main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✈️ ПОИСК БИЛЕТОВ", callback_data="search_tickets")],
    [InlineKeyboardButton(text="🏨 ПОИСК ОТЕЛЕЙ", callback_data="search_hotels")],
    [InlineKeyboardButton(text="📊 МОИ ДАННЫЕ", callback_data="all")]
])

flight_type_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔄 Туда и обратно", callback_data="flight_round")],
    [InlineKeyboardButton(text="➡️ Только туда", callback_data="flight_oneway")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
])

skip_budget_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⏩ ПРОПУСТИТЬ (любые билеты)", callback_data="skip_budget")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
])

hotel_stars_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⭐ 1 звезда", callback_data="hotel_stars_1"),
     InlineKeyboardButton(text="⭐⭐ 2 звезды", callback_data="hotel_stars_2")],
    [InlineKeyboardButton(text="⭐⭐⭐ 3 звезды", callback_data="hotel_stars_3"),
     InlineKeyboardButton(text="⭐⭐⭐⭐ 4 звезды", callback_data="hotel_stars_4")],
    [InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5 звезд", callback_data="hotel_stars_5"),
     InlineKeyboardButton(text="✨ ЛЮБЫЕ", callback_data="hotel_stars_any")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
])


# ===== ФУНКЦИИ ПОИСКА БИЛЕТОВ =====

def get_city_code(city_name):
    city_lower = city_name.lower().strip()
    if len(city_lower) == 3:
        return city_lower.upper()
    return CITIES.get(city_lower, city_lower.upper())


def get_airline_name(code):
    airlines = {
        "SU": "Аэрофлот", "S7": "S7 Airlines", "TK": "Turkish Airlines",
        "EK": "Emirates", "EY": "Etihad", "QR": "Qatar Airways",
        "LH": "Lufthansa", "BA": "British Airways", "AF": "Air France"
    }
    return airlines.get(code, code)


def search_flights(origin, destination, depart_date, budget=None):
    url = "https://api.travelpayouts.com/v1/prices/cheap"

    if len(depart_date) > 7:
        api_date = depart_date[:7]
    else:
        api_date = depart_date

    params = {
        "origin": origin,
        "destination": destination,
        "depart_date": api_date,
        "currency": "rub"
    }

    headers = {"X-Access-Token": TRAVELPAYOUTS_TOKEN}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if data.get('success') and data.get('data'):
                flights = []

                for dest, dest_data in data['data'].items():
                    if isinstance(dest_data, dict):
                        for flight_key, flight_data in dest_data.items():
                            if isinstance(flight_data, dict):
                                price = flight_data.get('price')

                                if budget and price and price > budget:
                                    continue

                                flights.append({
                                    'airline': flight_data.get('airline'),
                                    'price': price,
                                    'currency': 'RUB',
                                    'departure_at': flight_data.get('departure_at'),
                                    'origin': origin,
                                    'destination': dest,
                                    'link': f"https://www.aviasales.ru/search/{origin}{dest}1"
                                })

                flights.sort(key=lambda x: x['price'] if x['price'] else float('inf'))
                return flights
        return []
    except Exception as e:
        print(f"Ошибка поиска билетов: {e}")
        return []


def format_flights(flights, limit=20):
    if not flights:
        return "❌ Билеты не найдены.\n\nПопробуйте изменить дату или направление."

    result = f"✈️ *НАЙДЕНО БИЛЕТОВ: {len(flights)}*\n\n"

    for i, flight in enumerate(flights[:limit], 1):
        result += f"🎫 *ВАРИАНТ {i}*\n"
        result += f"💰 Цена: {flight['price']:,} RUB\n"
        result += f"🛫 Авиакомпания: {get_airline_name(flight['airline'])}\n"

        if flight.get('departure_at'):
            dep_date = flight['departure_at'].replace('T', ' ').replace('Z', '')[:16]
            result += f"📅 Вылет: {dep_date}\n"

        if flight.get('link'):
            result += f"🔗 [КУПИТЬ БИЛЕТ]({flight['link']})\n"

        result += "\n" + "─" * 35 + "\n"

    return result


# ===== ФУНКЦИИ ПОИСКА ОТЕЛЕЙ =====

def search_hotels(city, check_in, check_out, adults=2, min_stars=None, limit=15):
    """
    Поиск отелей через работающий API Hotellook
    """
    # Получаем IATA код города
    auto_url = "http://autocomplete.travelpayouts.com/places2"
    auto_params = {
        "term": city,
        "locale": "ru",
        "types[]": "city"
    }

    try:
        resp_auto = requests.get(auto_url, params=auto_params, timeout=10)
        if resp_auto.status_code != 200 or not resp_auto.json():
            print(f"❌ Город '{city}' не найден")
            return []

        city_code = resp_auto.json()[0].get('code')
        print(f"✅ Найден код для города '{city}': {city_code}")

        # 🔥 НОВЫЙ РАБОЧИЙ ЭНДПОИНТ
        hotels_url = "https://search.hotellook.com/search"

        params = {
            "location": city_code,
            "checkIn": check_in,
            "checkOut": check_out,
            "adults": adults,
            "currency": "rub",
            "limit": limit,
            "sort": "price",
            "lang": "ru"
        }

        response = requests.get(hotels_url, params=params, timeout=30)
        print(f"🏨 API отелей ответ: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            hotels_data = data.get('hotels', []) or data.get('results', [])

            hotels = []
            for hotel in hotels_data:
                hotel_stars = hotel.get('stars', 0) or hotel.get('starRating', 0)

                if min_stars and hotel_stars < min_stars:
                    continue

                hotels.append({
                    'name': hotel.get('name', 'Название не указано'),
                    'stars': hotel_stars,
                    'price_rub': int(hotel.get('price', 0)) if hotel.get('price') else None,
                    'currency': 'RUB',
                    'rating': hotel.get('rating'),
                    'reviews_count': hotel.get('reviewsCount', 0),
                    'address': hotel.get('address', ''),
                    'url': hotel.get('url') or f"https://hotellook.com/place?city={city_code}",
                })

            return hotels
        else:
            print(f"❌ Ошибка API отелей: {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ Ошибка поиска отелей: {e}")
        return []

def format_hotels(hotels, limit=15):
    """Форматирует результаты поиска отелей"""
    if not hotels:
        return "❌ Отели не найдены.\n\nПопробуйте:\n• Изменить даты\n• Уменьшить звездность"

    result = f"🏨 *НАЙДЕНО ОТЕЛЕЙ: {len(hotels)}*\n\n"

    for i, hotel in enumerate(hotels[:limit], 1):
        stars_emoji = "⭐" * hotel['stars'] if hotel['stars'] else "✨"

        result += f"🏨 *{i}. {hotel['name']}*\n"
        result += f"{stars_emoji} *{hotel['stars']} звезд*\n"

        if hotel.get('price_rub'):
            result += f"💰 Цена от: {hotel['price_rub']:,} RUB\n"

        if hotel.get('rating'):
            result += f"📊 Рейтинг: {hotel['rating']}/10 ({hotel['reviews_count']} отзывов)\n"

        if hotel.get('address'):
            result += f"📍 *Адрес:* {hotel['address'][:80]}\n"

        if hotel.get('url'):
            result += f"🔗 [ПОСМОТРЕТЬ ОТЕЛЬ]({hotel['url']})\n"

        result += "\n" + "─" * 40 + "\n"

    return result


# ===== ОБРАБОТЧИКИ =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    id = message.from_user.id
    if not db.user_exist(id):
        db.add_user(id)

    welcome_text = """
✈️ *ДОБРО ПОЖАЛОВАТЬ В TRAVEL BOT!*

Я помогу найти:
• ✈️ Авиабилеты по самым низким ценам
• 🏨 Отели с актуальными ценами

Нажмите на кнопку ниже, чтобы начать!
    """

    await message.answer(welcome_text, parse_mode='Markdown', reply_markup=main_keyboard)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
📚 *КАК ПОЛЬЗОВАТЬСЯ БОТОМ:*

*✈️ ПОИСК БИЛЕТОВ:*
1. Нажмите "ПОИСК БИЛЕТОВ"
2. Введите город вылета
3. Введите город назначения
4. Введите бюджет (или пропустите)
5. Введите дату вылета

*🏨 ПОИСК ОТЕЛЕЙ:*
1. Нажмите "ПОИСК ОТЕЛЕЙ"
2. Введите город
3. Выберите звездность
4. Введите дату заезда
5. Введите дату выезда
6. Введите количество гостей
    """
    await message.answer(help_text, parse_mode='Markdown')


@dp.message()
async def handle_message(message: types.Message):
    id = message.from_user.id
    text = message.text.strip()

    if not db.user_exist(id):
        db.add_user(id)

    status = db.get_field("users", id, "status")
    search_type = db.get_field("users", id, "search_type")

    # ===== ПОИСК БИЛЕТОВ =====
    if search_type == "flights":
        if status == 1:
            db.update_field("users", id, "where_fly_from", text)
            db.update_field("users", id, "status", 2)
            await message.answer("📍 *КУДА ЛЕТИМ?*", parse_mode='Markdown')

        elif status == 2:
            db.update_field("users", id, "where_to_fly", text)
            db.update_field("users", id, "status", 3)
            await message.answer(
                "💰 *БЮДЖЕТ НА БИЛЕТЫ?* (например: 30000)\n\n"
                "Или нажмите кнопку 'Пропустить'",
                parse_mode='Markdown',
                reply_markup=skip_budget_keyboard
            )

        elif status == 3:
            if text.lower() != 'пропустить':
                try:
                    budget = int(text.replace(' ', ''))
                    db.update_field("users", id, "budget", budget)
                except:
                    db.update_field("users", id, "budget", text)
            db.update_field("users", id, "status", 4)
            await message.answer("📅 *ДАТА ВЫЛЕТА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')

        elif status == 4:
            db.update_field("users", id, "departure_date", text)
            db.update_field("users", id, "status", 5)
            await message.answer("🔄 *ТИП РЕЙСА?*", parse_mode='Markdown', reply_markup=flight_type_keyboard)

        elif status == 6:
            db.update_field("users", id, "departure_time", text)
            db.update_field("users", id, "status", 0)
            db.update_field("users", id, "search_type", None)

            where_from = db.get_field("users", id, "where_fly_from")
            where_to = db.get_field("users", id, "where_to_fly")
            budget_raw = db.get_field("users", id, "budget")
            date = db.get_field("users", id, "departure_date")

            try:
                budget_int = int(budget_raw) if budget_raw and str(budget_raw).isdigit() else None
            except:
                budget_int = None

            origin_code = get_city_code(where_from)
            dest_code = get_city_code(where_to)

            searching_msg = await message.answer(
                f"🔍 ИЩУ БИЛЕТЫ {where_from} → {where_to}...\n⏳ ПОДОЖДИТЕ",
                parse_mode='Markdown'
            )

            api_date = date[:7] if len(date) > 7 else date
            flights = search_flights(origin_code, dest_code, api_date, budget_int)
            result = format_flights(flights)

            await searching_msg.delete()
            await message.answer(result, parse_mode='Markdown', disable_web_page_preview=True)
            await message.answer("✅ *ПОИСК ЗАВЕРШЕН!*", parse_mode='Markdown', reply_markup=main_keyboard)

    # ===== ПОИСК ОТЕЛЕЙ =====
    elif search_type == "hotels":
        if status == 10:
            db.update_field("users", id, "hotel_city", text)
            db.update_field("users", id, "status", 11)
            await message.answer(
                "⭐ *ВЫБЕРИТЕ ЗВЕЗДНОСТЬ ОТЕЛЯ:*",
                parse_mode='Markdown',
                reply_markup=hotel_stars_keyboard
            )

        elif status == 12:
            db.update_field("users", id, "hotel_check_in", text)
            db.update_field("users", id, "status", 13)
            await message.answer("📅 *ДАТА ВЫЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')

        elif status == 13:
            db.update_field("users", id, "hotel_check_out", text)
            db.update_field("users", id, "status", 14)
            await message.answer("👥 *КОЛИЧЕСТВО ГОСТЕЙ?* (например: 2)", parse_mode='Markdown')

        elif status == 14:
            try:
                guests = int(text)
            except:
                guests = 2

            city = db.get_field("users", id, "hotel_city")
            min_stars = db.get_field("users", id, "hotel_min_stars")
            check_in = db.get_field("users", id, "hotel_check_in")
            check_out = db.get_field("users", id, "hotel_check_out")

            db.update_field("users", id, "status", 0)
            db.update_field("users", id, "search_type", None)

            stars_text = f"{min_stars} звезд" if min_stars else "любой"
            searching_msg = await message.answer(
                f"🔍 ИЩУ ОТЕЛИ В *{city}*\n"
                f"⭐ {stars_text}\n"
                f"📅 {check_in} — {check_out}\n"
                f"👥 {guests} гостей\n"
                f"⏳ ПОДОЖДИТЕ...",
                parse_mode='Markdown'
            )

            hotels = search_hotels(city, check_in, check_out, guests, min_stars, limit=15)
            result = format_hotels(hotels)

            await searching_msg.delete()
            await message.answer(result, parse_mode='Markdown', disable_web_page_preview=True)
            await message.answer("✅ *ПОИСК ЗАВЕРШЕН!*", parse_mode='Markdown', reply_markup=main_keyboard)


# ===== INLINE КНОПКИ =====

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    id = call.from_user.id

    if not db.user_exist(id):
        db.add_user(id)

    if call.data == "search_tickets":
        db.update_field("users", id, "search_type", "flights")
        db.update_field("users", id, "status", 1)
        await call.message.answer("✈️ *ОТКУДА ЛЕТИМ?*", parse_mode='Markdown')
        await call.answer()

    elif call.data == "search_hotels":
        db.update_field("users", id, "search_type", "hotels")
        db.update_field("users", id, "status", 10)
        await call.message.answer("🏨 *В КАКОМ ГОРОДЕ ИЩЕМ ОТЕЛЬ?*", parse_mode='Markdown')
        await call.answer()

    elif call.data == "hotel_stars_1":
        db.update_field("users", id, "hotel_min_stars", 1)
        db.update_field("users", id, "status", 12)
        await call.message.answer("📅 *ДАТА ЗАЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "hotel_stars_2":
        db.update_field("users", id, "hotel_min_stars", 2)
        db.update_field("users", id, "status", 12)
        await call.message.answer("📅 *ДАТА ЗАЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "hotel_stars_3":
        db.update_field("users", id, "hotel_min_stars", 3)
        db.update_field("users", id, "status", 12)
        await call.message.answer("📅 *ДАТА ЗАЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "hotel_stars_4":
        db.update_field("users", id, "hotel_min_stars", 4)
        db.update_field("users", id, "status", 12)
        await call.message.answer("📅 *ДАТА ЗАЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "hotel_stars_5":
        db.update_field("users", id, "hotel_min_stars", 5)
        db.update_field("users", id, "status", 12)
        await call.message.answer("📅 *ДАТА ЗАЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "hotel_stars_any":
        db.update_field("users", id, "hotel_min_stars", None)
        db.update_field("users", id, "status", 12)
        await call.message.answer("📅 *ДАТА ЗАЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "skip_budget":
        db.update_field("users", id, "budget", None)
        db.update_field("users", id, "status", 4)
        await call.message.answer("📅 *ДАТА ВЫЛЕТА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "flight_round":
        db.update_field("users", id, "flight_type", "round")
        db.update_field("users", id, "status", 6)
        await call.message.answer("⏰ *ВРЕМЯ ВЫЛЕТА?* (например: 14:30)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "flight_oneway":
        db.update_field("users", id, "flight_type", "oneway")
        db.update_field("users", id, "status", 6)
        await call.message.answer("⏰ *ВРЕМЯ ВЫЛЕТА?* (например: 14:30)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "back_to_menu":
        db.update_field("users", id, "status", 0)
        db.update_field("users", id, "search_type", None)
        await call.message.answer("📱 *ГЛАВНОЕ МЕНЮ*", parse_mode='Markdown', reply_markup=main_keyboard)
        await call.answer()

    elif call.data == "all":
        where_from = db.get_field("users", id, "where_fly_from")
        where_to = db.get_field("users", id, "where_to_fly")
        budget = db.get_field("users", id, "budget")
        hotel_city = db.get_field("users", id, "hotel_city")

        info = f"📊 *ВАШИ ДАННЫЕ:*\n\n"
        info += f"✈️ *БИЛЕТЫ:*\n"
        info += f"  🛫 Откуда: {where_from or 'Не указано'}\n"
        info += f"  🛬 Куда: {where_to or 'Не указано'}\n"
        info += f"  💰 Бюджет: {budget or 'Любой'} RUB\n\n"
        info += f"🏨 *ОТЕЛИ:*\n"
        info += f"  🏙️ Город: {hotel_city or 'Не указан'}\n"

        await call.message.answer(info, parse_mode='Markdown')
        await call.answer()

    await bot.answer_callback_query(call.id)


# ===== ЗАПУСК =====

async def main():
    print("=" * 50)
    print("🚀 TRAVEL BOT ЗАПУЩЕН!")
    print("=" * 50)
    print("📱 БОТ ИЩЕТ:")
    print("   ✈️ АВИАБИЛЕТЫ (Travelpayouts API)")
    print("   🏨 ОТЕЛИ (Hotellook API)")
    print("=" * 50)
    print("💡 КОМАНДЫ: /start, /help")
    print("=" * 50)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
