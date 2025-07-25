import asyncio
import logging
import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.apihelper import ApiException

from constants import (
    MENU_STRUCTURE,
    CATEGORY_MESSAGE,
    CHECK_MESSAGE,
    WAIT_MESSAGE,
    WELCOME_MESSAGE
)
from keyboard import create_menu_keyboard
from utils import get_file

load_dotenv()
bot_token = os.getenv('TOKEN')
bot = AsyncTeleBot(bot_token)
user_data = {}  # Cловарь для отслеживания передвижения пользователя

# Настройки логирования:
bot_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(bot_dir, 'main.log')
logging.basicConfig(
    format=(
        '%(asctime)s - '
        '%(levelname)s - '
        '%(message)s - '
        '%(funcName)s - '
        '%(lineno)d'
    ),
    level=logging.ERROR,
    filename=log_path,
    filemode='w',
    encoding='utf-8',
)


@bot.message_handler(commands=['start'])
async def send_welcome_message(message):
    """Функция для начала общения."""
    main_menu = 'lvl_0'
    await bot.send_message(
        chat_id=message.chat.id,
        text=WELCOME_MESSAGE,
        reply_markup=create_menu_keyboard(main_menu)
    )


@bot.callback_query_handler(func=lambda call: True)
async def handle_inline_buttons(call):
    """
    Обработчик нажатия клавиш.

    Переменные:
    - chat_id - глобальный словарь для отслеживания на каком уровне меню
      находится пользователь.
    - previous_choice - предыдущий уровень мень.

    """
    global user_data
    main_menu = 'lvl_0'

    user_choice = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Задаем начальную позицию пользователя:
    if chat_id not in user_data:
        user_data[chat_id] = [main_menu]
    # Записываем шаги пользователя. Запись происходит в глубину меню.
    if user_choice != 'back':
        user_data[chat_id].append(user_choice)
    previous_choice = user_data[chat_id][-2]

    # Пользователь нажал клавишу: "в меню".
    if user_choice == main_menu:
        await bot.send_message(
            chat_id=chat_id,
            text=WELCOME_MESSAGE,
            reply_markup=create_menu_keyboard(main_menu)
        )
        del user_data[chat_id]  # Очищаем историю передвижения пользователя.

    # Пользователь нажал клавишу: "назад".
    elif user_choice == 'back':
        user_data[chat_id].pop()  # Убираем верхний уровень меню.
        text = CATEGORY_MESSAGE
        if previous_choice == main_menu:
            text = WELCOME_MESSAGE
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=create_menu_keyboard(previous_choice)
        )

    # Пользователь нажал клавишу, у которой нет следующего уровня.
    elif user_choice not in list(MENU_STRUCTURE.keys()):
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=WAIT_MESSAGE
        )

    # Пользователь нажал клавишу, по которой происходит скачивание файла.
    elif user_choice.endswith('file'):
        # Удаляем клавиатуру у старого сообщения.
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None
        )
        # Отправляем временное сообщение.
        temp_message = await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=WAIT_MESSAGE
        )

        content, document, text = get_file(user_choice)
        # Отправляем описание.
        if content:
            await bot.send_message(
                chat_id, content, parse_mode='HTML',
                reply_markup=create_menu_keyboard(user_choice))
        # Отправляем документ в виде файла.
        elif document:
            await bot.send_document(
                chat_id, document, caption=text,
                reply_markup=create_menu_keyboard(user_choice))

        # Удаляем временное сообщение
        await bot.delete_message(
            chat_id=temp_message.chat.id,
            message_id=temp_message.message_id
        )

    # Пользователь нажал клавишу меню второго уровня.
    elif len(user_choice) == 7:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=CATEGORY_MESSAGE,
            reply_markup=create_menu_keyboard(user_choice)
        )

    # Пользователь нажал клавишу проверки вложенности.
    elif user_choice.startswith('lvl_0_5'):
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=CHECK_MESSAGE,
            reply_markup=create_menu_keyboard(user_choice)
        )


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(bot.polling(non_stop=True))
        except ApiException as api_error:
            logging.error(f'Ошибка Telegram API: {api_error}')
        except Exception as e:
            logging.error(f'Необработанная ошибка: {e}')