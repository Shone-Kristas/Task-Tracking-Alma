from src.TaskTracking.models.database_utils import connect_db, cursor_db

conn = connect_db()
cur = cursor_db(conn)

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
conn.close()