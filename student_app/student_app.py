# filepath: [student_app.py](http://_vscodecontentref_/0)
# ...existing code...
import os
import sqlite3
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Resolve project root and DB path robustly (works even with nested folders)
# ✅ Correct absolute path to your shared database file
DB_PATH = r"C:\Users\darsh\Desktop\late-comers-management-system\latecomers.db"
print("✅ Using Database:", DB_PATH)

def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS late_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usn TEXT,
                name TEXT,
                class_name TEXT,
                faculty_name TEXT,
                subject TEXT,
                reason TEXT,
                minutes_late INTEGER,
                timestamp TEXT,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logging.info("Initialized DB at: %s", DB_PATH)
    except Exception:
        logging.exception("Failed to initialize DB")

@app.route('/')
def student_form():
    faculties = [
        {"name": "Dr. Smith", "subject": "Data Structures"},
        {"name": "Prof. Priya", "subject": "Database Management"},
        {"name": "Mr. Ramesh", "subject": "Computer Networks"},
        {"name": "Ms. Kavya", "subject": "Operating Systems"}
    ]
    return render_template('student.html', faculties=faculties)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        usn = request.form['usn']
        name = request.form['name']
        class_name = request.form['class']
        faculty = request.form['faculty']
        subject = request.form['subject']
        reason = request.form['reason']
        minutes = int(request.form['minutes'])
        status = "Absent" if minutes > 35 else "Pending"

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO late_entries (usn, name, class_name, faculty_name, subject, reason, minutes_late, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (usn, name, class_name, faculty, subject, reason, minutes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status))
        conn.commit()
        conn.close()
        return redirect(url_for('student_form'))
    except sqlite3.OperationalError as oe:
        logging.exception("SQLite operational error on submit")
        return Response("Database operational error. See server log.", status=500)
    except Exception:
        logging.exception("Unhandled error on submit")
        return Response("Server error. See server log.", status=500)

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
# ...existing code...  