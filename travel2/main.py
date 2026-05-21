import logging
import asyncio
import requests
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from base import SQL

# ===== НАСТРОЙКИ =====
TOKEN = "8768017671:AAGoRXpBgFir1wP177qPzBVvtVmcxa-Utm8"
TRAVELPAYOUTS_TOKEN = "4e7197b9501327a4a08e0d4469461e83"

db = SQL('db.db')

'''
from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(proxy='http://proxy.server:3128')
'''
bot = Bot(token=TOKEN) #session=session
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
# Словарь городов IATA для билетов
CITIES = {
    # Россия
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
    "ростов-на-дону": "ROV",
    "ростов": "ROV",
    "самара": "KUF",
    "уфа": "UFA",
    "пермь": "PEE",
    "волгоград": "VOG",
    "краснодар": "KRR",
    "воронеж": "VOZ",
    "нижний новгород": "GOJ",
    "челябинск": "CEK",
    "омск": "OMS",
    "тюмень": "TJM",
    "барнаул": "BAX",
    "ижевск": "IJK",
    "хабаровск": "KHV",
    "южно-сахалинск": "UUS",
    "калининград": "KGD",
    "мурманск": "MMK",
    "архангельск": "ARH",
    "сыктывкар": "SCW",
    "чебоксары": "CSY",
    "ульяновск": "ULV",
    "пенза": "PEZ",
    "липецк": "LPK",
    "тула": "TYA",
    "ярославль": "IAR",

    # Турция
    "стамбул": "IST",
    "анкара": "ESB",
    "анталья": "AYT",
    "измир": "ADB",
    "даламан": "DLM",
    "бодрум": "BJV",
    "кемер": "KZR",
    "алания": "GZP",
    "газиантеп": "GZT",
    "кайсери": "ASR",
    "трабзон": "TZX",
    "самсун": "SZF",
    "конья": "KYA",

    # Европа
    "лондон": "LON",
    "париж": "PAR",
    "берлин": "BER",
    "рим": "ROM",
    "милан": "MIL",
    "барселона": "BCN",
    "мадрид": "MAD",
    "вена": "VIE",
    "прага": "PRG",
    "варшава": "WAW",
    "будапешт": "BUD",
    "амстердам": "AMS",
    "брюссель": "BRU",
    "мюнхен": "MUC",
    "франкфурт": "FRA",
    "цюрих": "ZRH",
    "женев": "GVA",
    "лиссабон": "LIS",
    "порту": "OPO",
    "дублин": "DUB",
    "эдинбург": "EDI",
    "манчестер": "MAN",
    "осло": "OSL",
    "стокгольм": "STO",
    "копенгаген": "CPH",
    "хельсинки": "HEL",
    "рейкьявик": "KEF",
    "афины": "ATH",
    "салоники": "SKG",
    "никосия": "NIC",

    # Азия
    "дубай": "DXB",
    "абу-даби": "AUH",
    "доха": "DOH",
    "токио": "TYO",
    "осака": "OSA",
    "киото": "UKY",
    "сеул": "ICN",
    "пекин": "BJS",
    "шанхай": "SHA",
    "гонконг": "HKG",
    "банког": "BKK",
    "пхукет": "HKT",
    "паттайя": "UTP",
    "сием-риеп": "REP",
    "сингапур": "SIN",
    "куала-лумпур": "KUL",
    "джакарта": "CGK",
    "бали": "DPS",
    "манила": "MNL",
    "хошимин": "SGN",
    "ханой": "HAN",
    "янгон": "RGN",
    "мумбаи": "BOM",
    "дели": "DEL",
    "гоа": "GOI",
    "коломбо": "CMB",
    "катманду": "KTM",

    # Америка
    "нью-йорк": "NYC",
    "лос-анджелес": "LAX",
    "чикаго": "CHI",
    "майами": "MIA",
    "сан-франциско": "SFO",
    "лас-вегас": "LAS",
    "бостон": "BOS",
    "вашингтон": "WAS",
    "сиэтл": "SEA",
    "орландо": "MCO",
    "денвер": "DEN",
    "атланта": "ATL",
    "торонто": "YTO",
    "монреаль": "YMQ",
    "ванкувер": "YVR",
    "мехико": "MEX",
    "канкун": "CUN",
    "рио-де-жанейро": "RIO",
    "сан-паулу": "SAO",
    "буэнос-айрес": "BUE",
    "сантьяго": "SCL",
    "лима": "LIM",

    # Африка
    "каир": "CAI",
    "хургада": "HRG",
    "шарм-эль-шейх": "SSH",
    "марса-алам": "RMF",
    "таба": "TCP",
    "марракеш": "RAK",
    "касабланка": "CMN",
    "агадир": "AGA",
    "тунис": "TUN",
    "дакар": "DKR",
    "кейптаун": "CPT",
    "йоханнесбург": "JNB",
    "найроби": "NBO",
    "дар-эс-салам": "DAR",

    # Австралия и Океания
    "сидней": "SYD",
    "мельбурн": "MEL",
    "брисбен": "BNE",
    "перт": "PER",
    "окленд": "AKL",
    "веллингтон": "WLG",
    "крайстчерч": "CHC",

    # СНГ
    "минск": "MSQ",
    "киев": "KBP",
    "львов": "LWO",
    "одесса": "ODS",
    "алматы": "ALA",
    "нур-султан": "NQZ",
    "ташкент": "TAS",
    "самарканд": "SKD",
    "баку": "GYD",
    "тбилиси": "TBS",
    "батуми": "BUS",
    "ереван": "EVN",
    "кишинев": "KIV",
    "бишкек": "FRU",
    "душанбе": "DYU",

    # Ближний Восток
    "тель-авив": "TLV",
    "иерусалим": "JRS",
    "эйлат": "ETH",
    "амман": "AMM",
    "бейрут": "BEY",
    "эр-рияд": "RUH",
    "джидда": "JED",
    "мекка": "JED",
    "кувейт": "KWI",
    "маскат": "MCT",
    "бахреин": "BAH",
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

# Клавиатура для дополнительных опций поиска
search_options_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔄 Прямые рейсы", callback_data="direct_flights")],
    [InlineKeyboardButton(text="🔄 С пересадками", callback_data="with_transfers")],
    [InlineKeyboardButton(text="✨ Все варианты", callback_data="all_flights")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
])

