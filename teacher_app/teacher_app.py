import os
import sqlite3
import logging
from flask import Flask, render_template, redirect, url_for, Response, jsonify

# --------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__, template_folder='templates', static_folder='static')

# ✅ Correct absolute path to your shared database file
DB_PATH = r"C:\Users\darsh\Desktop\late-comers-management-system\latecomers.db"
print("✅ Using Database:", DB_PATH)

# Faculty-Subject mapping (faculty names + subjects)
FACULTY_SUBJECTS = {
    "prof. smith": {"faculty_name": "Dr. Smith", "subject": "Data Structures"},
    "prof. priya": {"faculty_name": "Prof. Priya", "subject": "Database Management"},
    "prof. ramesh": {"faculty_name": "Mr. Ramesh", "subject": "Computer Networks"},
    "prof. kavya": {"faculty_name": "Ms. Kavya", "subject": "Operating Systems"}
}


# --------------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------------
def init_db():
    try:
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
        logging.info("✅ Database ready at: %s", DB_PATH)
    except Exception:
        logging.exception("❌ Database initialization failed")


# --------------------------------------------------------
# ROUTES
# --------------------------------------------------------

@app.route('/health')
def health():
    """Health check route to confirm database path"""
    exists = os.path.exists(DB_PATH)
    return jsonify({"status": "ok" if exists else "missing", "db_path": DB_PATH})


@app.route('/')
def home():
    """Home page to select faculty"""
    return render_template('home.html', faculty_subjects={k: v['subject'] for k, v in FACULTY_SUBJECTS.items()})


@app.route('/<faculty>')
def teacher_dashboard(faculty):
    """Display latecomer entries for a given faculty"""
    info = FACULTY_SUBJECTS.get(faculty.lower())
    print(faculty)
    if not info:
        return "❌ Invalid faculty access!", 403

    faculty_name = info['faculty_name']
    subject = info['subject']

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT id, usn, name, class_name, faculty_name, subject, reason, minutes_late, timestamp, status
            FROM late_entries
            WHERE faculty_name=? AND subject=?
            ORDER BY timestamp DESC
        ''', (faculty_name, subject))
        entries = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        logging.exception("❌ Database read error for teacher_dashboard")
        return Response(f"Database error: {e}", status=500)

    return render_template('teacher.html', faculty=faculty_name, subject=subject, entries=entries)


@app.route('/update/<faculty>/<int:id>')
def update_status(faculty, id):
    """Update student's status to 'Noted' (only if not Absent)"""
    info = FACULTY_SUBJECTS.get(faculty.lower())
    print(faculty)
    if not info:
        return "❌ Invalid faculty access!", 403

    faculty_name = info['faculty_name']
    subject = info['subject']

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            UPDATE late_entries
            SET status="Noted"
            WHERE id=? AND faculty_name=? AND subject=? AND status!="Absent"
        ''', (id, faculty_name, subject))
        conn.commit()
        conn.close()
        logging.info("✅ Marked ID %d as Noted for %s", id, faculty_name)
    except sqlite3.Error as e:
        logging.exception("❌ Database update error")
        return Response(f"Database error: {e}", status=500)

    return redirect(url_for('teacher_dashboard', faculty=faculty))


# --------------------------------------------------------
# START THE APP
# --------------------------------------------------------
if __name__ == '__main__':
    try:
        init_db()
        logging.info("🚀 Teacher app running at: http://127.0.0.1:5001")
        app.run(host='127.0.0.1', port=5001, debug=True)
    except Exception:
        logging.exception("❌ Failed to start teacher app")
