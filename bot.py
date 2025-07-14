import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand, BotCommandScopeDefault
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot_config import BOT_TOKEN, OUTLINE_SERVERS
from db import init_db, add_user, add_key, get_keys
from outline_api import create_access_key
from outline_api import get_access_keys
from collections import defaultdict
from datetime import datetime

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатуры - создаем стабильные клавиатуры
main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Что такое Outline VPN?", callback_data="about")],
    [InlineKeyboardButton(text="Выбрать сервер", callback_data="choose_server")],
    [InlineKeyboardButton(text="Мои ключи", callback_data="my_keys")],
])

# Создаем стабильные клавиатуры для серверов
servers_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Германия 🇩🇪", callback_data="server_0")],
    [InlineKeyboardButton(text="Назад", callback_data="back_main")],
])

# Создаем стабильные клавиатуры для генерации ключей
gen_key_kb_germany = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Сгенерировать ключ", callback_data="genkey_0")],
    [InlineKeyboardButton(text="Назад", callback_data="choose_server")],
])

# Кнопка для WebApp
webapp_url = "https://borislav2515.github.io/r14vpn/"
webapp_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Открыть VPN WebApp", web_app=WebAppInfo(url=webapp_url))]
])

# Функция для установки команд меню
async def set_commands():
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="keys", description="🔑 Мои ключи"),
        BotCommand(command="support", description="💬 Поддержка"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

@dp.message(CommandStart())
async def start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username or "")
    await message.answer(
        "Привет! Я помогу тебе получить доступ к VPN через Outline. Выбери действие:",
        reply_markup=main_kb
    )
    await message.answer(
        "Или открой мини-приложение для управления ключами:",
        reply_markup=webapp_kb
    )

# Обработчик команды /keys
@dp.message(lambda message: message.text == "/keys")
async def keys_command(message: types.Message):
    user_id = message.from_user.id
    keys = get_keys(user_id)
    if not keys:
        await message.answer(
            "У тебя пока нет сгенерированных ключей.",
            reply_markup=main_kb
        )
        return
    
    from collections import defaultdict
    keys_by_server = defaultdict(list)
    for server_id, key_id, url, created, *rest in keys:
        expires_at = rest[0] if rest else None
        keys_by_server[server_id].append((key_id, url, created, expires_at))
    text = "<b>🔑 Твои VPN-ключи:</b>\n"
    found = False
    
    # Маппинг серверов для отображения правильных названий
    server_names = {
        0: "Германия 🇩🇪"
    }
    
    for server in OUTLINE_SERVERS:
        server_id = server["id"]
        if server_id not in keys_by_server:
            continue
        server_name = server_names.get(server_id, server['name'])
        try:
            from outline_api import get_access_keys
            real_keys = get_access_keys(server["api_url"])
            real_keys_map = {k["id"]: k for k in real_keys} if real_keys else dict()
            for idx, (key_id, url, created, expires_at) in enumerate(keys_by_server[server_id], 1):
                # Срок действия
                expires_str = ""
                if expires_at:
                    try:
                        dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                        days_left = (dt - datetime.now()).days
                        if days_left < 0:
                            expires_str = f"\n⏰ <b>Ключ истёк</b> <code>{expires_at[:16]}</code>"
                        else:
                            expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code> (<b>{days_left}</b> дн.)"
                    except Exception:
                        expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code>"
                if key_id in real_keys_map:
                    found = True
                    used_bytes = real_keys_map[key_id].get("usedBytes", 0)
                    text += (f"\n<b>{idx}. {server_name}</b>\n"
                             f"🌐 <b>Ссылка:</b> <code>{url}</code>\n"
                             f"{expires_str}\n"
                             f"📊 <b>Трафик:</b> <code>{used_bytes / (1024*1024):.1f} МБ</code>\n"
                             f"{'—'*24}")
                else:
                    found = True
                    text += (f"\n<b>{idx}. {server_name}</b>\n"
                             f"🌐 <b>Ссылка:</b> <code>{url}</code>\n"
                             f"{expires_str}\n"
                             f"❗️ <i>Ключ не найден на сервере</i>\n"
                             f"{'—'*24}")
        except Exception:
            for idx, (key_id, url, created, expires_at) in enumerate(keys_by_server[server_id], 1):
                found = True
                expires_str = ""
                if expires_at:
                    try:
                        dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                        days_left = (dt - datetime.now()).days
                        if days_left < 0:
                            expires_str = f"\n⏰ <b>Ключ истёк</b> <code>{expires_at[:16]}</code>"
                        else:
                            expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code> (<b>{days_left}</b> дн.)"
                    except Exception:
                        expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code>"
                text += (f"\n<b>{idx}. {server_name}</b>\n"
                         f"🌐 <b>Ссылка:</b> <code>{url}</code>\n"
                         f"{expires_str}\n"
                         f"⚠️ <i>Сервер временно недоступен</i>\n"
                         f"{'—'*24}")
    if not found:
        text = "У тебя нет актуальных ключей на сервере. Возможно, они были удалены."
    await message.answer(text, reply_markup=main_kb, parse_mode="HTML")

