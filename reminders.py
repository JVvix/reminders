import os
import sqlite3

db_path = os.path.join(os.path.expanduser('~'), 'projects', 'reminders', 'reminders.db')
conn = sqlite5.connect(db_path)
cur = conn.cursor()
cur2 = conn.cursor()
information = []
upcoming = []

cur.execute('select * from dates')
cur2.execute('select * from days_until')
