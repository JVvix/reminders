#!/usr/bin/env python3

import io
import os
import subprocess
import sys
import sqlite3
from datetime import datetime, timedelta
from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown

# Console setup
console = Console()

# Database setup
db_path = os.path.join(os.path.expanduser('~'), 'projects', 'reminders', 'reminders.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur2 = conn.cursor()
cur3 = conn.cursor()
cur4 = conn.cursor()

# Function to update reminders
def update_reminders():
    try:
        cur.execute("DELETE FROM reminders WHERE julianday(date) - julianday(current_date) < 0")
        cur.execute("DELETE FROM upcoming WHERE julianday(date) - julianday(current_date) < 0")
        cur.execute("INSERT OR IGNORE INTO upcoming (event, date, time, description, id) SELECT event, date, time, description, id FROM reminders WHERE julianday(date) - julianday(current_date) < 2")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating reminders: {e}")

# Function to add a reminder
def add_reminder(event, date, time=None, description=None):
    format_date = subprocess.run(f"date -d '{date}' +'%Y-%m-%d'", shell=True, capture_output=True, text=True).stdout.strip()
    if time and time.lower() != "none":
        format_time = subprocess.run(f"date -d '{time}' +'%H:%M'", shell=True, capture_output=True, text=True).stdout.strip()
        cur.execute('INSERT INTO reminders (event, date, time) VALUES (?, ?, ?)', (event, format_date, format_time))
    elif description and description.lower() != "none":
        cur.execute('INSERT INTO reminders (event, date, description) VALUES (?, ?, ?)', (event, format_date, description))
    else:
        cur.execute('INSERT INTO reminders (event, date) VALUES (?, ?)', (event, format_date))
    conn.commit()

# Function to show reminders
def show():
    try:
        cur.execute("SELECT * FROM reminders")
        cur2.execute("SELECT * FROM days_until")
        rows = cur.fetchall()
        days_rows = cur2.fetchall()

        markdown = "# REMINDERS\n"
        for row, days_row in zip(rows, days_rows):
            event, date, time, description, id = row
            days_until = days_row[1]
            if time and days_until < 1:
                format_time = subprocess.run(f"date -d '{time}' +'%H'", shell=True, capture_output=True, text=True).stdout.strip()
                hours_until = int(datetime.now().strftime("%H")) - int(format_time)
                hours_until =  int(format_time) - int(datetime.now().strftime("%H"))
                if hours_until == 0:
                    str_hours_until = "LESS THAN AN HOUR"
                elif hours_until == 1:
                    str_hours_until = str(hours_until) + " HOUR"
                elif hours_until < 0:
                    cur.execute(f"DELETE FROM reminders WHERE event='{event}' and id={id}")
                else:
                    str_hours_until = str(hours_until) + " HOURS"
                # print(hours_until)

            date = subprocess.run(f"date -d '{date}' +'%B %d, %Y'", shell=True, capture_output=True, text=True).stdout.strip()
            time = subprocess.run(f"date -d '{time}' +'%I:%M %p'", shell=True, capture_output=True, text=True).stdout.strip() if time else ""
            markdown += f"\n## {event}\n- When: {date} {'at ' + time if time else ''}\n"
            if description:
                markdown += f"- Description: {description}\n"
            if days_until > 1:
                markdown += f"- {int(days_until)} days left\n"
            elif days_until > 0:
                markdown += f"- {int(days_until)} day left\n"
            else:
                if time:
                    markdown += f"- HAPPENING TODAY IN {str_hours_until}\n"
                else:
                    markdown += f"- HAPPENING TODAY\n"

        cur3.execute("SELECT COUNT(*) FROM upcoming")
        empty = cur3.fetchall()
        if empty[0][0] != 0:
            cur3.execute("SELECT * FROM upcoming")
            cur4.execute("SELECT * FROM upcoming_days_until")
            upcoming_rows = cur3.fetchall()
            upcoming_days_rows = cur4.fetchall()
            # markdown += "\n# UPCOMING\n"
            for row, upcoming_days_row in zip(upcoming_rows, upcoming_days_rows):
                upcoming_days_until = int(upcoming_days_row[1])
                event, date, time, description, id = row
                date = subprocess.run(f"date -d '{date}' +'%B %d, %Y'", shell=True, capture_output=True, text=True).stdout.strip()
                time = subprocess.run(f"date -d '{time}' +'%I:%M %p'", shell=True, capture_output=True, text=True).stdout.strip() if time else ""
                if upcoming_days_until == 1:
                    today_or_tomorrow = "tomorrow"
                else:
                    today_or_tomorrow = "TODAY"

                subprocess.run(f"notify-send '{event}' 'When: {date} {'at ' + time if time else ''}\nDescription: {description}\nHappening {today_or_tomorrow}!'", shell=True)
                # markdown += f"\n{event}\n- When: {date} {'at ' + time if time else ''}\n"
                # if description:
                #     markdown += f"- Description: {description}\n"
                # if upcoming_days_until > 1:
                #     markdown += f"- {upcoming_days_until} days left\n"
                # elif upcoming_days_until > 0:
                #     markdown += f"- {upcoming_days_until} day left\n"
                # else:
                #     markdown += f"- HAPPENING TODAY\n"
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
                cur.execute("DELETE FROM upcoming")
                conn.commit()
            elif len(sys.argv) > 2:
                cur.execute("DELETE FROM reminders WHERE event = ?", (sys.argv[2],))
                cur.execute("DELETE FROM upcoming WHERE event = ?", (sys.argv[2],))
                conn.commit()
        elif command in ["list", "show"]:
            markdown = show()
            # if markdown and "# UPCOMING" in markdown:
                # upcoming_section = markdown.split("# UPCOMING")[1]
            console.print(Markdown(f"{markdown}"))


            cur.close()
            cur2.close()
            cur3.close()
            conn.close()
            sys.exit()

    cur.close()
    cur2.close()
    cur3.close()
    conn.close()
