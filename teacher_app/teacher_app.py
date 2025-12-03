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


# --------------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------------
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Create late_entries table
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
        
        # Create faculties table
        c.execute('''
            CREATE TABLE IF NOT EXISTS faculties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faculty_key TEXT UNIQUE NOT NULL,
                faculty_name TEXT NOT NULL,
                subject TEXT NOT NULL
            )
        ''')
        
        # Insert default faculty data if table is empty
        c.execute('SELECT COUNT(*) FROM faculties')
        if c.fetchone()[0] == 0:
            default_faculties = [
                ("dr. smith", "Dr. Smith", "Data Structures"),
                ("prof. priya", "Prof. Priya", "Database Management"),
                ("mr. ramesh", "Mr. Ramesh", "Computer Networks"),
                ("ms. kavya", "Ms. Kavya", "Operating Systems")
            ]
            c.executemany('INSERT INTO faculties (faculty_key, faculty_name, subject) VALUES (?, ?, ?)', 
                         default_faculties)
            logging.info("✅ Inserted default faculty data")
        
        conn.commit()
        conn.close()
        logging.info("✅ Database ready at: %s", DB_PATH)
    except Exception:
        logging.exception("❌ Database initialization failed")


def get_all_faculties():
    """Fetch all faculties from the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT faculty_key, faculty_name, subject FROM faculties')
        faculties = {row[0]: {"faculty_name": row[1], "subject": row[2]} for row in c.fetchall()}
        conn.close()
        return faculties
    except Exception:
        logging.exception("❌ Failed to fetch faculties")
        return {}


def get_faculty_info(faculty_key):
    """Fetch a specific faculty's information from the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT faculty_name, subject FROM faculties WHERE faculty_key=?', (faculty_key.lower(),))
        row = c.fetchone()
        conn.close()
        if row:
            return {"faculty_name": row[0], "subject": row[1]}
        return None
    except Exception:
        logging.exception("❌ Failed to fetch faculty info")
        return None


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
    faculties = get_all_faculties()
    faculty_subjects = {k: v['subject'] for k, v in faculties.items()}
    return render_template('home.html', faculty_subjects=faculty_subjects)


@app.route('/<faculty>')
def teacher_dashboard(faculty):
    """Display latecomer entries for a given faculty"""
    info = get_faculty_info(faculty)
    
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
    info = get_faculty_info(faculty)
    
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
