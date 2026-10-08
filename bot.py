import asyncio
import random
import sqlite3
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


# =========================================================
# SOZLAMALAR
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7621605173
ADMIN_USERNAME = "matkharimov1"


# =========================================================
# KARTALAR
# =========================================================

CARDS = {
    "HUMO": {
        "number": "9860 1606 0244 9177",
        "owner": "M.A"
    },
    "UZCARD": {
        "number": "9860 1606 0244 9177",
        "owner": "M.A"
    },
    "VISA": {
        "number": "9860 1606 0244 9177",
        "owner": "M.A"
    }
}


# =========================================================
# BOT
# =========================================================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


# =========================================================
# DATABASE
# =========================================================

db = sqlite3.connect("bot.db")
db.row_factory = sqlite3.Row
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    service TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER DEFAULT 0,
    price REAL DEFAULT 0,
    total REAL DEFAULT 0,
    platform TEXT DEFAULT '',
    link TEXT DEFAULT '',
    tariff TEXT DEFAULT '',
    admin_message_id INTEGER DEFAULT 0,
    completed_time TEXT DEFAULT ''
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    name TEXT PRIMARY KEY,
    value TEXT
)
""")

db.commit()


# =========================================================
# EMOJILAR
# =========================================================

DEFAULT_EMOJIS = {
    "services": "🗂️",
    "orders": "🛒",
    "balance": "💰",
    "deposit": "💳",
    "help": "✍️",
    "admin": "👨‍💻",
}


def get_emoji(name):
    cursor.execute(
        "SELECT value FROM settings WHERE name=?",
        (f"emoji_{name}",)
    )

    row = cursor.fetchone()

    if row:
        return row["value"]

    return DEFAULT_EMOJIS.get(name, "🔹")


def set_emoji(name, value):
    cursor.execute(
        """
        INSERT INTO settings (name, value)
        VALUES (?, ?)
        ON CONFLICT(name)
        DO UPDATE SET value=excluded.value
        """,
        (f"emoji_{name}", value)
    )

    db.commit()


# =========================================================
# USER ID
# =========================================================

def generate_user_id():

    while True:
        uid = random.randint(1000000, 9999999)

        cursor.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (uid,)
        )

        if cursor.fetchone() is None:
            return uid


def get_or_create_user(tg_id):

    cursor.execute(
        "SELECT user_id FROM users WHERE telegram_id=?",
        (tg_id,)
    )

    row = cursor.fetchone()

    if row:
        return row["user_id"]

    uid = generate_user_id()

    cursor.execute(
        """
        INSERT INTO users
        (telegram_id, user_id, balance)
        VALUES (?, ?, 0)
        """,
        (tg_id, uid)
    )

    db.commit()

    return uid


def get_balance(tg_id):

    cursor.execute(
        "SELECT balance FROM users WHERE telegram_id=?",
        (tg_id,)
    )

    row = cursor.fetchone()

    if not row:
        get_or_create_user(tg_id)
        return 0

    return float(row["balance"])

def get_telegram_id_by_user_id(user_id):

    cursor.execute(
        "SELECT telegram_id FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cursor.fetchone()

    return row["telegram_id"] if row else None


def change_balance(tg_id, amount):

    get_or_create_user(tg_id)

    cursor.execute(
        """
        UPDATE users
        SET balance = balance + ?
        WHERE telegram_id=?
        """,
        (amount, tg_id)
    )

    db.commit()


# =========================================================
# TUGMALAR UCHUN EMOJI
# =========================================================

def get_button_emoji(key):
    # Telegram keyboard tugmalarida custom/premium emoji entity ishlatilmaydi.
    # Shuning uchun premium emoji saqlangan bo‘lsa ham tugmada oddiy fallback ko‘rsatiladi.
    custom = get_custom_emoji(key) if "get_custom_emoji" in globals() else None
    if custom:
        return DEFAULT_MENU_EMOJIS.get(key, "🔹")
    return get_button_emoji(key)


# =========================================================
# ASOSIY MENYU
# =========================================================

def main_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=f"{get_button_emoji('services')} Xizmatlar"
                ),
                KeyboardButton(
                    text=f"{get_button_emoji('orders')} Buyurtmalarim"
                )
            ],
            [
                KeyboardButton(
                    text=f"{get_button_emoji('balance')} Mening hisobim"
                ),
                KeyboardButton(
                    text=f"{get_button_emoji('deposit')} Hisob to‘ldirish"
                )
            ],
            [
                KeyboardButton(
                    text=f"{get_button_emoji('help')} Yordam xizmati"
                ),
                KeyboardButton(
                    text=f"{get_button_emoji('admin')} Admin"
                )
            ]
        ],
        resize_keyboard=True
    )


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start(message: Message):

    uid = get_or_create_user(
        message.from_user.id
    )

    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "SMM xizmatlar botiga xush kelibsiz.\n\n"
        f"🆔 Sizning ID: <code>{uid}</code>\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=main_menu()
    )


# =========================================================
# XIZMATLAR
# =========================================================

def services_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{get_button_emoji('telegram')} Telegram",
                    callback_data="tg"
                ),
                InlineKeyboardButton(
                    text=f"{get_button_emoji('instagram')} Instagram",
                    callback_data="ig"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{get_button_emoji('tiktok')} TikTok",
                    callback_data="tt"
                ),
                InlineKeyboardButton(
                    text=f"{get_button_emoji('youtube')} YouTube",
                    callback_data="yt"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{get_button_emoji('stars')} Telegram [Stars-Premium-Gift]",
                    callback_data="stars"
                )
            ]
        ]
    )


# ENG MUHIM QISM:
# Xizmatlar tugmasi emoji o‘zgargan bo‘lsa ham ishlaydi.
@dp.message(
    lambda m:
    m.text is not None
    and m.text.endswith(" Xizmatlar")
)
async def services(message: Message):

    await message.answer(
        "Quyidagi ijtimoiy tarmoqlardan birini tanlang 👇",
        reply_markup=services_keyboard()
    )

# =========================================================
# TIKTOK / YOUTUBE
# =========================================================

async def unavailable_service(callback: CallbackQuery):

    await callback.message.edit_text(
        "❌ Bu xizmat hozircha mavjud emas.\n\n"
        "Agarda bu xizmat sizga kerak bo‘lsa, "
        "Yordam xizmatiga murojaat qilishingiz mumkin.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Orqaga",
                        callback_data="back_services"
                    )
                ]
            ]
        )
    )

    await callback.answer()


@dp.callback_query(F.data == "tt")
async def tiktok(callback: CallbackQuery):

    await unavailable_service(callback)


@dp.callback_query(F.data == "yt")
async def youtube(callback: CallbackQuery):

    await unavailable_service(callback)


@dp.callback_query(F.data == "back_services")
async def back_services(callback: CallbackQuery):

    await callback.message.edit_text(
        "Quyidagi ijtimoiy tarmoqlardan birini tanlang 👇",
        reply_markup=services_keyboard()
    )

    await callback.answer()


# =========================================================
# TELEGRAM XIZMATLARI
# =========================================================

telegram_services = [
    ("Obunachi [ -Kafolatli ]", "tg1"),
    ("Premium Obunachi [ - Kafolatli ]", "tg2"),
    ("Premium Ovozlar [ - BOOST ]", "tg3"),
    ("Prasmotrlar [ - Tezkor ]", "tg4"),
    ("Prasmotrlar [ - AvtoPost ]", "tg5"),
    ("O‘zbek Xizmatlar [ Barchasi ]", "tg6"),
    ("Reaksiyalar [ Tezkor ]", "tg7"),
    ("Reaksiyalar [ -AvtoPost ]", "tg8"),
    ("So‘rovnomalar [ - OVOZ ]", "tg9"),
    ("Post Ulashish [ Kanal uchun ]", "tg10"),
    ("Post ulashish Share [AvtoPost]", "tg11"),
    ("Premium Obunachi [Yangi Baza]", "tg12"),
]


@dp.callback_query(F.data == "tg")
async def telegram(callback):

    rows = [
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji(data)} {text}",
                callback_data=data
            )
        ]
        for text, data in telegram_services
    ]

    rows.append([
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="back_services"
        )
    ])

    await callback.message.edit_text(
        f"{get_button_emoji('telegram')} "
        f"<b>Telegram xizmatlari</b>\n\n"
        "💰 Narxlar 1000 ta ko‘rinishda hisoblangan summa.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=rows
        )
    )

    await callback.answer()


# =========================================================
# INSTAGRAM
# =========================================================

@dp.callback_query(F.data == "ig")
async def instagram(callback):

    rows = [
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji('ig1')} Obunachilar [ Sifatli-Tezkor ]",
                callback_data="ig1"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji('ig2')} Likelar [ Sifatli Baza ]",
                callback_data="ig2"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji('ig3')} Prasmotr [ Ko‘rishlar ]",
                callback_data="ig3"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji('ig4')} Post Comentlar",
                callback_data="ig4"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji('ig5')} Istoriya Prasmotrlar",
                callback_data="ig5"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji('ig6')} Jonli Efir Live [Prasmotr]",
                callback_data="ig6"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{get_button_emoji('ig7')} O‘zbek Xizmatlar [Uzbekistan]",
                callback_data="ig7"
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Orqaga",
                callback_data="back_services"
            )
        ]
    ]

    await callback.message.edit_text(
        f"{get_button_emoji('instagram')} "
        f"<b>Instagram xizmatlari</b>\n\n"
        "💰 Narxlar 1000 ta uchun hisoblangan summa.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=rows
        )
    )

    await callback.answer()


# =========================================================
# STARS
# =========================================================

@dp.callback_query(F.data == "stars")
async def stars_menu(callback: CallbackQuery):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{get_button_emoji('star')} Telegram Stars [Avtomatik]",
                    callback_data="star_auto"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{get_button_emoji('gift')} Telegram Giftlar [Avtomatik]",
                    callback_data="gift_auto"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Orqaga",
                    callback_data="back_services"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"{get_button_emoji('stars')} "
        f"<b>Telegram Stars-Premium-Gift</b>",
        reply_markup=kb
    )

    await callback.answer()
# =========================================================
# TARIFLAR
# =========================================================

TARIFFS = {
    "tg1": [
        ("Obunachi [90 kun chiqmaydi]", 26845),
        ("Obunachi [365 kun chiqmaydi]", 53600),
    ],

    "tg2": [
        ("Premium Obunachi [R30-Garant]", 99500),
        ("PR Obunachi [R-7 Garant]", 55625),
    ],

    "tg3": [
        ("Boost Ovozlar [R-1 Garant]", 700000),
    ],

    "tg4": [
        ("Prasmotr [Arzon]", 527),
        ("Prasmotr [Ultra-Tezkor]", 523),
    ],

    "tg5": [
        ("Avto Prasmotr [Oxirgi 5ta Post]", 1377),
        ("Avto Prasmotr [Oxirgi 10ta Post]", 3457),
        ("Avto Prasmotr [Oxirgi 20ta Post]", 6771),
    ],

    "tg6": [
        ("O‘zbek Obunachilar [Jonsiz]", 20691),
        ("O‘zbek Post Ko‘rishlar", 31595),
        ("O‘zbek Premium Obunachi [R15]", 193613),
        ("O‘zbek Premium /start Bot [R30]", 313290),
    ],

    "tg7": [
        ("Post Reaction", 1596),
        ("Reaksiya [keyingi 10ta post]", 28403),
        ("Reaksiya [keyingi 30ta post]", 75210),
    ],

    "tg11": [
        ("Avto post ulashish [keyingi 30ta post]", 48881),
        ("Avto post ulashish [keyingi 50ta post]", 95763),
    ],

    "tg12": [
        ("Premium Obunachi [30 kunlik]", 167945),
    ],

    "ig1": [
        ("Obunachi [Arzon-Tezroq]", 13464),
        ("Obunachi [Sifatli-Tezkor]", 17659),
        ("Kafolatli Obunachi [15 kun]", 16967),
        ("Kafolatli Obunachi [30 kun]", 28935),
        ("Kafolatli Obunachi [60 kun]", 40903),
        ("Obunachi [Ultra tezkor]", 15478),
    ],

    "ig2": [
        ("Real Likelar [Eski Baza]", 8829),
        ("Real Likelar [Yangi Baza]", 8191),
    ],

    "ig3": [
        ("Prasmotr [Arzon]", 1121),
        ("Prasmotr [Ultra Tezkor]", 1151),
    ],

    "ig4": [
        ("Comment [Text and Emoji]", 16701),
    ],

    "ig5": [
        ("Istoriya Prasmotr", 5047),
        ("Istoriya Prasmotr [min:20]", 5659),
    ],
}


STARS = [
    ("Stars [Post] - 100ta", 33000),
    ("Stars [Profil] - 100ta", 37000),
]


GIFTS = [
    ("Yurak hadyasi", 6990),
    ("Ayiqcha hadyasi", 6990),
    ("Sovg‘a qutisi hadyasi", 9990),
    ("Gul hadyasi", 9990),
    ("Tort hadyasi", 17990),
    ("Gullar hadyasi", 17990),
    ("Raketa hadyasi", 17990),
    ("Shampan hadyasi", 17990),
    ("Kubok hadyasi", 31990),
    ("Olmos hadyasi", 31990),
    ("Uzuk hadyasi", 31990),
]


# =========================================================
# TARIFLARNI KO‘RSATISH
# =========================================================

async def show_tariffs(
    callback: CallbackQuery,
    code: str,
    title: str,
    back: str
):

    tariffs = TARIFFS.get(code)

    if not tariffs:
        await callback.answer(
            "Tariflar topilmadi.",
            show_alert=True
        )
        return

    rows = []

    for i, (name, price) in enumerate(tariffs):

        rows.append([
            InlineKeyboardButton(
                text=f"{name} - {price:,.0f} so‘m",
                callback_data=f"buy_{code}_{i}"
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data=back
        )
    ])

    await callback.message.edit_text(
        f"📋 <b>{title}</b>\n\n"
        "💰 Narx 1000 dona uchun hisoblangan.\n\n"
        "Kerakli tarifni tanlang 👇",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=rows
        )
    )

    await callback.answer()


# =========================================================
# TELEGRAM TARIFLARI
# =========================================================

@dp.callback_query(F.data == "tg1")
async def tg1(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg1",
        "Telegram Obunachi",
        "tg"
    )


@dp.callback_query(F.data == "tg2")
async def tg2(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg2",
        "Telegram Premium Obunachi",
        "tg"
    )


@dp.callback_query(F.data == "tg3")
async def tg3(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg3",
        "Telegram Premium Ovozlar",
        "tg"
    )


@dp.callback_query(F.data == "tg4")
async def tg4(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg4",
        "Telegram Prasmotrlar",
        "tg"
    )


@dp.callback_query(F.data == "tg5")
async def tg5(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg5",
        "Telegram Avto Prasmotr",
        "tg"
    )


@dp.callback_query(F.data == "tg6")
async def tg6(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg6",
        "O‘zbek Xizmatlar",
        "tg"
    )


@dp.callback_query(F.data == "tg7")
async def tg7(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg7",
        "Telegram Reaksiyalar",
        "tg"
    )


@dp.callback_query(F.data.in_({"tg8", "tg9", "tg10"}))
async def telegram_unavailable(callback: CallbackQuery):

    await callback.message.edit_text(
        "❌ Ushbu xizmat hozircha mavjud emas.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Orqaga",
                        callback_data="tg"
                    )
                ]
            ]
        )
    )

    await callback.answer()


@dp.callback_query(F.data == "tg11")
async def tg11(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg11",
        "Post ulashish Share",
        "tg"
    )


@dp.callback_query(F.data == "tg12")
async def tg12(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "tg12",
        "Premium Obunachi Yangi Baza",
        "tg"
    )


# =========================================================
# INSTAGRAM TARIFLARI
# =========================================================

@dp.callback_query(F.data == "ig1")
async def ig1(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "ig1",
        "Instagram Obunachilar",
        "ig"
    )


@dp.callback_query(F.data == "ig2")
async def ig2(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "ig2",
        "Instagram Likelar",
        "ig"
    )


@dp.callback_query(F.data == "ig3")
async def ig3(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "ig3",
        "Instagram Prasmotr",
        "ig"
    )


@dp.callback_query(F.data == "ig4")
async def ig4(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "ig4",
        "Instagram Post Comentlar",
        "ig"
    )


@dp.callback_query(F.data == "ig5")
async def ig5(callback: CallbackQuery):
    await show_tariffs(
        callback,
        "ig5",
        "Instagram Istoriya Prasmotrlar",
        "ig"
    )


# =========================================================
# STARS
# =========================================================

@dp.callback_query(F.data == "star_auto")
async def star_auto(callback: CallbackQuery):

    rows = []

    for i, (name, price) in enumerate(STARS):

        rows.append([
            InlineKeyboardButton(
                text=f"{name}: {price:,.0f} so‘m",
                callback_data=f"star_{i}"
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="stars"
        )
    ])

    await callback.message.edit_text(
        "⭐ <b>Telegram Stars</b>\n\n"
        "💰 Narx 100 ta uchun hisoblangan.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=rows
        )
    )

    await callback.answer()


# =========================================================
# GIFTLAR
# =========================================================

@dp.callback_query(F.data == "gift_auto")
async def gift_auto(callback: CallbackQuery):

    rows = []

    for i, (name, price) in enumerate(GIFTS):

        rows.append([
            InlineKeyboardButton(
                text=f"{name} - {price:,.0f} so‘m",
                callback_data=f"gift_{i}"
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="stars"
        )
    ])

    await callback.message.edit_text(
        "🎁 <b>Telegram Giftlar</b>\n\n"
        "💰 Narx 1 dona uchun hisoblangan.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=rows
        )
    )

    await callback.answer()


# =========================================================
# BUYURTMA HOLATLARI
# =========================================================

waiting_order_quantity = {}
waiting_order_link = {}
waiting_order_confirm = {}


def get_selected_tariff(code, index):

    if code == "star":
        if 0 <= index < len(STARS):
            return STARS[index]

    if code == "gift":
        if 0 <= index < len(GIFTS):
            return GIFTS[index]

    tariffs = TARIFFS.get(code)

    if tariffs and 0 <= index < len(tariffs):
        return tariffs[index]

    return None


# =========================================================
# TARIF TANLASH
# =========================================================

@dp.callback_query(
    F.data.regexp(r"^buy_(.+)_([0-9]+)$")
)
async def start_order(callback: CallbackQuery):

    parts = callback.data.split("_")

    if len(parts) != 3:
        await callback.answer(
            "Buyurtma xatosi.",
            show_alert=True
        )
        return

    code = parts[1]
    index = int(parts[2])

    tariff = get_selected_tariff(
        code,
        index
    )

    if not tariff:
        await callback.answer(
            "Tarif topilmadi.",
            show_alert=True
        )
        return

    name, price = tariff
    tg_id = callback.from_user.id

    waiting_order_quantity[tg_id] = {
        "platform_service": code,
        "tariff": name,
        "price": price
    }

    await callback.message.edit_text(
        f"🛒 <b>Buyurtma berish</b>\n\n"
        f"📌 Xizmat: {name}\n"
        f"💰 Narx: {price:,.0f} so‘m / 1000 ta\n\n"
        f"🔢 Qancha miqdor buyurtma qilmoqchisiz?\n\n"
        f"Masalan: <code>1000</code>"
    )

    await callback.answer()


# =========================================================
# STARS/GIFT BUYURTMASI
# =========================================================

@dp.callback_query(
    F.data.regexp(r"^(star|gift)_([0-9]+)$")
)
async def start_special_order(callback: CallbackQuery):

    parts = callback.data.split("_")

    code = parts[0]
    index = int(parts[1])

    tariff = get_selected_tariff(
        code,
        index
    )

    if not tariff:
        await callback.answer(
            "Tarif topilmadi.",
            show_alert=True
        )
        return

    name, price = tariff
    tg_id = callback.from_user.id

    waiting_order_quantity[tg_id] = {
        "platform_service": code,
        "tariff": name,
        "price": price
    }

    await callback.message.edit_text(
        f"🛒 <b>Buyurtma berish</b>\n\n"
        f"📌 Xizmat: {name}\n"
        f"💰 Narx: {price:,.0f} so‘m\n\n"
        f"🔢 Qancha miqdor kerak?\n\n"
        f"Masalan: <code>1</code>"
    )

    await callback.answer()


# =========================================================
# MIQDOR
# =========================================================

@dp.message(
    lambda m:
    m.from_user.id in waiting_order_quantity
    and m.text not in {
        "🗂️ Xizmatlar",
        "🛒 Buyurtmalarim",
        "💰 Mening hisobim",
        "💳 Hisob to‘ldirish",
        "✍️ Yordam xizmati",
        "👨‍💻 Admin"
    }
)
async def order_quantity(message: Message):

    tg_id = message.from_user.id
    data = waiting_order_quantity.get(tg_id)

    if not data:
        return

    try:
        quantity = int(message.text.replace(" ", ""))

        if quantity <= 0:
            raise ValueError

    except:
        await message.answer(
            "❌ Miqdorni faqat raqam bilan yozing.\n"
            "Masalan: <code>1000</code>"
        )
        return

    total = data["price"] * quantity / 1000
    balance = get_balance(tg_id)

    if balance < total:

        waiting_order_quantity.pop(tg_id, None)

        await message.answer(
            f"❌ <b>Hisobingizda pul yetarli emas.</b>\n\n"
            f"💰 Buyurtma narxi: {total:,.0f} so‘m\n"
            f"💳 Balansingiz: {balance:,.0f} so‘m\n\n"
            f"Hisobingizni to‘ldiring.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💳 Hisob to‘ldirish",
                            callback_data="deposit"
                        )
                    ]
                ]
            )
        )
        return

    data["quantity"] = quantity
    data["total"] = total

    waiting_order_link[tg_id] = data
    waiting_order_quantity.pop(tg_id, None)

    await message.answer(
        f"📌 Xizmat: {data['tariff']}\n"
        f"🔢 Miqdor: {quantity:,} ta\n"
        f"💰 Jami: {total:,.0f} so‘m\n\n"
        f"🔗 Qaysi linkga yubormoqchisiz?\n"
        f"Yubormoqchi bo‘lgan link yoki username-ni yuboring."
    )

# =========================================================
# LINK
# =========================================================

@dp.message(
    lambda message:
    message.from_user.id in waiting_order_link
)
async def order_link(message: Message):

    tg_id = message.from_user.id

    data = waiting_order_link.get(tg_id)

    if not data:
        return

    if not message.text:

        await message.answer(
            "❌ Link yoki username yuboring."
        )

        return

    link = message.text.strip()

    if len(link) < 2:

        await message.answer(
            "❌ Link yoki username noto‘g‘ri."
        )

        return

    data["link"] = link

    waiting_order_link.pop(
        tg_id,
        None
    )

    waiting_order_confirm[tg_id] = data

    await message.answer(
        f"🛒 <b>Buyurtmangiz</b>\n\n"
        f"📌 Tarif: {data['tariff']}\n"
        f"🔢 Miqdor: {data['quantity']:,}\n"
        f"💰 Jami: {data['total']:,.0f} so‘m\n"
        f"🔗 Link: <code>{link}</code>\n\n"
        f"Buyurtmani tasdiqlaysizmi?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Tasdiqlash",
                        callback_data="order_confirm"
                    ),
                    InlineKeyboardButton(
                        text="❌ Bekor qilish",
                        callback_data="order_cancel"
                    )
                ]
            ]
        )
    )
    
# =========================================================
# BUYURTMA TASDIQLASH
# =========================================================

@dp.callback_query(F.data == "order_confirm")
async def order_confirm(callback: CallbackQuery):

    tg_id = callback.from_user.id
    data = waiting_order_confirm.get(tg_id)

    if not data:
        await callback.answer(
            "Buyurtma topilmadi.",
            show_alert=True
        )
        return

    balance = get_balance(tg_id)

    if balance < data["total"]:

        waiting_order_confirm.pop(
            tg_id,
            None
        )

        await callback.message.edit_text(
            "❌ Hisobingizda pul yetarli emas.\n\n"
            "Iltimos, hisobingizni to‘ldiring."
        )

        await callback.answer()
        return

    # Pulni yechish
    change_balance(
        tg_id,
        -data["total"]
    )

    cursor.execute(
        """
        INSERT INTO orders
        (
            telegram_id,
            service,
            status,
            quantity,
            price,
            total,
            platform,
            link,
            tariff
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            tg_id,
            data["platform_service"],
            "waiting_admin",
            data["quantity"],
            data["price"],
            data["total"],
            data["platform_service"],
            data["link"],
            data["tariff"]
        )
    )

    order_id = cursor.lastrowid

    db.commit()

    remaining = get_balance(tg_id)

    waiting_order_confirm.pop(
        tg_id,
        None
    )

    await callback.message.edit_text(
        f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"💸 Buyurtma uchun: "
        f"{data['total']:,.0f} so‘m yechildi.\n"
        f"💰 Qolgan balans: "
        f"{remaining:,.0f} so‘m\n\n"
        f"⏳ Arizangiz admin tomonidan ko‘rib chiqiladi."
    )

    uid = get_or_create_user(tg_id)

    admin_text = (
        f"🛒 <b>YANGI BUYURTMA #{order_id}</b>\n\n"
        f"👤 Mijoz: {callback.from_user.full_name}\n"
        f"🆔 Mijoz ID: <code>{uid}</code>\n"
        f"🔢 Telegram ID: <code>{tg_id}</code>\n\n"
        f"📱 Platforma: <b>{data['platform_service']}</b>\n"
        f"📌 Tarif: <b>{data['tariff']}</b>\n"
        f"🔢 Miqdor: <b>{data['quantity']:,}</b>\n"
        f"💰 Narx: <b>{data['price']:,.0f} so‘m</b>\n"
        f"💵 Jami: <b>{data['total']:,.0f} so‘m</b>\n"
        f"🔗 Link: <code>{data['link']}</code>"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Qabul qilish",
                    callback_data=f"admin_accept_{order_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"admin_reject_{order_id}"
                )
            ]
        ]
    )

    try:

        sent = await bot.send_message(
            ADMIN_ID,
            admin_text,
            reply_markup=kb
        )

        cursor.execute(
            """
            UPDATE orders
            SET admin_message_id=?
            WHERE id=?
            """,
            (
                sent.message_id,
                order_id
            )
        )

        db.commit()

    except Exception as e:

        # Admin xabar ketmasa pulni qaytarish
        change_balance(
            tg_id,
            data["total"]
        )

        cursor.execute(
            """
            UPDATE orders
            SET status='system_error'
            WHERE id=?
            """,
            (order_id,)
        )

        db.commit()

        await callback.message.answer(
            "❌ Admin paneliga yuborishda xatolik.\n"
            "Pul balansingizga qaytarildi."
        )

        print(
            "ADMIN SEND ERROR:",
            e
        )

    await callback.answer()