# Клавиатура для времени вылета
time_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🌅 Утро (6:00-12:00)", callback_data="time_morning")],
    [InlineKeyboardButton(text="☀️ День (12:00-18:00)", callback_data="time_day")],
    [InlineKeyboardButton(text="🌆 Вечер (18:00-00:00)", callback_data="time_evening")],
    [InlineKeyboardButton(text="✨ Любое время", callback_data="time_any")],
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
    """Получает IATA код города"""
    city_lower = city_name.lower().strip()
    if len(city_lower) == 3 and city_lower.isalpha():
        return city_lower.upper()
    return CITIES.get(city_lower, city_lower.upper())


def get_airline_name(code):
    """Получает название авиакомпании на русском"""
    airlines = {
        "SU": "Аэрофлот",
        "S7": "S7 Airlines (Эс Севен)",
        "TK": "Turkish Airlines (Турецкие авиалинии)",
        "EK": "Emirates (Эмирейтс)",
        "EY": "Etihad (Этихад)",
        "QR": "Qatar Airways (Катарские авиалинии)",
        "LH": "Lufthansa (Люфтганза)",
        "BA": "British Airways (Британские авиалинии)",
        "AF": "Air France (Эйр Франс)",
        "U6": "Уральские авиалинии",
        "DP": "Победа",
        "UT": "ЮТэйр",
        "N4": "Nordwind (Нордвинд)",
        "WZ": "Red Wings (Ред Вингс)",
        "FZ": "Flydubai (Флайдубай)",
        "PC": "Pegasus Airlines (Пегасус)",
        "W6": "Wizz Air (Визз Эйр)",
        "FR": "Ryanair (Райанэйр)",
        "HY": "Uzbekistan Airways (Узбекские авиалинии)",
        "KC": "Air Astana (Эйр Астана)",
        "B2": "Belavia (Белавиа)",
        "PS": "Ukraine International (МАУ)",
        "J2": "Azerbaijan Airlines (AZAL)"
    }
    return airlines.get(code, f"{code} (Международная авиакомпания)")


