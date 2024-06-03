import telebot

from bs4 import BeautifulSoup

from src.TaskTracking.models.database_utils import connect_db, cursor_db, get_new_task, get_last_task
from src.TaskTracking.models.web_utils import write_file, requestions, open_file, serching

import schedule
import time

import os
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
chat = os.getenv('CHAT_ID')

def send_message():
    write_file(requestions())

    soup = BeautifulSoup(open_file(), 'lxml')

    with connect_db() as conn:
        cur = cursor_db(conn)
        try:
            last_task, last_task_date = get_last_task(cur)

            new_task = get_new_task(cur)

            task_list = soup.find('div', id='recent_mod').find_all('tr', class_='my-buglist-bug')
            serching(new_task, task_list, last_task, last_task_date, cur, conn, chat, bot)
        finally:
            cur.close()


if __name__ == "__main__":
    try:
        schedule.every(1).seconds.do(send_message)
        while True:
            schedule.run_pending()
            time.sleep(7200)   # 2 часа (7200)
    except Exception as e:
        print(e)