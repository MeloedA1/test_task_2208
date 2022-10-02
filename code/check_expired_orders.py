import schedule
import telegram
import time

from db_queries import PGWriter
from config import cfg

TELEGRAM_BOT_TOKEN = cfg.tg_token
CHAT_ID = cfg.tg_chat_id


def expiration_notify(expired_orders):

    '''
        Посылаем уведомление об истечении срока доставки
    '''

    expired_orders_mesages = [f"‼️*Delivery time expired!!!*\n" \
                              f"*Order number:* {row[0]}\n" \
                              f"*Delivery time:* {row[1]}" for row in expired_orders]

    message = f"*{len(expired_orders_mesages)} orders were expired*\n\n" + "\n\n".join(expired_orders_mesages)
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(CHAT_ID, message, parse_mode='Markdown')


def get_expired_orders():

    expired_orders = PGWriter().get_expired_orders()
    expiration_notify(expired_orders)


if __name__ == '__main__':
    
   
    # Создаем шедулер, по которому скрипт будет запускаться раз в 2 минуты (для тестирования,
    #  затем можно поменять на более долгий период)
    schedule.every(2).minutes.do(get_expired_orders)
    while True:
       schedule.run_pending()
       time.sleep(1)