# =========================================================
# BUYURTMA BEKOR QILISH
# =========================================================

@dp.callback_query(F.data == "order_cancel")
async def order_cancel(callback: CallbackQuery):

    tg_id = callback.from_user.id

    waiting_order_confirm.pop(
        tg_id,
        None
    )

    await callback.message.edit_text(
        "❌ Buyurtma bekor qilindi.\n\n"
        "Hisobingizdan pul yechilmadi."
    )

    await callback.answer()


# =========================================================
# ADMIN BUYURTMANI QABUL QILISH
# =========================================================

@dp.callback_query(
    F.data.startswith("admin_accept_")
)
async def admin_accept(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )

        return

    order_id = int(
        callback.data.split("_")[2]
    )

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE id=?
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    if not order:

        await callback.answer(
            "Buyurtma topilmadi.",
            show_alert=True
        )

        return

    if order["status"] != "waiting_admin":

        await callback.answer(
            "Bu buyurtma allaqachon ko‘rib chiqilgan.",
            show_alert=True
        )

        return

    cursor.execute(
        """
        UPDATE orders
        SET status='accepted'
        WHERE id=?
        """,
        (order_id,)
    )

    db.commit()

    await bot.send_message(
        order["telegram_id"],
        f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"🆔 Buyurtma: #{order_id}\n"
        f"📌 Xizmat: {order['tariff']}\n"
        f"🔢 Miqdor: {order['quantity']:,}\n\n"
        f"⏳ Buyurtma bajarilishi kutilmoqda."
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        f"✅ Buyurtma #{order_id} qabul qilindi."
    )

    await callback.answer()


