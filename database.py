import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
DB_NAME = "interviewiq.db"
IST = ZoneInfo("Asia/Kolkata")
def get_current_time():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            question TEXT,
            answer TEXT,
            score REAL,
            date_time TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_attempt(level, question, answer, score):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interview_history
        (level, question, answer, score, date_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        level,
        question,
        answer,
        score,
        get_current_time()
    ))

    conn.commit()
    conn.close()

def get_attempts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT level, question, answer, score, date_time
        FROM interview_history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows

setup_database()
```
