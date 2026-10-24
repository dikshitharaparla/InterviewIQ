import sqlite3
import pandas as pd

DB_NAME = "interview_history.db"


def setup_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            level TEXT,
            question TEXT,
            answer TEXT,
            score REAL,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(attempts)")
    columns = [column[1] for column in cursor.fetchall()]

    if "level" not in columns:
        cursor.execute(
            "ALTER TABLE attempts ADD COLUMN level TEXT"
        )

    connection.commit()
    connection.close()


def save_attempt(subject, level, question, answer, score):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO attempts
        (subject, level, question, answer, score)
        VALUES (?, ?, ?, ?, ?)
    """, (subject, level, question, answer, score))

    connection.commit()
    connection.close()


def get_attempts():
    connection = sqlite3.connect(DB_NAME)

    dataframe = pd.read_sql_query("""
        SELECT subject, level, question, answer, score, date_time
        FROM attempts
        ORDER BY date_time DESC
    """, connection)

    connection.close()
    return dataframe