# =========================================================
# ADMIN BUYURTMANI RAD ETISH
# =========================================================

@dp.callback_query(
    F.data.startswith("admin_reject_")
)
async def admin_reject(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )

        return

    order_id = int(
        callback.data.split("_")[2]
    )

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE id=?
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    if not order:

        await callback.answer(
            "Buyurtma topilmadi.",
            show_alert=True
        )

        return

    if order["status"] != "waiting_admin":

        await callback.answer(
            "Bu buyurtma allaqachon ko‘rib chiqilgan.",
            show_alert=True
        )

        return

    # Pulni qaytarish
    change_balance(
        order["telegram_id"],
        order["total"]
    )

    cursor.execute(
        """
        UPDATE orders
        SET status='rejected'
        WHERE id=?
        """,
        (order_id,)
    )

    db.commit()

    new_balance = get_balance(
        order["telegram_id"]
    )

    await bot.send_message(
        order["telegram_id"],
        f"❌ <b>Buyurtmangiz rad etildi.</b>\n\n"
        f"🆔 Buyurtma: #{order_id}\n"
        f"💰 {order['total']:,.0f} so‘m balansingizga qaytarildi.\n"
        f"💳 Joriy balans: {new_balance:,.0f} so‘m"
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        f"❌ Buyurtma #{order_id} rad etildi.\n"
        f"💰 Pul mijozga qaytarildi."
    )

    await callback.answer()


