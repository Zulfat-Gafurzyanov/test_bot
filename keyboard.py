import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from constants import (
    MENU_STRUCTURE,
    BACK_BUTTON,
    BACK_TO_MENU_BUTTON
)


def create_menu_keyboard(level):
    """
    Функция создает клавиатуру на основе текущего уровня меню.

    level - уровень меню:
        'lvl_0' - главное меню (уровень 0)
        'lvl_0_0' - уровень 1
        'lvl_0_5_0_0' - уровень 3
    label - название клавиш
    """
    try:
        keyboard = InlineKeyboardMarkup(row_width=1)

        # Если уровень представляет собой скачивание файла,
        # то такому уровню создаем только клавишу: "В меню".
        if 'file' in level:
            btn = InlineKeyboardButton(
                BACK_TO_MENU_BUTTON, callback_data='lvl_0')
            keyboard.add(btn)
            return keyboard

        # Основной цикл создания клавиатур
        label_list = MENU_STRUCTURE[level]
        for index in range(len(label_list)):
            label = label_list[index]
            data = level + f'_{index}'  # форма клавиши (пример): lvl_0_1_2
            if 'file' in label:
                data = f'{level}_{index}_file'
                label = label[:-5]
            btn = InlineKeyboardButton(label, callback_data=data)
            keyboard.add(btn)

        # Если мы находимся на уровне 1 и выше, то добавляем клавиши:
        if len(level) > 5:
            btn_1 = InlineKeyboardButton(
                BACK_BUTTON, callback_data='back')
            btn_2 = InlineKeyboardButton(
                BACK_TO_MENU_BUTTON, callback_data='lvl_0')
            keyboard.add(btn_1, btn_2)
        return keyboard

    except KeyError as e:
        logging.error(f'Произошла ошибка KeyError: {e}')

    except Exception as ex:
        logging.error(f'Возникло непредвиденное исключение: {ex}')
