"""
data_manager.py - Data validation, CSV import/export, and Pandas preprocessing
for Personal Health Tracker Application.
"""

import io
from typing import Tuple, Optional, Dict, Any
import pandas as pd
from database import save_health_entry, get_all_entries, bulk_insert_entries, DEFAULT_DB_PATH


REQUIRED_CSV_COLUMNS = ["date", "steps", "calories", "sleep_hours", "water_liters"]


def validate_health_entry(
    date_str: str,
    steps: int,
    calories: float,
    sleep_hours: float,
    water_liters: float,
    resting_heart_rate: Optional[int] = None
) -> Tuple[bool, str]:
    """Validate entry inputs for physiological sanity and correct types."""
    try:
        pd.to_datetime(date_str)
    except Exception:
        return False, "Invalid date format. Expected YYYY-MM-DD."

    if steps < 0 or steps > 100000:
        return False, f"Steps ({steps}) must be between 0 and 100,000."

    if calories < 0 or calories > 12000:
        return False, f"Calories ({calories}) must be between 0 and 12,000 kcal."

    if sleep_hours < 0 or sleep_hours > 24:
        return False, f"Sleep duration ({sleep_hours} hrs) must be between 0 and 24 hours."

    if water_liters < 0 or water_liters > 15:
        return False, f"Water intake ({water_liters} L) must be between 0 and 15 liters."

    if resting_heart_rate is not None and (resting_heart_rate < 35 or resting_heart_rate > 220):
        return False, f"Resting heart rate ({resting_heart_rate} bpm) must be between 35 and 220."

    return True, "Valid"


def import_csv_data(uploaded_file, db_path: Optional[str] = None) -> Tuple[bool, str, int]:
    """
    Import health records from a CSV file into the database.
    Validates required columns, handles dates, and reports errors.
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        return False, f"Could not parse CSV file: {str(e)}", 0

    # Clean column names (strip whitespace and lowercase)
    df.columns = df.columns.str.strip().str.lower()

    # Check required columns
    missing = [col for col in REQUIRED_CSV_COLUMNS if col not in df.columns]
    if missing:
        return False, f"CSV is missing required column(s): {', '.join(missing)}", 0

    # Coerce and clean
    try:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df['steps'] = pd.to_numeric(df['steps'], errors='coerce').fillna(0).astype(int)
        df['calories'] = pd.to_numeric(df['calories'], errors='coerce').fillna(0.0).astype(float)
        df['sleep_hours'] = pd.to_numeric(df['sleep_hours'], errors='coerce').fillna(0.0).astype(float)
        df['water_liters'] = pd.to_numeric(df['water_liters'], errors='coerce').fillna(0.0).astype(float)

        if 'resting_heart_rate' in df.columns:
            df['resting_heart_rate'] = pd.to_numeric(df['resting_heart_rate'], errors='coerce')
        else:
            df['resting_heart_rate'] = None

        if 'mood' not in df.columns:
            df['mood'] = 'Good'
        else:
            df['mood'] = df['mood'].fillna('Good')

        if 'notes' not in df.columns:
            df['notes'] = ''
        else:
            df['notes'] = df['notes'].fillna('')

        records = df.to_dict(orient='records')
        count = bulk_insert_entries(records, db_path=db_path)
        return True, f"Successfully imported {count} records.", count

    except Exception as e:
        return False, f"Error processing CSV data: {str(e)}", 0


def export_to_csv(df: pd.DataFrame) -> str:
    """Convert dataframe to CSV string for downloading."""
    if df.empty:
        return ""
    export_df = df.copy()
    if 'date' in export_df.columns:
        export_df['date'] = pd.to_datetime(export_df['date']).dt.strftime('%Y-%m-%d')
    return export_df.to_csv(index=False)