# =========================================================
# BUYURTMALARIM
# =========================================================

@dp.message(
    F.text.func(
        lambda text:
        text is not None
        and text.endswith(" Buyurtmalarim")
    )
)
async def orders(message: Message):

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE telegram_id=?
        ORDER BY id DESC
        LIMIT 20
        """,
        (message.from_user.id,)
    )

    rows = cursor.fetchall()

    if not rows:

        await message.answer(
            "📭 Sizda hozircha buyurtmalar mavjud emas."
        )

        return

    text = "🛒 <b>Sizning buyurtmalaringiz</b>\n\n"

    status_names = {
        "waiting_admin": "⏳ Ko‘rib chiqilmoqda",
        "accepted": "✅ Qabul qilingan",
        "rejected": "❌ Rad etilgan",
        "system_error": "⚠️ Texnik xato",
    }

    for order in rows:

        status = status_names.get(
            order["status"],
            order["status"]
        )

        text += (
            f"🆔 <b>#{order['id']}</b>\n"
            f"📱 {order['platform']}\n"
            f"📌 {order['tariff']}\n"
            f"🔢 {order['quantity']:,} dona\n"
            f"💰 {order['total']:,.0f} so‘m\n"
            f"📊 {status}\n\n"
        )

    await message.answer(text)


# =========================================================
# MENING HISOBIM
# =========================================================

@dp.message(
    F.text.func(
        lambda text:
        text is not None
        and text.endswith(" Mening hisobim")
    )
)
async def balance(message: Message):

    uid = get_or_create_user(
        message.from_user.id
    )

    bal = get_balance(
        message.from_user.id
    )

    await message.answer(
        f"👤 <b>Mening hisobim</b>\n\n"
        f"🆔 ID: <code>{uid}</code>\n"
        f"💰 Balans: <b>{bal:,.0f} so‘m</b>"
    )


# =========================================================
# HISOB TO‘LDIRISH
# =========================================================

def deposit_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 HUMO",
                    callback_data="card_HUMO"
                ),
                InlineKeyboardButton(
                    text="💳 UZCARD",
                    callback_data="card_UZCARD"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 VISA",
                    callback_data="card_VISA"
                )
            ]
        ]
    )


@dp.message(
    F.text.func(
        lambda text:
        text is not None
        and text.endswith(" Hisob to‘ldirish")
    )
)
async def deposit(message: Message):

    await message.answer(
        "📲 <b>To‘lov turini tanlang:</b>",
        reply_markup=deposit_keyboard()
    )


@dp.callback_query(F.data == "deposit")
async def deposit_callback(callback: CallbackQuery):

    await callback.message.answer(
        "📲 <b>To‘lov turini tanlang:</b>",
        reply_markup=deposit_keyboard()
    )

    await callback.answer()


# =========================================================
# KARTA
# =========================================================

@dp.callback_query(
    F.data.startswith("card_")
)
async def card_selected(callback: CallbackQuery):

    card_name = callback.data.split(
        "_",
        1
    )[1]

    card = CARDS.get(card_name)

    if not card:

        await callback.answer(
            "Karta topilmadi.",
            show_alert=True
        )

        return

    await callback.message.edit_text(
        f"📲 <b>To‘lov turi:</b> {card_name}\n\n"
        f"💳 <b>{card_name}:</b> "
        f"<code>{card['number']}</code>\n\n"
        f"👤 <b>Karta egasi:</b> "
        f"{card['owner']}\n\n"
        f"1️⃣ Kartaga kerakli summani yuboring.\n"
        f"2️⃣ «✅ To‘lov qildim» tugmasini bosing.\n"
        f"3️⃣ Yuborgan summangizni yozing.\n"
        f"4️⃣ Chek rasmini yuboring.\n"
        f"5️⃣ Admin tasdiqlashini kuting.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ To‘lov qildim",
                        callback_data=f"pay_{card_name}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="◀️ Orqaga",
                        callback_data="deposit"
                    )
                ]
            ]
        )
    )

    await callback.answer()


# =========================================================
# TO‘LOV HOLATLARI
# =========================================================

payment_waiting_amount = {}
payment_waiting_receipt = {}


@dp.callback_query(
    F.data.startswith("pay_")
)
async def payment_start(callback: CallbackQuery):

    card_name = callback.data.split(
        "_",
        1
    )[1]

    payment_waiting_amount[
        callback.from_user.id
    ] = card_name

    await callback.message.answer(
        "💰 <b>To‘lov qilgan summangizni yozing.</b>\n\n"
        "Masalan: <code>50000</code>"
    )

    await callback.answer()


# =========================================================
# TO‘LOV SUMMASI
# =========================================================

@dp.message(
    lambda message:
    message.from_user.id in payment_waiting_amount
)
async def payment_amount_handler(message: Message):

    tg_id = message.from_user.id

    try:

        amount = float(
            message.text
            .replace(" ", "")
            .replace(",", "")
        )

        if amount <= 0:
            raise ValueError

    except Exception:

        await message.answer(
            "❌ Summani faqat raqam bilan yozing.\n"
            "Masalan: <code>50000</code>"
        )

        return

    card_name = payment_waiting_amount.pop(
        tg_id
    )

    payment_waiting_receipt[tg_id] = {
        "amount": amount,
        "card": card_name
    }

    await message.answer(
        "📸 <b>To‘lov chekini yuboring.</b>\n\n"
        "Chek rasmini shu yerga yuboring."
    )


# =========================================================
# CHEK
# =========================================================

@dp.message(
    lambda message:
    message.from_user.id in payment_waiting_receipt
    and message.photo
)
async def receipt_handler(message: Message):

    tg_id = message.from_user.id

    data = payment_waiting_receipt.pop(
        tg_id
    )

    uid = get_or_create_user(tg_id)

    await message.answer(
        "✅ To‘lovingiz bo‘yicha ariza admin'ga yuborildi.\n\n"
        "⏳ Tasdiqlanishini kuting."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=(
                        f"payment_accept_"
                        f"{tg_id}_"
                        f"{int(data['amount'])}"
                    )
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=(
                        f"payment_reject_"
                        f"{tg_id}_"
                        f"{int(data['amount'])}"
                    )
                )
            ]
        ]
    )

    caption = (
        f"💳 <b>YANGI TO‘LOV</b>\n\n"
        f"👤 Mijoz: {message.from_user.full_name}\n"
        f"🆔 Mijoz ID: <code>{uid}</code>\n"
        f"🔢 Telegram ID: <code>{tg_id}</code>\n"
        f"💳 Karta: {data['card']}\n"
        f"💰 Summa: <b>{data['amount']:,.0f} so‘m</b>\n\n"
        f"To‘lovni tekshiring."
    )

    await bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=caption,
        reply_markup=kb
    )


# =========================================================
# CHEK RASM EMAS
# =========================================================

@dp.message(
    lambda message:
    message.from_user.id in payment_waiting_receipt
)
async def receipt_not_photo(message: Message):

    await message.answer(
        "📸 Iltimos, chekni <b>rasm</b> ko‘rinishida yuboring."
    )


# =========================================================
# TO‘LOVNI TASDIQLASH
# =========================================================

@dp.callback_query(
    F.data.startswith("payment_accept_")
)
async def payment_accept(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )

        return

    parts = callback.data.split("_")

    tg_id = int(parts[2])
    amount = float(parts[3])

    change_balance(
        tg_id,
        amount
    )

    new_balance = get_balance(
        tg_id
    )

    await bot.send_message(
        tg_id,
        f"✅ <b>To‘lovingiz tasdiqlandi!</b>\n\n"
        f"💰 Hisobingizga: "
        f"{amount:,.0f} so‘m qo‘shildi.\n"
        f"💳 Joriy balans: "
        f"{new_balance:,.0f} so‘m"
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        f"✅ To‘lov tasdiqlandi.\n"
        f"💰 {amount:,.0f} so‘m balansga qo‘shildi."
    )

    await callback.answer()


# =========================================================
# TO‘LOVNI RAD ETISH
# =========================================================

@dp.callback_query(
    F.data.startswith("payment_reject_")
)
async def payment_reject(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )

        return

    parts = callback.data.split("_")

    tg_id = int(parts[2])
    amount = float(parts[3])

    await bot.send_message(
        tg_id,
        f"❌ <b>To‘lovingiz rad etildi.</b>\n\n"
        f"💰 Summa: {amount:,.0f} so‘m\n"
        f"Sababi: to‘lov tasdiqlanmadi."
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        "❌ To‘lov rad etildi."
    )

    await callback.answer()


# =========================================================
# ADMIN TUGMASI
# =========================================================

@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and m.text is not None
    and m.text.endswith(" Admin")
)
async def admin_button(message: Message):
    await message.answer(
        "👨‍💻 <b>Admin panel</b>\n\n"
        "Mijozni ko‘rish uchun <code>#MijozID</code> yuboring.\n"
        "Masalan: <code>#1234567</code>"
    )


# =========================================================
# YORDAM
# =========================================================

waiting_question = set()
waiting_answer = {}


@dp.message(
    F.text.func(
        lambda text:
        text is not None
        and text.endswith(" Yordam xizmati")
    )
)
async def help_service(message: Message):

    waiting_question.add(
        message.from_user.id
    )

    await message.answer(
        "❓ Savolingizni shu yerga yozing."
    )


@dp.message(
    lambda message:
    message.from_user.id in waiting_question
    and message.from_user.id != ADMIN_ID
)
async def question(message: Message):

    waiting_question.discard(
        message.from_user.id
    )

    uid = get_or_create_user(
        message.from_user.id
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✍️ Javob yozish",
                    callback_data=(
                        f"answer_{message.from_user.id}"
                    )
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=(
                        f"reject_{message.from_user.id}"
                    )
                )
            ]
        ]
    )

    await bot.send_message(
        ADMIN_ID,
        f"📩 <b>YANGI SAVOL</b>\n\n"
        f"👤 {message.from_user.full_name}\n"
        f"🆔 <code>{uid}</code>\n"
        f"🔢 TG ID: <code>{message.from_user.id}</code>\n\n"
        f"💬 Savol:\n{message.text}",
        reply_markup=kb
    )

    await message.answer(
        "✅ Savolingiz operatorga yuborildi."
    )


# =========================================================
# ADMIN — #MIJOZ_ID
# =========================================================

@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and m.text
    and m.text.startswith("#")
)
async def admin_client_info(message: Message):

    try:
        user_id = int(message.text[1:].strip())
    except:
        await message.answer(
            "❌ ID noto‘g‘ri.\n\n"
            "To‘g‘ri ko‘rinishi:\n"
            "<code>#1234567</code>"
        )
        return

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        await message.answer(
            f"❌ <b>{user_id}</b> ID li mijoz topilmadi."
        )
        return

    tg_id = user["telegram_id"]
    balance_value = float(user["balance"])

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE telegram_id=?
        """,
        (tg_id,)
    )

    order_count = cursor.fetchone()["count"]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Pul qo‘shish",
                    callback_data=f"client_add_{user_id}"
                ),
                InlineKeyboardButton(
                    text="➖ Pul ayirish",
                    callback_data=f"client_minus_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="0️⃣ Balansni 0 qilish",
                    callback_data=f"client_zero_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Buyurtmalarini ko‘rish",
                    callback_data=f"client_orders_{user_id}"
                )
            ]
        ]
    )

    await message.answer(
        f"👤 <b>MIJOZ MA'LUMOTLARI</b>\n\n"
        f"🆔 Mijoz ID: <code>{user_id}</code>\n"
        f"🔢 Telegram ID: <code>{tg_id}</code>\n"
        f"💰 Balans: <b>{balance_value:,.0f} so‘m</b>\n"
        f"📦 Buyurtmalar: <b>{order_count} ta</b>",
        reply_markup=kb
    )


