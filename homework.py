import os
import time

import requests
import telegram
import logging

from dotenv import load_dotenv

load_dotenv()

# noinspection PyArgumentList
logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    encoding='UTF-8',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    """Compare json string response with actual status,
    prepared messages under bot output.
    """

    logging.debug(msg='Запуск парсера.')
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'reviewing':
        verdict = 'Работа взята в ревью.'
    else:
        verdict = ('Ревьюеру всё понравилось,'
                   ' можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """Responding to a Well-formed API Request Praktikum."""

    try:
        homework_statuses = requests.get(
            URL_API,
            params={'from_date': current_timestamp},
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
        )
        return homework_statuses.json()
    except requests.RequestException as error:
        logging.error(
            f'Не правильно сформированный запрос API. Ошибка: {error}'
        )
        return {}


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logging.debug(msg='| Запуск бота |')
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]), bot
                )
                logging.info('| Сообщение отправлено. |')
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
