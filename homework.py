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

    logging.debug(msg='| Запуск парсера. |')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None or homework_status is None:
        logging.error(f'Ошибка парсера {homework}')
        return 'Ошибка парсера'

    status_list = {
        'reviewing': 'Работа взята в ревью.',
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': ('Ревьюеру всё понравилось,'
                     ' можно приступать к следующему уроку.')
    }

    if homework_status in status_list:
        verdict = status_list[homework.get('status')]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        logging.error(f'Ошибка "статуса" работы "{homework_name}"')
        return 'Ошибка статуса'


def get_homework_statuses(current_timestamp):
    """Responding to a Well-formed API Request Praktikum."""

    current_timestamp = current_timestamp or int(time.time())
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

    try:
        homework_statuses = requests.get(
            URL_API,
            params=params,
            headers=headers
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
                logging.info('/ Сообщение отправлено. /')
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
