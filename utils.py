import logging
import os

from telebot.types import InputFile

from constants import MENU_STRUCTURE


def get_file(user_choice):
    """Функция для получения файла."""

    file_name = MENU_STRUCTURE[user_choice]  # Имя файла - это название клавиш
    file_path = os.path.join(os.getcwd(), 'download_files', file_name)

    content = None  # Описание из раздела рекламация
    document = None  # Файл
    try:
        if file_name.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            document = InputFile(file_path)
    except FileNotFoundError:
        logging.error(f'Файл не найден: {file_name}')
    except Exception as ex:
        logging.error(f'Возникло непредвиденное исключение: {ex}')

    # Готовим текст сообщения для пользователя при отправлке файла.
    level = user_choice[:-7]
    label_list = MENU_STRUCTURE[level]
    # По цифре уровня: Х_file получаем название клавиши:
    label = label_list[int(user_choice[-6])]
    doc_name = label[:-5]  # Из названия клавиши убираем: _file
    text = f'Вот документ для изучения {doc_name}'

    return content, document, text
