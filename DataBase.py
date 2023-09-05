import sqlite3


conn = sqlite3.connect('bugs.db')

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS tasks(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   number BLOB,
   status TEXT,
   priority TEXT,
   version TEXT,
   subject TEXT,
   category TEXT,
   date TEXT);
""")
conn.commit()