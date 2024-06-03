import time

import requests

from aiogram.utils.markdown import hlink

import datetime

from src.TaskTracking.models.database_utils import update_task, check_and_update_max_task


def requestions():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get("https://bugs.almalinux.org/set_project.php?project_id=0", headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        time.sleep(300)
        return requestions()


def write_file(response):
    with open("bugs_almalinux_site.html", "w", encoding="utf-8") as file:
        file.write(response.text)


def open_file():
    with open("bugs_almalinux_site.html", encoding="utf-8") as file:
        src = file.read()
        return src


def parameter_extraction(task_list):
    number = task_list.find('a').text
    link_tr = task_list.find('a').get('href')
    link = f"https://bugs.almalinux.org{link_tr}"
    element_i_list = task_list.find_all('i')
    status = element_i_list[0]["title"]
    priority = element_i_list[1]["title"]
    description_list = task_list.find_all('span')
    version = description_list[0].text
    subject = description_list[1].text
    category = description_list[2].text
    date = description_list[3].text

    date_time_tr = datetime.datetime.strptime(date, ' - %Y-%m-%d %H:%M')
    task_link = hlink(number, link)

    task_tr = (number, status, priority, version, subject, category, date)

    result = f'Link:  {task_link} \nStatus:  {status} \nPriority:  {priority} \nVersionOS:  {version} \nDescription:  {subject} \nKategory:  {category} \nDate:  {date}'

    return task_tr, result, int(number), date_time_tr, date


def serching(*args):
    new_task, task_list, last_task, last_task_date, cur, conn, chat, bot = args
    new_task_db = int(new_task[0])
    new_max_task = 0
    for index, tr in enumerate(task_list):
        parameter_extraction(tr)
        task_tr, result, number_tr, date_time_tr, date_tr = parameter_extraction(tr)

        if index == 0:
            if task_tr == last_task or date_time_tr <= last_task_date:
                break
            else:
                update_task(cur, conn, task_tr)
        elif index == 9:
            check_and_update_max_task(cur, conn, new_max_task, new_task_db, date_tr)

        if task_tr != last_task and number_tr > new_task_db and date_time_tr > last_task_date:
            if new_max_task < number_tr:
                new_max_task = number_tr
                check_and_update_max_task(cur, conn, new_max_task, new_task_db, date_tr)
            bot.send_message(chat, 'NEW task:')
            bot.send_message(chat, result, parse_mode='HTML')
        elif task_tr != last_task and number_tr <= new_task_db and date_time_tr > last_task_date:
            bot.send_message(chat, 'OLD task:')
            bot.send_message(chat, result, parse_mode='HTML')
        elif task_tr == last_task or date_time_tr <= last_task_date:
            check_and_update_max_task(cur, conn, new_max_task, new_task_db, date_tr)
            break