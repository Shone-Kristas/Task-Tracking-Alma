import sqlite3
import os

import datetime

current_dir = os.path.dirname(__file__)

db_relative_path = 'bugs.db'

db_path = os.path.join(current_dir, db_relative_path)

def connect_db():
    return sqlite3.connect(db_path)


def commit_db(conn):
     return conn.commit()


def cursor_db(conn):
    return conn.cursor()


def get_last_task(cur):
    cur.execute("SELECT number, status, priority, version, subject, category, date FROM tasks;")

    last_task = cur.fetchone()
    date = last_task[-1]
    last_task_date = datetime.datetime.strptime(date, ' - %Y-%m-%d %H:%M')

    return last_task, last_task_date


def get_new_task(cur):
    cur.execute("SELECT number FROM tasks WHERE id=2")
    new_task = cur.fetchone()
    return new_task


def check_and_update_max_task(*args):
    cur, conn, new_max_task, new_task_db, date = args
    if new_max_task > new_task_db:
        tuple_task = (new_max_task, date)
        cur.execute("UPDATE tasks SET (number, date) = (?, ?) where id=2", tuple_task)
        commit_db(conn)


def update_task(*args):
    cur, conn, task_tr = args
    cur.execute(
        "UPDATE tasks SET (number, status, priority, version, subject, category, date) = (?, ?, ?, ?, ?, ?, ?) where id=1",
        task_tr)
    commit_db(conn)