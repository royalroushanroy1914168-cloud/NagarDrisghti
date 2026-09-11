import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "nagar_drishti.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            latitude REAL,
            longitude REAL,
            image_path TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_report(problem_type,severity,priority_score,latitude,longitude,image_path):
    conn=get_connection()
    cursor=conn.execute("""
        INSERT INTO reports
        (problem_type,severity,priority_score,latitude,longitude,image_path)
        VALUES (?,?,?,?,?,?)
    """,(problem_type,severity,priority_score,latitude,longitude,image_path))
    conn.commit()
    report_id=cursor.lastrowid
    conn.close()
    return report_id

def get_reports():
    conn=get_connection()
    reports=conn.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in reports]