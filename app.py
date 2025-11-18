import os
import sqlite3
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)

# Faculty-Subject mapping
FACULTY_SUBJECTS = {
    "smith": "Data Structures",
    "priya": "Database Management",
    "ramesh": "Computer Networks",
    "kavya": "Operating Systems"
}

# Resolve project root and DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'latecomers.db')

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

# Student Routes
@app.route('/')
@app.route('/student')
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
        usn = request.form.get('usn','').strip()
        name = request.form.get('name','').strip()
        class_name = request.form.get('class','').strip()
        faculty = request.form.get('faculty','').strip()
        subject = request.form.get('subject','').strip()
        reason = request.form.get('reason','').strip()
        minutes = int(request.form.get('minutes','0') or 0)
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

# Teacher Routes
@app.route('/teacher')
def teacher_home():
    return render_template('home.html', faculty_subjects=FACULTY_SUBJECTS)

@app.route('/teacher/<faculty>')
def teacher_dashboard(faculty):
    subject = FACULTY_SUBJECTS.get(faculty.lower())
    if not subject:
        return "Invalid faculty access!", 403
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, usn, name, class_name, faculty_name, subject, reason, minutes_late, timestamp, status FROM late_entries WHERE subject=? ORDER BY timestamp DESC', (subject,))
        entries = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        logging.exception("DB read error for teacher_dashboard")
        return Response(f"Database error: {e}", status=500)
    return render_template('teacher.html', faculty=faculty.capitalize(), subject=subject, entries=entries)

@app.route('/teacher/update/<faculty>/<int:id>')
def update_status(faculty, id):
    subject = FACULTY_SUBJECTS.get(faculty.lower())
    if not subject:
        return "Invalid faculty access!", 403
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE late_entries SET status="Noted" WHERE id=? AND subject=? AND status!="Absent"', (id, subject))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logging.exception("DB write error for update_status")
        return Response(f"Database error: {e}", status=500)
    return redirect(url_for('teacher_dashboard', faculty=faculty))

@app.route('/health')
def health():
    return jsonify({"status": "ok", "db_path": DB_PATH})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