# =========================================================
# PUL QO‘SHISH / AYIRISH HOLATI
# =========================================================

admin_money_action = {}


@dp.callback_query(F.data.startswith("client_add_"))
async def client_add_money(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(
        callback.data.replace(
            "client_add_",
            ""
        )
    )

    admin_money_action[ADMIN_ID] = {
        "user_id": user_id,
        "action": "add"
    }

    await callback.message.answer(
        f"➕ <b>Balans qo‘shish</b>\n\n"
        f"🆔 Mijoz ID: <code>{user_id}</code>\n\n"
        f"Qancha pul qo‘shmoqchisiz?\n"
        f"Masalan: <code>50000</code>"
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("client_minus_"))
async def client_minus_money(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(
        callback.data.replace(
            "client_minus_",
            ""
        )
    )

    admin_money_action[ADMIN_ID] = {
        "user_id": user_id,
        "action": "minus"
    }

    await callback.message.answer(
        f"➖ <b>Balans ayirish</b>\n\n"
        f"🆔 Mijoz ID: <code>{user_id}</code>\n\n"
        f"Qancha pul ayirmoqchisiz?\n"
        f"Masalan: <code>50000</code>"
    )

    await callback.answer()


@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and ADMIN_ID in admin_money_action
)
async def admin_money_amount(message: Message):

    data = admin_money_action.get(ADMIN_ID)

    try:
        amount = float(
            message.text
            .replace(" ", "")
            .replace(",", "")
        )

        if amount <= 0:
            raise ValueError

    except:
        await message.answer(
            "❌ Summani raqam bilan kiriting.\n\n"
            "Masalan: <code>50000</code>"
        )
        return

    user_id = data["user_id"]

    tg_id = get_telegram_id_by_user_id(
        user_id
    )

    if not tg_id:

        admin_money_action.pop(
            ADMIN_ID,
            None
        )

        await message.answer(
            "❌ Mijoz topilmadi."
        )
        return

    if data["action"] == "add":

        change_balance(
            tg_id,
            amount
        )

        action_text = "qo‘shildi"

    else:

        current_balance = get_balance(
            tg_id
        )

        if amount > current_balance:
            amount = current_balance

        change_balance(
            tg_id,
            -amount
        )

        action_text = "ayirildi"

    new_balance = get_balance(
        tg_id
    )

    admin_money_action.pop(
        ADMIN_ID,
        None
    )

    await message.answer(
        f"✅ <b>Balans yangilandi.</b>\n\n"
        f"🆔 Mijoz ID: <code>{user_id}</code>\n"
        f"💰 {amount:,.0f} so‘m {action_text}.\n"
        f"💳 Yangi balans: <b>{new_balance:,.0f} so‘m</b>"
    )

    try:

        if data["action"] == "add":

            await bot.send_message(
                tg_id,
                f"💰 Hisobingizga "
                f"<b>{amount:,.0f} so‘m</b> qo‘shildi.\n\n"
                f"💳 Balansingiz: "
                f"<b>{new_balance:,.0f} so‘m</b>"
            )

        else:

            await bot.send_message(
                tg_id,
                f"💸 Hisobingizdan "
                f"<b>{amount:,.0f} so‘m</b> ayirildi.\n\n"
                f"💳 Balansingiz: "
                f"<b>{new_balance:,.0f} so‘m</b>"
            )

    except:
        pass


# =========================================================
# BALANSNI 0 QILISH
# =========================================================

@dp.callback_query(F.data.startswith("client_zero_"))
async def client_zero_balance(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(
        callback.data.replace(
            "client_zero_",
            ""
        )
    )

    tg_id = get_telegram_id_by_user_id(
        user_id
    )

    if not tg_id:
        await callback.answer(
            "Mijoz topilmadi.",
            show_alert=True
        )
        return

    cursor.execute(
        """
        UPDATE users
        SET balance=0
        WHERE telegram_id=?
        """,
        (tg_id,)
    )

    db.commit()

    await callback.message.answer(
        f"0️⃣ <b>Balans 0 qilindi.</b>\n\n"
        f"🆔 Mijoz ID: <code>{user_id}</code>\n"
        f"💰 Yangi balans: <b>0 so‘m</b>"
    )

    try:
        await bot.send_message(
            tg_id,
            "💳 Hisobingizdagi balans 0 qilindi."
        )
    except:
        pass

    await callback.answer()


# =========================================================
# MIJOZ BUYURTMALARI
# =========================================================

@dp.callback_query(F.data.startswith("client_orders_"))
async def client_orders(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(
        callback.data.replace(
            "client_orders_",
            ""
        )
    )

    tg_id = get_telegram_id_by_user_id(
        user_id
    )

    if not tg_id:
        await callback.answer(
            "Mijoz topilmadi.",
            show_alert=True
        )
        return

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE telegram_id=?
        ORDER BY id DESC
        LIMIT 50
        """,
        (tg_id,)
    )

    orders_list = cursor.fetchall()

    if not orders_list:

        await callback.message.answer(
            f"📦 <b>Mijoz buyurtmalari</b>\n\n"
            f"🆔 ID: <code>{user_id}</code>\n\n"
            f"📭 Buyurtmalari yo‘q."
        )

        await callback.answer()
        return

    text = (
        f"📦 <b>MIJOZ BUYURTMALARI</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📊 Jami: <b>{len(orders_list)} ta</b>\n\n"
    )

    for order in orders_list:

        status = {
            "waiting_admin": "⏳ Kutilmoqda",
            "accepted": "✅ Qabul qilingan",
            "rejected": "❌ Rad etilgan",
            "system_error": "⚠️ Texnik xato",
        }.get(
            order["status"],
            order["status"]
        )

        text += (
            f"🛒 <b>#{order['id']}</b>\n"
            f"📱 {order['platform']}\n"
            f"📌 {order['tariff']}\n"
            f"🔢 {order['quantity']:,} dona\n"
            f"💰 {order['total']:,.0f} so‘m\n"
            f"📊 {status}\n\n"
        )

    await callback.message.answer(
        text
    )

    await callback.answer()
# =========================================================
# ADMIN PANEL
# =========================================================

admin_money_action = {}
admin_client_orders = {}


def admin_client_keyboard(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Pul qo‘shish",
                    callback_data=f"admin_add_{user_id}"
                ),
                InlineKeyboardButton(
                    text="➖ Pul ayirish",
                    callback_data=f"admin_sub_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="0️⃣ Balansni 0 qilish",
                    callback_data=f"admin_zero_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛒 Buyurtmalar",
                    callback_data=f"admin_orders_{user_id}"
                )
            ]
        ]
    )


@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and m.text
    and m.text.startswith("#")
)
async def admin_find_client(message: Message):

    try:
        user_id = int(message.text[1:].strip())
    except:
        await message.answer(
            "❌ ID noto‘g‘ri.\n\n"
            "Masalan: <code>#1234567</code>"
        )
        return

    tg_id = get_telegram_id_by_user_id(user_id)

    if not tg_id:
        await message.answer(
            "❌ Bunday mijoz topilmadi."
        )
        return

    balance = get_balance(tg_id)

    cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE telegram_id=?
        """,
        (tg_id,)
    )

    order_count = cursor.fetchone()["count"]

    await message.answer(
        f"👤 <b>Mijoz ma’lumotlari</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"🔢 Telegram ID: <code>{tg_id}</code>\n"
        f"💰 Balans: <b>{balance:,.0f} so‘m</b>\n"
        f"🛒 Buyurtmalar: <b>{order_count} ta</b>",
        reply_markup=admin_client_keyboard(user_id)
    )


@dp.callback_query(F.data.startswith("admin_add_"))
async def admin_add_start(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(callback.data.split("_")[2])

    admin_money_action[ADMIN_ID] = {
        "action": "add",
        "user_id": user_id
    }

    await callback.message.answer(
        "➕ <b>Qancha pul qo‘shmoqchisiz?</b>\n\n"
        "Masalan: <code>50000</code>"
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("admin_sub_"))
async def admin_sub_start(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(callback.data.split("_")[2])

    admin_money_action[ADMIN_ID] = {
        "action": "sub",
        "user_id": user_id
    }

    await callback.message.answer(
        "➖ <b>Qancha pul ayirmoqchisiz?</b>\n\n"
        "Masalan: <code>50000</code>"
    )

    await callback.answer()


@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and m.from_user.id in admin_money_action
)
async def admin_money_handler(message: Message):

    data = admin_money_action.get(ADMIN_ID)

    if not data:
        return

    try:
        amount = float(
            message.text.replace(" ", "").replace(",", "")
        )

        if amount <= 0:
            raise ValueError

    except:
        await message.answer(
            "❌ Summani faqat raqam bilan yozing.\n"
            "Masalan: <code>50000</code>"
        )
        return

    user_id = data["user_id"]
    tg_id = get_telegram_id_by_user_id(user_id)

    if not tg_id:
        admin_money_action.pop(ADMIN_ID, None)

        await message.answer(
            "❌ Mijoz topilmadi."
        )
        return

    if data["action"] == "add":

        change_balance(
            tg_id,
            amount
        )

        await message.answer(
            f"✅ <b>Pul qo‘shildi.</b>\n\n"
            f"🆔 Mijoz ID: <code>{user_id}</code>\n"
            f"➕ Qo‘shildi: <b>{amount:,.0f} so‘m</b>\n"
            f"💰 Yangi balans: <b>{get_balance(tg_id):,.0f} so‘m</b>"
        )

    else:

        balance = get_balance(tg_id)

        if amount > balance:
            amount = balance

        change_balance(
            tg_id,
            -amount
        )

        await message.answer(
            f"✅ <b>Pul ayirildi.</b>\n\n"
            f"🆔 Mijoz ID: <code>{user_id}</code>\n"
            f"➖ Ayirildi: <b>{amount:,.0f} so‘m</b>\n"
            f"💰 Yangi balans: <b>{get_balance(tg_id):,.0f} so‘m</b>"
        )

    admin_money_action.pop(
        ADMIN_ID,
        None
    )


@dp.callback_query(F.data.startswith("admin_zero_"))
async def admin_zero(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(callback.data.split("_")[2])

    tg_id = get_telegram_id_by_user_id(user_id)

    if not tg_id:
        await callback.answer(
            "Mijoz topilmadi.",
            show_alert=True
        )
        return

    balance = get_balance(tg_id)

    change_balance(
        tg_id,
        -balance
    )

    await callback.message.answer(
        f"0️⃣ <b>Balans 0 qilindi.</b>\n\n"
        f"🆔 Mijoz ID: <code>{user_id}</code>"
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("admin_orders_"))
async def admin_orders(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )
        return

    user_id = int(callback.data.split("_")[2])

    tg_id = get_telegram_id_by_user_id(user_id)

    if not tg_id:
        await callback.answer(
            "Mijoz topilmadi.",
            show_alert=True
        )
        return

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE telegram_id=?
        ORDER BY id DESC
        LIMIT 50
        """,
        (tg_id,)
    )

    rows = cursor.fetchall()

    if not rows:
        await callback.message.answer(
            f"🛒 <b>Buyurtmalar</b>\n\n"
            f"🆔 Mijoz ID: <code>{user_id}</code>\n\n"
            f"📭 Buyurtmalar mavjud emas."
        )

        await callback.answer()
        return

    text = (
        f"🛒 <b>Mijoz buyurtmalari</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n\n"
    )

    for order in rows:

        status = {
            "waiting_admin": "⏳ Kutilmoqda",
            "accepted": "✅ Qabul qilingan",
            "rejected": "❌ Rad etilgan",
            "system_error": "⚠️ Texnik xato",
        }.get(
            order["status"],
            order["status"]
        )

        text += (
            f"🆔 <b>#{order['id']}</b>\n"
            f"📱 {order['platform']}\n"
            f"📌 {order['tariff']}\n"
            f"🔢 {order['quantity']:,} dona\n"
            f"💰 {order['total']:,.0f} so‘m\n"
            f"📊 {status}\n\n"
        )

    await callback.message.answer(text)

    await callback.answer()


# =========================================================
# ADMIN JAVOBI
# =========================================================

@dp.callback_query(
    F.data.startswith("answer_")
)
async def answer_start(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )

        return

    client = int(
        callback.data.split("_")[1]
    )

    waiting_answer[ADMIN_ID] = client

    await callback.message.answer(
        "✍️ Mijozga yuboriladigan javobni yozing."
    )

    await callback.answer()


@dp.message(
    lambda message:
    message.from_user.id == ADMIN_ID
    and ADMIN_ID in waiting_answer
)
async def answer_send(message: Message):

    client = waiting_answer.pop(
        ADMIN_ID
    )

    try:

        await bot.send_message(
            client,
            f"👨‍💻 <b>Operator javobi</b>\n\n"
            f"{message.text}"
        )

        await message.answer(
            "✅ Javob mijozga yuborildi."
        )

    except Exception as e:

        await message.answer(
            f"❌ Xatolik:\n<code>{e}</code>"
        )


# =========================================================
# SAVOLNI RAD ETISH
# =========================================================

@dp.callback_query(
    F.data.startswith("reject_")
)
async def reject_question(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Siz admin emassiz.",
            show_alert=True
        )

        return

    client = int(
        callback.data.split("_")[1]
    )

    try:

        await bot.send_message(
            client,
            "❌ Savolingiz rad etildi."
        )

    except Exception:
        pass

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.answer(
        "Rad etildi"
    )


# =========================================================
# EMOJI SOZLAMASI — ADMIN
# =========================================================
emoji_waiting = {}

EMOJI_MENUS = {
    # GLAVNIY MENU
    "Xizmatlar": "services",
    "Buyurtmalarim": "orders",
    "Mening hisobim": "balance",
    "Hisob to‘ldirish": "deposit",
    "Yordam xizmati": "help",
    "Admin": "admin",

    # PLATFORMALAR
    "Telegram": "telegram",
    "Instagram": "instagram",
    "TikTok": "tiktok",
    "YouTube": "youtube",
    "Stars": "stars",

    # TELEGRAM ICHKI MENULAR
    "Telegram Obunachi": "tg1",
    "Telegram Premium Obunachi": "tg2",
    "Telegram Premium Ovozlar": "tg3",
    "Telegram Prasmotrlar": "tg4",
    "Telegram AvtoPost": "tg5",
    "Telegram O‘zbek Xizmatlar": "tg6",
    "Telegram Reaksiyalar": "tg7",
    "Telegram Post Ulashish": "tg11",
    "Telegram Premium Yangi Baza": "tg12",

    # INSTAGRAM ICHKI MENULAR
    "Instagram Obunachilar": "ig1",
    "Instagram Likelar": "ig2",
    "Instagram Prasmotr": "ig3",
    "Instagram Commentlar": "ig4",
    "Instagram Istoriya Prasmotrlar": "ig5",
    "Instagram Jonli Efir": "ig6",
    "Instagram O‘zbek Xizmatlar": "ig7",

    # STARS
    "Telegram Stars": "star",
    "Telegram Giftlar": "gift",
}


DEFAULT_MENU_EMOJIS = {
    "services": "🗂️",
    "orders": "🛒",
    "balance": "💰",
    "deposit": "💳",
    "help": "✍️",
    "admin": "👨‍💻",

    "telegram": "📱",
    "instagram": "📸",
    "tiktok": "🎵",
    "youtube": "▶️",
    "stars": "⭐",

    "tg1": "👥",
    "tg2": "💎",
    "tg3": "⭐",
    "tg4": "👁️",
    "tg5": "👁️",
    "tg6": "🇺🇿",
    "tg7": "❤️",
    "tg11": "🔄",
    "tg12": "💎",

    "ig1": "👥",
    "ig2": "❤️",
    "ig3": "👁️",
    "ig4": "💬",
    "ig5": "👀",
    "ig6": "🔴",
    "ig7": "🇺🇿",

    "star": "⭐",
    "gift": "🎁",
}


# =========================================================
# ODDIY EMOJI SAQLASH
# =========================================================

def set_menu_emoji(key, emoji):
    cursor.execute(
        """
        INSERT INTO settings (name, value)
        VALUES (?, ?)
        ON CONFLICT(name)
        DO UPDATE SET value=excluded.value
        """,
        (f"menu_emoji_{key}", emoji)
    )

    db.commit()


def get_custom_emoji(key):
    cursor.execute(
        "SELECT value FROM settings WHERE name=?",
        (f"custom_emoji_{key}",)
    )
    row = cursor.fetchone()
    return row["value"] if row else None


def get_menu_emoji(key):
    custom_id = get_custom_emoji(key)
    if custom_id:
        return f'<tg-emoji emoji-id="{custom_id}">⭐</tg-emoji>'

    cursor.execute(
        "SELECT value FROM settings WHERE name=?",
        (f"menu_emoji_{key}",)
    )
    row = cursor.fetchone()
    if row:
        return row["value"]

    return DEFAULT_MENU_EMOJIS.get(key, "🔹")


def get_button_emoji(key):
    custom_id = get_custom_emoji(key)
    if custom_id:
        return DEFAULT_MENU_EMOJIS.get(key, "🔹")
    return get_menu_emoji(key)


# =========================================================
# PREMIUM EMOJI SAQLASH
# =========================================================

def save_custom_emoji(key, emoji_id):

    cursor.execute(
        """
        INSERT INTO settings (name, value)
        VALUES (?, ?)
        ON CONFLICT(name)
        DO UPDATE SET value=excluded.value
        """,
        (
            f"custom_emoji_{key}",
            str(emoji_id)
        )
    )

    db.commit()


# =========================================================
# PREMIUM EMOJI O‘CHIRISH
# =========================================================

def delete_custom_emoji(key):

    cursor.execute(
        "DELETE FROM settings WHERE name=?",
        (f"custom_emoji_{key}",)
    )

    db.commit()


# =========================================================
# /emoji
# =========================================================

@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and m.text
    and m.text.strip().lower() == "/emoji"
)
async def emoji_command(message: Message):

    text = (
        "🎨 <b>Emoji sozlamasi</b>\n\n"
        "Qaysi menyuning emojisini o‘zgartirmoqchisiz?\n\n"
    )

    for menu_name in EMOJI_MENUS:

        key = EMOJI_MENUS[menu_name]
        current = get_menu_emoji(key)

        text += (
            f"{current} "
            f"<code>/emoji {menu_name}</code>\n"
        )

    await message.answer(text)


# =========================================================
# /emoji MENU NOMI
# =========================================================

@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and m.text
    and m.text.lower().startswith("/emoji ")
)
async def emoji_menu_select(message: Message):

    menu_name = message.text.split(" ", 1)[1].strip()

    found = None

    for name in EMOJI_MENUS:

        if name.lower() == menu_name.lower():

            found = name
            break

    if not found:

        await message.answer(
            "❌ Bunday menyu topilmadi.\n\n"
            "Avval <code>/emoji</code> deb yozing."
        )

        return

    key = EMOJI_MENUS[found]

    current = get_menu_emoji(key)

    await message.answer(
        f"🎨 <b>{found}</b>\n\n"
        f"Hozirgi emoji: {current}\n\n"
        "Yangi emoji yuboring.\n\n"
        "Oddiy emoji yoki Telegram Premium emoji yuborishingiz mumkin."
    )

    emoji_waiting[ADMIN_ID] = key


# =========================================================
# EMOJI QABUL QILISH
# =========================================================

@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and ADMIN_ID in emoji_waiting
)
async def emoji_change(message: Message):

    key = emoji_waiting.get(ADMIN_ID)

    if not key:
        return

    # =====================================================
    # PREMIUM / CUSTOM EMOJI
    # =====================================================

    if message.entities:

        for entity in message.entities:

            if entity.type == "custom_emoji":

                custom_id = entity.custom_emoji_id

                if not custom_id:
                    continue

                save_custom_emoji(
                    key,
                    custom_id
                )

                emoji_waiting.pop(
                    ADMIN_ID,
                    None
                )

                await message.answer(
                    "✅ <b>Premium emoji saqlandi!</b>\n\n"
                    f"Emoji ID: <code>{custom_id}</code>\n\n"
                    "Endi bot xabarlarida shu premium emoji ishlatiladi."
                )

                return

    # =====================================================
    # ODDIY EMOJI
    # =====================================================

    if message.text:

        new_emoji = message.text.strip()

        if not new_emoji:

            await message.answer(
                "❌ Emoji yuboring."
            )

            return

        # Juda uzun matnni emoji deb qabul qilmaymiz
        if len(new_emoji) > 8:

            await message.answer(
                "❌ Faqat bitta emoji yuboring.\n\n"
                "Masalan: 🔥"
            )

            return

        # Eski premium emoji bo‘lsa o‘chiramiz
        delete_custom_emoji(key)

        # Oddiy emoji saqlaymiz
        set_menu_emoji(
            key,
            new_emoji
        )

        emoji_waiting.pop(
            ADMIN_ID,
            None
        )

        await message.answer(
            "✅ <b>Emoji muvaffaqiyatli o‘zgartirildi!</b>\n\n"
            f"Yangi emoji: {new_emoji}"
        )

        return

    # =====================================================
    # EMOJI TOPILMADI
    # =====================================================

    await message.answer(
        "❌ Emoji topilmadi.\n\n"
        "Oddiy emoji yoki Telegram Premium emoji yuboring."
    )


# =========================================================
# EMOJI BEKOR QILISH
# =========================================================

@dp.message(
    lambda m:
    m.from_user.id == ADMIN_ID
    and m.text
    and m.text.lower() == "/emoji_cancel"
)
async def emoji_cancel(message: Message):

    emoji_waiting.pop(
        ADMIN_ID,
        None
    )

    await message.answer(
        "❌ Emoji o‘zgartirish bekor qilindi."
    )
# =========================================================
# RUN
# =========================================================

async def main():
    print("=" * 50)
    print("BOT ISHGA TUSHYAPTI...")
    print("=" * 50)

    try:
        me = await bot.get_me()

        print(f"BOT: @{me.username}")
        print(f"BOT ID: {me.id}")
        print("POLLING BOSHLANDI...")
        print("=" * 50)

        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )

    except Exception as e:
        print("=" * 50)
        print("BOTDA XATOLIK!")
        print("=" * 50)
        print(type(e).__name__)
        print(e)
        print("=" * 50)

        input("Yopish uchun Enter bosing...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBOT TO'XTATILDI.")
        input("Yopish uchun Enter bosing...")
    except Exception as e:
        print("=" * 50)
        print("KRITIK XATOLIK!")
        print("=" * 50)
        print(type(e).__name__)
        print(e)
        print("=" * 50)
        input("Yopish uchun Enter bosing...")
    
