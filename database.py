"""
database.py - SQLite backend data persistence layer for Personal Health Tracker.
Provides database initialization, CRUD operations, upserts, and bulk loading.
"""

import os
import sqlite3
import pandas as pd
from typing import Optional, Dict, Any, List

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "health_tracker.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get a SQLite database connection with row factory enabled."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the health_records table if it doesn't already exist."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    steps INTEGER NOT NULL CHECK (steps >= 0),
                    calories REAL NOT NULL CHECK (calories >= 0),
                    sleep_hours REAL NOT NULL CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
                    water_liters REAL NOT NULL CHECK (water_liters >= 0),
                    resting_heart_rate INTEGER CHECK (resting_heart_rate IS NULL OR resting_heart_rate > 30),
                    mood TEXT DEFAULT 'Good',
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_health_records_date ON health_records (date);")
    finally:
        conn.close()


def save_health_entry(
    date: str,
    steps: int,
    calories: float,
    sleep_hours: float,
    water_liters: float,
    resting_heart_rate: Optional[int] = None,
    mood: str = "Good",
    notes: str = "",
    db_path: Optional[str] = None
) -> bool:
    """
    Insert or update a daily health record.
    If an entry for this date already exists, it updates all values.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                INSERT INTO health_records (date, steps, calories, sleep_hours, water_liters, resting_heart_rate, mood, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    steps = excluded.steps,
                    calories = excluded.calories,
                    sleep_hours = excluded.sleep_hours,
                    water_liters = excluded.water_liters,
                    resting_heart_rate = excluded.resting_heart_rate,
                    mood = excluded.mood,
                    notes = excluded.notes,
                    created_at = CURRENT_TIMESTAMP;
            """, (date, int(steps), float(calories), float(sleep_hours), float(water_liters), resting_heart_rate, mood, notes))
        return True
    finally:
        conn.close()


def get_all_entries(db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieve all health records ordered by date ascending as a Pandas DataFrame.
    """
    conn = get_connection(db_path)
    try:
        query = """
            SELECT date, steps, calories, sleep_hours, water_liters, resting_heart_rate, mood, notes
            FROM health_records
            ORDER BY date ASC;
        """
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    finally:
        conn.close()


def get_entry_by_date(date: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single day's health record by date string (YYYY-MM-DD)."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, steps, calories, sleep_hours, water_liters, resting_heart_rate, mood, notes
            FROM health_records
            WHERE date = ?;
        """, (date,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def delete_entry_by_date(date: str, db_path: Optional[str] = None) -> bool:
    """Delete a health record by date string."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM health_records WHERE date = ?;", (date,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def bulk_insert_entries(records: List[Dict[str, Any]], db_path: Optional[str] = None) -> int:
    """
    Bulk upsert a list of records.
    Each record must have date, steps, calories, sleep_hours, water_liters.
    """
    conn = get_connection(db_path)
    count = 0
    try:
        with conn:
            for r in records:
                conn.execute("""
                    INSERT INTO health_records (date, steps, calories, sleep_hours, water_liters, resting_heart_rate, mood, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(date) DO UPDATE SET
                        steps = excluded.steps,
                        calories = excluded.calories,
                        sleep_hours = excluded.sleep_hours,
                        water_liters = excluded.water_liters,
                        resting_heart_rate = excluded.resting_heart_rate,
                        mood = excluded.mood,
                        notes = excluded.notes,
                        created_at = CURRENT_TIMESTAMP;
                """, (
                    str(r['date']),
                    int(r.get('steps', 0)),
                    float(r.get('calories', 0.0)),
                    float(r.get('sleep_hours', 0.0)),
                    float(r.get('water_liters', 0.0)),
                    r.get('resting_heart_rate'),
                    r.get('mood', 'Good'),
                    r.get('notes', '')
                ))
                count += 1
        return count
    finally:
        conn.close()


def reset_database(db_path: Optional[str] = None) -> None:
    """Clear all records from the database table."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM health_records;")
    finally:
        conn.close()