# Обработчик команды /support
@dp.message(lambda message: message.text == "/support")
async def support_command(message: types.Message):
    support_text = (
        "💬 <b>Поддержка</b>\n\n"
        "Если у тебя возникли вопросы или проблемы:\n\n"
        "📧 <b>Email:</b> support@example.com\n"
        "📱 <b>Telegram:</b> @support_username\n"
        "🌐 <b>Сайт:</b> https://example.com\n\n"
        "⏰ <b>Время работы:</b> 24/7\n\n"
        "Также можешь написать нам прямо здесь, и мы ответим в ближайшее время."
    )
    await message.answer(support_text, parse_mode="HTML", reply_markup=main_kb)

@dp.callback_query(lambda c: c.data == "about")
async def about_outline(callback: types.CallbackQuery):
    text = (
        "Outline VPN — это простой и безопасный способ получить доступ к интернету без ограничений. "
        "Ты сможешь подключиться к серверам в разных странах и пользоваться интернетом свободно."
    )
    await callback.message.edit_text(text, reply_markup=main_kb)

@dp.callback_query(lambda c: c.data == "choose_server")
async def choose_server(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выбери сервер для генерации VPN-ключа:",
        reply_markup=servers_kb
    )

@dp.callback_query(lambda c: c.data.startswith("server_"))
async def server_menu(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    server = OUTLINE_SERVERS[idx]
    
    # Информация о сервере
    server_info = {
        0: {
            "name": "Германия",
            "flag": "🇩🇪",
            "traffic": "∞",
            "price": "349₽/месяц",
            "type": "🌐 Outline",
            "rating": "NA",
            "ping": "n/a ms",
            "cost": "349 руб/мес.",
            "trial": "1 день"
        }
    }
    
    info = server_info.get(idx, {
        "name": server['name'],
        "flag": "🌐",
        "traffic": "∞",
        "price": "349₽/месяц",
        "type": "🌐 Outline",
        "rating": "NA",
        "ping": "n/a ms",
        "cost": "349 руб/мес.",
        "trial": "1 день."
    })
    
    text = (
        f"Информация о сервере {info['name']} {info['flag']}, {info['traffic']}, {info['price']}:\n\n"
        f"Тип: {info['type']}\n"
        f"Рейтинг: {info['rating']}\n"
        f"Ping: {info['ping']}\n"
        f"Стоимость: {info['cost']}\n"
        f"Тестовый период: {info['trial']}\n\n"
        f"Получая ключ вы подтверждаете, что ознакомились и принимаете правила опубликованные на https://outlinekeys.net/rules/OutlineKeysRobot"
    )
    
    # Создаем клавиатуру с двумя кнопками
    kb = InlineKeyboardBuilder()
    kb.button(text="Получить ключ", callback_data=f"genkey_{idx}")
    kb.button(text="Отменить", callback_data="choose_server")
    reply_markup = kb.as_markup()
    
    await callback.message.edit_text(text, reply_markup=reply_markup)

@dp.callback_query(lambda c: c.data.startswith("genkey_"))
async def generate_key(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    server = OUTLINE_SERVERS[idx]
    user_id = callback.from_user.id
    username = callback.from_user.username or f"user_{user_id}"
    res = create_access_key(server["api_url"], name=username)
    
    # Создаем клавиатуру с кнопкой "Назад"
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="choose_server")
    reply_markup = kb.as_markup()
    
    if res and "id" in res and "accessUrl" in res:
        add_key(user_id, server["id"], res["id"], res["accessUrl"])
        await callback.message.edit_text(
            f"✅ Ключ сгенерирован!\n\nСсылка для подключения:\n{res['accessUrl']}",
            reply_markup=reply_markup
        )
    else:
        await callback.message.edit_text(
            "Ошибка при генерации ключа. Попробуйте позже.",
            reply_markup=reply_markup
        )

@dp.callback_query(lambda c: c.data == "my_keys")
async def my_keys(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    keys = get_keys(user_id)
    if not keys:
        await callback.message.edit_text(
            "У тебя пока нет сгенерированных ключей.",
            reply_markup=main_kb
        )
        return
    from collections import defaultdict
    keys_by_server = defaultdict(list)
    for server_id, key_id, url, created, *rest in keys:
        expires_at = rest[0] if rest else None
        keys_by_server[server_id].append((key_id, url, created, expires_at))
    text = "<b>🔑 Твои VPN-ключи:</b>\n"
    found = False
    
    # Маппинг серверов для отображения правильных названий
    server_names = {
        0: "Германия 🇩🇪"
    }
    
    for server in OUTLINE_SERVERS:
        server_id = server["id"]
        if server_id not in keys_by_server:
            continue
        server_name = server_names.get(server_id, server['name'])
        try:
            from outline_api import get_access_keys
            real_keys = get_access_keys(server["api_url"])
            real_keys_map = {k["id"]: k for k in real_keys} if real_keys else dict()
            for idx, (key_id, url, created, expires_at) in enumerate(keys_by_server[server_id], 1):
                # Срок действия
                expires_str = ""
                if expires_at:
                    try:
                        dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                        days_left = (dt - datetime.now()).days
                        if days_left < 0:
                            expires_str = f"\n⏰ <b>Ключ истёк</b> <code>{expires_at[:16]}</code>"
                        else:
                            expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code> (<b>{days_left}</b> дн.)"
                    except Exception:
                        expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code>"
                if key_id in real_keys_map:
                    found = True
                    used_bytes = real_keys_map[key_id].get("usedBytes", 0)
                    text += (f"\n<b>{idx}. {server_name}</b>\n"
                             f"🌐 <b>Ссылка:</b> <code>{url}</code>\n"
                             f"{expires_str}\n"
                             f"📊 <b>Трафик:</b> <code>{used_bytes / (1024*1024):.1f} МБ</code>\n"
                             f"{'—'*24}")
                else:
                    found = True
                    text += (f"\n<b>{idx}. {server_name}</b>\n"
                             f"🌐 <b>Ссылка:</b> <code>{url}</code>\n"
                             f"{expires_str}\n"
                             f"❗️ <i>Ключ не найден на сервере</i>\n"
                             f"{'—'*24}")
        except Exception:
            for idx, (key_id, url, created, expires_at) in enumerate(keys_by_server[server_id], 1):
                found = True
                expires_str = ""
                if expires_at:
                    try:
                        dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                        days_left = (dt - datetime.now()).days
                        if days_left < 0:
                            expires_str = f"\n⏰ <b>Ключ истёк</b> <code>{expires_at[:16]}</code>"
                        else:
                            expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code> (<b>{days_left}</b> дн.)"
                    except Exception:
                        expires_str = f"\n⏰ <b>Действует до:</b> <code>{expires_at[:16]}</code>"
                text += (f"\n<b>{idx}. {server_name}</b>\n"
                         f"🌐 <b>Ссылка:</b> <code>{url}</code>\n"
                         f"{expires_str}\n"
                         f"⚠️ <i>Сервер временно недоступен</i>\n"
                         f"{'—'*24}")
    if not found:
        text = "У тебя нет актуальных ключей на сервере. Возможно, они были удалены."
    await callback.message.edit_text(text, reply_markup=main_kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_kb
    )

async def main():
    init_db()
    # Устанавливаем команды меню
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 