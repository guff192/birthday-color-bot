import logging
import os
from dotenv import load_dotenv


from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook

from PIL import Image


load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')

# webhook settings
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = os.getenv('WEBAPP_HOST')
WEBAPP_PORT = os.getenv('WEBAPP_PORT')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Regular request
    text = 'Китикэт, напиши дату своего рождения пж) "DD.MM.YY"'
    await bot.send_message(message.chat.id, text)

    # or reply INTO webhook
    # return SendMessage(message.chat.id, message.text)


@dp.message_handler()
async def generate_color(message: types.Message):
    splitted_message = message.text.split('.')
    message_date = list(filter(lambda s: s.isdigit(), splitted_message))
    if len(splitted_message) != 3 or len(splitted_message) != len(message_date):
        await bot.send_message(message.chat.id, 'Пашол нахуй ♡ (неправильный формат даты). Думай ещё.')
        return

    day, month, year = list(map(lambda s: int(s), message_date))

    image = Image.new("RGB", (500, 500), (day, month, year))
    image_path = f'app/images/{day}:{month}:{year}.png'
    image.save(f'app/images/{day}:{month}:{year}.png')

    with open(image_path, 'rb') as image_file:
        await bot.send_photo(message.chat.id, image_file)



async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info('bot started')
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

