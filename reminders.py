#!/usr/bin/env python3

import io
import os
import sys
import sqlite3
from datetime import datetime, timedelta

# Database setup
db_path = os.path.join(os.path.expanduser('~'), 'projects', 'reminders', 'reminders.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur2 = conn.cursor()
cur3 = conn.cursor()

# Function to update reminders
def update_reminders():
    try:
        cur.execute("DELETE FROM reminders WHERE julianday(date) - julianday(current_date) < 0")
        cur.execute("DELETE FROM upcoming WHERE julianday(date) - julianday(current_date) < 0")
        cur.execute("INSERT OR IGNORE INTO upcoming (event, date, time, description, id) SELECT event, date, time, description, id FROM reminders WHERE julianday(date) - julianday(current_date) < 3")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating reminders: {e}")

# Function to add a reminder
def add_reminder(event, date, time=None, description=None):
    format_date = os.popen(f"date -d '{date}' +'%Y-%m-%d'").read().strip()
    if time and time.lower() != "none":
        format_time = os.popen(f"date -d '{time}' +'%H:%M'").read().strip()
        cur.execute('INSERT INTO reminders (event, date, time) VALUES (?, ?, ?)', (event, format_date, format_time))
    elif description and description.lower() != "none":
        cur.execute('INSERT INTO reminders (event, date, description) VALUES (?, ?, ?)', (event, format_date, description))
    else:
        cur.execute('INSERT INTO reminders (event, date) VALUES (?, ?)', (event, format_date))
    conn.commit()

# Function to show reminders
def show(upcoming=False):
    try:
        cur.execute("SELECT * FROM reminders")
        cur2.execute("SELECT * FROM days_until")
        rows = cur.fetchall()
        days_rows = cur2.fetchall()

        markdown = "# REMINDERS\n"
        for row, days_row in zip(rows, days_rows):
            event, date, time, description, id = row
            days_until = int(days_row[1])
            date = os.popen(f"date -d '{date}' +'%B %d, %Y'").read().strip()
            time = os.popen(f"date -d '{time}' +'%I:%M %p'").read().strip() if time else ""
            markdown += f"\n{event}\n- When: {date} {'at ' + time if time else ''}\n"
            if description:
                markdown += f"- Description: {description}\n"
            markdown += f"- {days_until} days left\n"

        if upcoming:
            cur3.execute("SELECT * FROM upcoming")
            upcoming_rows = cur3.fetchall()
            markdown += "\n# UPCOMING\n"
            for row in upcoming_rows:
                event, date, time, description, id = row
                date = os.popen(f"date -d '{date}' +'%B %d, %Y'").read().strip()
                time = os.popen(f"date -d '{time}' +'%I:%M %p'").read().strip() if time else ""
                markdown += f"\n# {event}\n- When: {date} {'at ' + time if time else ''}\n"
                if description:
                    markdown += f"- Description: {description}\n"

        return markdown
    except sqlite3.Error as e:
        return f"Error showing reminders: {e}"

# Main script logic
if __name__ == "__main__":
    update_reminders()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "add":
            if len(sys.argv) > 5:
                add_reminder(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            elif len(sys.argv) > 4:
                add_reminder(sys.argv[2], sys.argv[3], sys.argv[4])
            elif len(sys.argv) > 3:
                add_reminder(sys.argv[2], sys.argv[3])
            else:
                print("Please provide event details.")
        elif command in ["delete", "remove"]:
            if len(sys.argv) > 2 and sys.argv[2].lower() == "all":
                cur.execute("DELETE FROM reminders")
                conn.commit()
            elif len(sys.argv) > 2:
                cur.execute("DELETE FROM reminders WHERE event = ?", (sys.argv[2],))
                conn.commit()
        elif command in ["list", "show"]:
            markdown = show(upcoming=(len(sys.argv) > 2 and sys.argv[2].lower() == "upcoming"))
            if markdown and "# UPCOMING" in markdown:
                upcoming_section = markdown.split("# UPCOMING")[1]
                os.system(f"echo '{markdown}' | glow")
                os.system(f"tmux display-popup -E \"echo '{upcoming_section}' | glow\"")
            else:
                os.system(f"echo '{markdown}' | glow")

    cur.close()
    cur2.close()
    cur3.close()
    conn.close()