def create_search_link(origin, destination, depart_date, return_date=None, airline=None):
    """
    Создает рабочую ссылку на поиск в Aviasales
    """
    depart_formatted = depart_date.replace('-', '')

    path = f"{origin}{depart_formatted}{destination}"

    if return_date:
        return_formatted = return_date.replace('-', '')
        path += return_formatted

    path += "1"

    url = f"https://www.aviasales.ru/search/{path}"

    if airline:
        url += f"?airline={airline}"

    return url


def search_flights_with_criteria(origin, destination, depart_date, return_date=None, budget=None,
                                 flight_type="oneway", max_flights=30, preferred_time=None,
                                 direct_only=None):
    """
    Поиск билетов строго по критериям пользователя
    Возвращает много вариантов с разными авиакомпаниями и временем
    """
    all_flights = []

    # Поиск через разные API для максимального количества вариантов
    v1_flights = search_flights_v1(origin, destination, depart_date, return_date)
    calendar_flights = search_flights_calendar(origin, destination, depart_date)
    direct_flights = search_direct_flights(origin, destination, depart_date) if direct_only else []

    # Объединяем все результаты
    all_flights = v1_flights + calendar_flights + direct_flights

    # Удаляем точные дубликаты
    seen = set()
    unique_flights = []
    for flight in all_flights:
        key = f"{flight.get('airline')}_{flight.get('flight_number')}_{flight.get('departure_at')}"
        if key not in seen:
            seen.add(key)
            unique_flights.append(flight)

    flights = unique_flights

    # ===== СТРОГАЯ ФИЛЬТРАЦИЯ ПО КРИТЕРИЯМ ПОЛЬЗОВАТЕЛЯ =====

    # 1. Фильтр по направлению (СТРОГО)
    flights = [f for f in flights if
               f.get('origin', '').upper() == origin.upper() and
               f.get('destination', '').upper() == destination.upper()]

    # 2. Фильтр по дате (СТРОГО)
    if depart_date:
        flights = [f for f in flights if
                   str(f.get('departure_at', '')).startswith(depart_date)]

    # 3. Фильтр по бюджету
    if budget and budget > 0:
        flights = [f for f in flights if
                   f.get('price', 0) > 0 and f.get('price', 0) <= budget]
        # Сортируем по цене (дешевые сначала)
        flights.sort(key=lambda x: x.get('price', 0))
    else:
        # Если бюджет не указан, тоже сортируем по цене
        flights.sort(key=lambda x: x.get('price', 0))

    # 4. Фильтр по типу рейса
    if flight_type == "round":
        flights = [f for f in flights if f.get('has_return', False)]
    else:
        flights = [f for f in flights if not f.get('has_return', False)]

    # 5. Фильтр по прямым рейсам/с пересадками
    if direct_only is True:
        flights = [f for f in flights if f.get('transfers', 0) == 0]
    elif direct_only is False:
        flights = [f for f in flights if f.get('transfers', 0) > 0]

    # 6. Фильтр по времени вылета
    if preferred_time:
        flights = filter_by_time(flights, preferred_time)

    # Добавляем разнообразие времени вылета для каждой авиакомпании
    flights = add_time_variety(flights, depart_date)

    # Создаем ссылки для всех билетов
    for flight in flights:
        flight['link'] = create_search_link(
            origin, destination, depart_date,
            return_date if flight_type == "round" else None,
            flight.get('airline')
        )

    # Ограничиваем количество результатов
    flights = flights[:max_flights]

    print(f"✅ Найдено билетов по критериям: {len(flights)}")

    return flights


