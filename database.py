import sqlite3
import pandas as pd
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
            subject TEXT,
            level TEXT,
            question TEXT,
            answer TEXT,
            score REAL,
            date_time TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(interview_history)")
    columns = [row[1] for row in cursor.fetchall()]

    if "subject" not in columns:
        cursor.execute(
            "ALTER TABLE interview_history ADD COLUMN subject TEXT"
        )

    conn.commit()
    conn.close()


def save_attempt(subject, level, question, answer, score):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interview_history
        (subject, level, question, answer, score, date_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        subject,
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

    history = pd.read_sql_query("""
        SELECT subject, level, question, answer, score, date_time
        FROM interview_history
        ORDER BY id DESC
    """, conn)

    conn.close()
    return history


setup_database()
