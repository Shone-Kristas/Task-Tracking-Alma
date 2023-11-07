import telebot
import requests
from bs4 import BeautifulSoup
import datetime
import sqlite3
import schedule
import time
from aiogram.utils.markdown import hlink
import os
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

def send_message():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    req = requests.get("https://bugs.almalinux.org/set_project.php?project_id=0", headers)
    with open("bugs_almalinux_site.html", "w", encoding="utf-8") as file:
        file.write(req.text)

    with open("bugs_almalinux_site.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    conn = sqlite3.connect('bugs.db')
    cursor = conn.cursor()

    cursor.execute("SELECT number, status, priority, version, subject, category, date FROM tasks;")
    last_task_save = cursor.fetchone()
    data_last = last_task_save[-1]
    date_time_lastsave = datetime.datetime.strptime(data_last, ' - %Y-%m-%d %H:%M')

    cursor.execute("SELECT number FROM tasks WHERE id=2")
    max_numb_save = cursor.fetchone()

    all_task_list = soup.find('div', id='recent_mod').find_all('tr', class_='my-buglist-bug')

    def serching(all_task_list):
        total = 0
        max_numb_db = int(max_numb_save[0])
        new_max_task = 0
        for tr in all_task_list:
            number = tr.find('a').text
            link_tr = tr.find('a').get('href')
            link = f"https://bugs.almalinux.org{link_tr}"
            element_i_list = tr.find_all('i')
            status = element_i_list[0]["title"]
            priority = element_i_list[1]["title"]
            description_list = tr.find_all('span')
            version = description_list[0].text
            subject = description_list[1].text
            category = description_list[2].text
            date = description_list[3].text

            date_time_tr = datetime.datetime.strptime(date, ' - %Y-%m-%d %H:%M')
            task_link = hlink(number, link)

            task_tr = (number, status, priority, version, subject, category, date)
            result = f'Link:  {task_link} \nStatus:  {status} \nPriority:  {priority} \nVersionOS:  {version} \nDescription:  {subject} \nKategory:  {category} \nDate:  {date}'
            total += 1

            if total == 1:
                cursor.execute(
                    "UPDATE tasks SET (number, status, priority, version, subject, category, date) = (?, ?, ?, ?, ?, ?, ?) where id=1",
                    task_tr)
                conn.commit()
                if task_tr == last_task_save or date_time_tr <= date_time_lastsave:
                    break
            elif total == 10:
                if new_max_task > max_numb_db:
                    tuple_new_max_task = (new_max_task, date)
                    cursor.execute("UPDATE tasks SET (number, date) = (?, ?) where id=2", tuple_new_max_task)
                    conn.commit()
            if task_tr != last_task_save and int(number) > max_numb_db and date_time_tr > date_time_lastsave:
                if int(number) > new_max_task:
                    new_max_task = int(number)
                bot.send_message(396956685, 'NEW task:')
                bot.send_message(396956685, result, parse_mode='HTML')
            elif task_tr != last_task_save and int(number) <= max_numb_db and date_time_tr > date_time_lastsave:
                bot.send_message(396956685, 'OLD task:')
                bot.send_message(396956685, result, parse_mode='HTML')
            elif task_tr == last_task_save or date_time_tr <= date_time_lastsave:
                if new_max_task > max_numb_db:
                    tuple_new_max_task = (new_max_task, date)
                    cursor.execute("UPDATE tasks SET (number, date) = (?, ?) where id=2", tuple_new_max_task)
                    conn.commit()
                break

    serching(all_task_list)
    conn.close()

schedule.every(1).seconds.do(send_message)


while True:
    schedule.run_pending()
    time.sleep(300)


if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)