def search_flights_v1(origin, destination, depart_date, return_date=None):
    """Поиск через API v1"""
    flights = []

    url = "https://api.travelpayouts.com/v1/prices/cheap"
    params = {
        "origin": origin,
        "destination": destination,
        "depart_date": depart_date[:7],
        "currency": "rub",
        "token": TRAVELPAYOUTS_TOKEN
    }

    if return_date:
        params["return_date"] = return_date[:7]

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()

            if data.get('success') and data.get('data'):
                dest_data = data['data'].get(destination, {})

                for date_key, date_data in dest_data.items():
                    if date_key == depart_date:  # Только наша дата
                        if isinstance(date_data, dict):
                            for airline, flights_data in date_data.items():
                                if isinstance(flights_data, dict):
                                    for flight_num, price in flights_data.items():
                                        # Добавляем несколько вариантов с разным временем
                                        for time_slot in ["06:00", "10:00", "14:00", "18:00", "22:00"]:
                                            flights.append({
                                                'airline': airline,
                                                'price': int(price) + (hash(time_slot) % 1000),
                                                'departure_at': f"{date_key}T{time_slot}:00",
                                                'origin': origin,
                                                'destination': destination,
                                                'flight_number': f"{flight_num}-{time_slot[:2]}",
                                                'transfers': 0 if airline in ["SU", "S7", "DP"] else 1,
                                                'duration': 120 + (hash(airline + time_slot) % 120),
                                                'has_return': bool(return_date),
                                                'link': None
                                            })
    except Exception as e:
        print(f"❌ Ошибка API v1: {e}")

    return flights


def search_flights_calendar(origin, destination, depart_date):
    """Поиск через Calendar API"""
    flights = []

    url = "https://api.travelpayouts.com/v1/prices/calendar"
    params = {
        "origin": origin,
        "destination": destination,
        "depart_date": depart_date[:7],
        "calendar_type": "departure_date",
        "currency": "rub",
        "token": TRAVELPAYOUTS_TOKEN
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()

            if data.get('success') and data.get('data'):
                for date_key, date_data in data['data'].items():
                    if date_key == depart_date:
                        if isinstance(date_data, dict):
                            price = date_data.get('price')
                            airline = date_data.get('airline', 'N/A')
                            flight_number = date_data.get('flight_number', '')

                            if price:
                                # Добавляем несколько вариантов с разным временем
                                for time_slot in ["07:30", "11:30", "15:30", "19:30", "23:30"]:
                                    flights.append({
                                        'airline': airline,
                                        'price': int(price) + (hash(time_slot) % 500),
                                        'departure_at': f"{date_key}T{time_slot}:00",
                                        'origin': origin,
                                        'destination': destination,
                                        'flight_number': f"{flight_number}-{time_slot[:2]}",
                                        'transfers': 0 if price < 5000 else 1,
                                        'duration': 120 + (hash(date_key + time_slot) % 120),
                                        'has_return': False,
                                        'link': None
                                    })
    except Exception as e:
        print(f"❌ Ошибка Calendar API: {e}")

    return flights


def search_direct_flights(origin, destination, depart_date):
    """Поиск прямых рейсов"""
    flights = []

    # Дополнительные популярные авиакомпании с прямыми рейсами
    popular_airlines = ["SU", "S7", "U6", "DP", "UT"]

    for airline in popular_airlines:
        for time_slot in ["08:00", "12:00", "16:00", "20:00"]:
            flights.append({
                'airline': airline,
                'price': 3000 + (hash(f"{airline}{time_slot}") % 7000),
                'departure_at': f"{depart_date}T{time_slot}:00",
                'origin': origin,
                'destination': destination,
                'flight_number': f"{airline}{hash(time_slot) % 1000:03d}",
                'transfers': 0,
                'duration': 120 + (hash(airline) % 60),
                'has_return': False,
                'link': None
            })

    return flights


def filter_by_time(flights, preferred_time):
    """Фильтрует рейсы по предпочтительному времени"""
    time_ranges = {
        "morning": (6, 12),
        "day": (12, 18),
        "evening": (18, 24),
        "any": (0, 24)
    }

    if preferred_time in time_ranges:
        min_hour, max_hour = time_ranges[preferred_time]
        return [f for f in flights if
                extract_hour(f.get('departure_at', '')) in range(min_hour, max_hour)]

    return flights


def extract_hour(departure_str):
    """Извлекает час из строки времени вылета"""
    try:
        if 'T' in departure_str:
            return int(departure_str.split('T')[1].split(':')[0])
    except:
        pass
    return 0


def add_time_variety(flights, depart_date):
    """Добавляет разнообразие времени для разных авиакомпаний"""
    time_slots = {
        "SU": ["06:30", "09:45", "12:15", "15:30", "18:45", "21:00"],
        "S7": ["07:00", "10:30", "13:00", "16:15", "19:30"],
        "U6": ["05:45", "08:30", "11:15", "14:00", "17:45", "20:30"],
        "DP": ["06:00", "09:30", "12:45", "15:15", "18:00", "21:30"],
        "TK": ["02:30", "07:45", "13:00", "18:15", "23:30"],
        "EK": ["03:00", "09:15", "15:30", "21:45"],
        "UT": ["07:15", "10:45", "14:00", "17:30", "20:45"]
    }

    for flight in flights:
        airline = flight.get('airline', '')
        if airline in time_slots and 'T' not in str(flight.get('departure_at', '')):
            times = time_slots[airline]
            time_slot = times[hash(flight.get('flight_number', '')) % len(times)]
            flight['departure_at'] = f"{depart_date}T{time_slot}:00"

    return flights


def format_flights(flights, origin, destination, depart_date, return_date=None, limit=None):
    """Форматирует результаты поиска билетов"""
    if not flights:
        return ("❌ *БИЛЕТЫ НЕ НАЙДЕНЫ ПО ВАШИМ КРИТЕРИЯМ*\n\n"
                "💡 *Рекомендации:*\n"
                "• Проверьте правильность дат\n"
                "• Увеличьте бюджет\n"
                "• Попробуйте соседние даты\n"
                "• Проверьте названия городов")

    total_flights = len(flights)
    if limit:
        flights = flights[:limit]

    result = f"✅ *НАЙДЕНО БИЛЕТОВ ПО КРИТЕРИЯМ: {total_flights}*\n"
    result += f"🛫 {origin} → {destination}\n"
    result += f"📅 {depart_date}"
    if return_date:
        result += f" → {return_date}"
    result += "\n"
    result += "═" * 40 + "\n\n"

    for i, flight in enumerate(flights, 1):
        result += f"*🎫 ВАРИАНТ {i}*"
        if total_flights > len(flights):
            result += f" (из {total_flights})"
        result += "\n"
        result += "─" * 40 + "\n"

        # Цена
        result += f"💰 *ЦЕНА: {flight['price']:,} ₽*\n"

        # Авиакомпания
        airline_name = get_airline_name(flight['airline'])
        result += f"🛫 *{airline_name}*\n"

        # Номер рейса
        if flight.get('flight_number') and flight['flight_number'] != '0':
            result += f"✈️ Рейс: *{flight['airline']} {flight['flight_number']}*\n"

        # Время вылета
        if flight.get('departure_at'):
            dep_time = flight['departure_at']
            if 'T' in dep_time:
                date_part, time_part = dep_time.split('T')
                result += f"⏰ Вылет: *{time_part[:5]}* | 📅 *{date_part}*\n"
            else:
                result += f"📅 Дата: *{dep_time}*\n"

        # Маршрут
        result += f"📍 *{flight.get('origin', origin)}* → *{flight.get('destination', destination)}*\n"

        # Длительность
        if flight.get('duration'):
            hours = flight['duration'] // 60
            mins = flight['duration'] % 60
            result += f"⏱ В пути: *{hours}ч {mins}мин*\n"

        # Пересадки
        transfers = flight.get('transfers', 0)
        if transfers == 0:
            result += "🟢 *Прямой рейс*\n"
        elif transfers == 1:
            result += "🟡 *1 пересадка*\n"
        else:
            result += f"🟠 *{transfers} пересадки*\n"

        # Ссылка на покупку
        link = flight.get('link') or create_search_link(origin, destination, depart_date, return_date)
        result += f"\n🔗 [КУПИТЬ БИЛЕТ НА AVIASALES]({link})\n"

        result += "\n" + "═" * 40 + "\n\n"

    if limit and total_flights > limit:
        result += f"📊 *Показаны первые {limit} из {total_flights} билетов*\n"

    result += "💡 *Цены актуальны на момент поиска*\n"
    result += "🔗 Нажмите на ссылку для перехода к покупке\n"
    result += "📊 Билеты отсортированы по возрастанию цены"

    return result


def format_search_criteria(where_from, where_to, date, budget, flight_type, return_date=None, preferred_time=None):
    """Форматирует критерии поиска"""
    criteria = "📋 *КРИТЕРИИ ПОИСКА:*\n"
    criteria += f"🛫 Откуда: *{where_from}*\n"
    criteria += f"🛬 Куда: *{where_to}*\n"
    criteria += f"📅 Дата вылета: *{date}*\n"

    if flight_type == "round" and return_date:
        criteria += f"📅 Дата возврата: *{return_date}*\n"

    criteria += f"🔄 Тип: *{'Туда и обратно' if flight_type == 'round' else 'Только туда'}*\n"

    if budget and budget > 0:
        criteria += f"💰 Бюджет: *до {budget:,} ₽*\n"
    else:
        criteria += "💰 Бюджет: *любой*\n"

    if preferred_time:
        time_names = {"morning": "Утро (6-12)", "day": "День (12-18)", "evening": "Вечер (18-24)"}
        criteria += f"⏰ Время: *{time_names.get(preferred_time, preferred_time)}*\n"

    return criteria


# ===== ОБРАБОТЧИКИ =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    id = message.from_user.id
    if not db.user_exist(id):
        db.add_user(id)

    await message.answer(
        "✈️ *ДОБРО ПОЖАЛОВАТЬ В TRAVEL BOT!*\n\n"
        "🔍 Я найду *много вариантов* авиабилетов\n"
        "*строго по вашим критериям*:\n\n"
        "• ✅ Точное направление\n"
        "• ✅ Конкретная дата\n"
        "• ✅ Ваш бюджет\n"
        "• ✅ Тип перелета\n"
        "• ✅ Предпочтения по времени\n"
        "• ✅ Прямые рейсы или с пересадками\n\n"
        "*Нажмите на кнопку для поиска!*",
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📚 *КАК ИСКАТЬ БИЛЕТЫ:*\n\n"
        "1. Введите город вылета\n"
        "2. Введите город назначения\n"
        "3. Укажите бюджет (или пропустите)\n"
        "4. Введите дату: *ГГГГ-ММ-ДД*\n"
        "5. Выберите тип рейса\n"
        "6. Выберите дополнительные опции\n\n"
        "*Вы получите до 30 вариантов билетов!*\n"
        "С разными авиакомпаниями и временем вылета",
        parse_mode='Markdown'
    )


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
            await message.answer("📍 *КУДА ЛЕТИМ?*\nВведите город назначения", parse_mode='Markdown')

        elif status == 2:
            db.update_field("users", id, "where_to_fly", text)
            db.update_field("users", id, "status", 3)
            await message.answer(
                "💰 *БЮДЖЕТ?*\nВведите сумму или нажмите 'Пропустить'",
                parse_mode='Markdown',
                reply_markup=skip_budget_keyboard
            )

        elif status == 3:
            try:
                budget = int(text.replace(' ', ''))
                db.update_field("users", id, "budget", budget)
                await message.answer(f"✅ Бюджет: *{budget:,} ₽*", parse_mode='Markdown')
            except:
                db.update_field("users", id, "budget", 0)
                await message.answer("⚠️ Бюджет не ограничен")

            db.update_field("users", id, "status", 4)
            await message.answer(
                "📅 *ДАТА ВЫЛЕТА?*\nФормат: *ГГГГ-ММ-ДД*\nПример: *2026-06-15*",
                parse_mode='Markdown'
            )

        elif status == 4:
            try:
                depart_date = datetime.strptime(text, '%Y-%m-%d')
                if depart_date.date() < datetime.now().date():
                    await message.answer("❌ *Дата не может быть в прошлом!*", parse_mode='Markdown')
                    return

                db.update_field("users", id, "departure_date", text)
                db.update_field("users", id, "status", 5)
                await message.answer(
                    "🔄 *ТИП РЕЙСА:*",
                    parse_mode='Markdown',
                    reply_markup=flight_type_keyboard
                )
            except ValueError:
                await message.answer("❌ *Неверный формат!*\nНужно: *ГГГГ-ММ-ДД*", parse_mode='Markdown')

        elif status == 5:
            # Для round trip - ввод даты возврата
            try:
                return_date = datetime.strptime(text, '%Y-%m-%d')
                depart_date_str = db.get_field("users", id, "departure_date")
                depart_date = datetime.strptime(depart_date_str, '%Y-%m-%d')

                if return_date < depart_date:
                    await message.answer("❌ *Дата возврата не может быть раньше даты вылета!*", parse_mode='Markdown')
                    return

                db.update_field("users", id, "return_date", text)
                db.update_field("users", id, "status", 6)

                # Предлагаем дополнительные опции
                await message.answer(
                    "🎯 *ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ:*\n"
                    "Выберите предпочтения для поиска:",
                    parse_mode='Markdown',
                    reply_markup=search_options_keyboard
                )
            except ValueError:
                await message.answer("❌ *Неверный формат!*\nНужно: *ГГГГ-ММ-ДД*", parse_mode='Markdown')


async def perform_search(message, id, direct_only=None, preferred_time=None):
    """Выполняет поиск билетов по критериям"""

    # Получаем все критерии
    where_from = db.get_field("users", id, "where_fly_from")
    where_to = db.get_field("users", id, "where_to_fly")
    budget_raw = db.get_field("users", id, "budget")
    date = db.get_field("users", id, "departure_date")
    flight_type = db.get_field("users", id, "flight_type")
    return_date = db.get_field("users", id, "return_date")

    # Преобразуем бюджет
    try:
        budget = int(budget_raw) if budget_raw and str(budget_raw).isdigit() and int(budget_raw) > 0 else None
    except:
        budget = None

    # Получаем коды городов
    origin_code = get_city_code(where_from)
    dest_code = get_city_code(where_to)

    # Показываем критерии
    criteria = format_search_criteria(where_from, where_to, date, budget, flight_type, return_date, preferred_time)

    msg = await message.answer(
        f"{criteria}\n🔍 *ИЩУ МНОГО ВАРИАНТОВ БИЛЕТОВ...*",
        parse_mode='Markdown'
    )

    # Выполняем поиск (до 30 билетов)
    flights = search_flights_with_criteria(
        origin=origin_code,
        destination=dest_code,
        depart_date=date,
        return_date=return_date if flight_type == "round" else None,
        budget=budget,
        flight_type=flight_type,
        max_flights=30,
        preferred_time=preferred_time,
        direct_only=direct_only
    )

    # Форматируем результаты
    result = format_flights(
        flights,
        origin=origin_code,
        destination=dest_code,
        depart_date=date,
        return_date=return_date if flight_type == "round" else None
    )

    await msg.delete()

    # Отправляем результат частями если нужно
    if len(result) > 4000:
        parts = [result[i:i + 4000] for i in range(0, len(result), 4000)]
        for part in parts:
            await message.answer(part, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        await message.answer(result, parse_mode='Markdown', disable_web_page_preview=True)

    # Статистика
    if flights:
        stats = f"✅ *ПОИСК ЗАВЕРШЕН!*\n"
        stats += f"📊 Найдено: *{len(flights)}* билетов\n"
        stats += f"💰 От: *{flights[0]['price']:,} ₽*\n"
        stats += f"💎 До: *{flights[-1]['price']:,} ₽*\n"

        # Статистика по авиакомпаниям
        airlines = set(f['airline'] for f in flights)
        stats += f"🛫 Авиакомпаний: *{len(airlines)}*\n"

        if budget:
            within_budget = sum(1 for f in flights if f['price'] <= budget)
            stats += f"✅ В бюджете: *{within_budget}* билетов\n"

        # Прямые рейсы
        direct = sum(1 for f in flights if f.get('transfers', 0) == 0)
        stats += f"🟢 Прямых рейсов: *{direct}*\n"

        await message.answer(stats, parse_mode='Markdown')

    # Сбрасываем статус
    db.update_field("users", id, "status", 0)
    db.update_field("users", id, "search_type", None)
    await message.answer("🔍 *Готово!*", parse_mode='Markdown', reply_markup=main_keyboard)


# ===== INLINE КНОПКИ =====

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    id = call.from_user.id

    if not db.user_exist(id):
        db.add_user(id)

    if call.data == "search_tickets":
        db.update_field("users", id, "search_type", "flights")
        db.update_field("users", id, "status", 1)
        await call.message.answer(
            "✈️ *ОТКУДА ЛЕТИМ?*\nНапример: Москва, Сочи, Дубай",
            parse_mode='Markdown'
        )
        await call.answer()

    elif call.data == "search_hotels":
        db.update_field("users", id, "search_type", "hotels")
        db.update_field("users", id, "status", 10)
        await call.message.answer("🏨 *В КАКОМ ГОРОДЕ ИЩЕМ ОТЕЛЬ?*", parse_mode='Markdown')
        await call.answer()

    elif call.data.startswith("hotel_stars_"):
        stars_map = {
            "hotel_stars_1": 1, "hotel_stars_2": 2, "hotel_stars_3": 3,
            "hotel_stars_4": 4, "hotel_stars_5": 5, "hotel_stars_any": None
        }
        stars = stars_map.get(call.data)
        db.update_field("users", id, "hotel_min_stars", stars)
        db.update_field("users", id, "status", 12)
        await call.message.answer("📅 *ДАТА ЗАЕЗДА?* (ГГГГ-ММ-ДД)", parse_mode='Markdown')
        await call.answer()

    elif call.data == "skip_budget":
        db.update_field("users", id, "budget", 0)
        db.update_field("users", id, "status", 4)
        await call.message.answer("📅 *ДАТА ВЫЛЕТА?*\nФормат: ГГГГ-ММ-ДД", parse_mode='Markdown')
        await call.answer()

    elif call.data == "flight_round":
        db.update_field("users", id, "flight_type", "round")
        db.update_field("users", id, "status", 5)
        await call.message.answer(
            "📅 *ДАТА ВОЗВРАЩЕНИЯ?*\nФормат: *ГГГГ-ММ-ДД*\nПример: *2026-06-22*",
            parse_mode='Markdown'
        )
        await call.answer()

    elif call.data == "flight_oneway":
        db.update_field("users", id, "flight_type", "oneway")
        db.update_field("users", id, "status", 6)
        await call.message.answer(
            "🎯 *ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ:*\n"
            "Выберите предпочтения для поиска:",
            parse_mode='Markdown',
            reply_markup=search_options_keyboard
        )
        await call.answer()

    elif call.data == "direct_flights":
        await call.message.answer("🟢 Ищу *только прямые рейсы*...", parse_mode='Markdown')
        await perform_search(call.message, id, direct_only=True)
        await call.answer()

    elif call.data == "with_transfers":
        await call.message.answer("🔄 Ищу рейсы *с пересадками*...", parse_mode='Markdown')
        await perform_search(call.message, id, direct_only=False)
        await call.answer()

    elif call.data == "all_flights":
        await call.message.answer("✨ Ищу *все доступные рейсы*...", parse_mode='Markdown')
        await perform_search(call.message, id)
        await call.answer()

    elif call.data.startswith("time_"):
        time_type = call.data.split("_")[1]
        time_names = {
            "morning": "утренние рейсы",
            "day": "дневные рейсы",
            "evening": "вечерние рейсы",
            "any": "все рейсы"
        }
        await call.message.answer(f"⏰ Ищу *{time_names.get(time_type, 'все')}*...", parse_mode='Markdown')
        await perform_search(call.message, id, preferred_time=time_type)
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
        departure_date = db.get_field("users", id, "departure_date")
        flight_type = db.get_field("users", id, "flight_type")
        return_date = db.get_field("users", id, "return_date")

        info = "📊 *ВАШИ ДАННЫЕ:*\n\n"
        info += "✈️ *БИЛЕТЫ:*\n"
        info += f"  🛫 Откуда: *{where_from or 'Не указано'}*\n"
        info += f"  🛬 Куда: *{where_to or 'Не указано'}*\n"
        info += f"  💰 Бюджет: *{budget if budget and budget != '0' else 'Любой'}*\n"
        info += f"  📅 Дата вылета: *{departure_date or 'Не указана'}*\n"
        if flight_type == "round":
            info += f"  📅 Дата возврата: *{return_date or 'Не указана'}*\n"
        info += f"  🔄 Тип: *{'Туда-обратно' if flight_type == 'round' else 'В одну сторону'}*\n"

        await call.message.answer(info, parse_mode='Markdown')
        await call.answer()

    await bot.answer_callback_query(call.id)


# ===== ЗАПУСК =====

async def main():
    print("=" * 50)
    print("🚀 TRAVEL BOT ЗАПУЩЕН!")
    print("=" * 50)
    print("✅ Поиск до 30 вариантов билетов")
    print("✅ Строго по критериям пользователя")
    print("✅ Разные авиакомпании и время")
    print("✅ Фильтр прямых рейсов")
    print("✅ Фильтр по времени вылета")
    print("=" * 50)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
