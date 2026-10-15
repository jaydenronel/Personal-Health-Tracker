"""
sample_data.py - Generates realistic synthetic 30-day health tracking data
for demonstration, testing, and evaluation of the Personal Health Tracker Application.
"""

from datetime import date, timedelta
import random
from typing import List, Dict, Any


def generate_sample_health_records(days: int = 30) -> List[Dict[str, Any]]:
    """
    Generate realistic health tracking data for the past `days` days.
    Simulates variations between weekdays and weekends, sleep changes, and hydration.
    """
    today = date.today()
    records = []

    # Seed for reproducible realistic look
    random.seed(42)

    moods = ["Energetic", "Great", "Good", "Normal", "Tired", "Stressed"]

    for i in range(days - 1, -1, -1):
        day_date = today - timedelta(days=i)
        is_weekend = day_date.weekday() >= 5

        # Base steps with weekend variation
        if is_weekend:
            # Maybe a long hike or a lazy Sunday
            base_steps = random.choice([5500, 11500, 13200, 8400, 12000])
        else:
            # Weekday office/walking
            base_steps = random.randint(6500, 10800)

        # Calorie burn correlates with steps + basal metabolic rate
        # ~1800 BMR + ~0.045 kcal per step
        calories = round(1750 + (base_steps * 0.046) + random.uniform(-100, 120), 1)

        # Sleep duration (mostly 6.5 to 8.5 hours, occasional short or long night)
        if is_weekend:
            sleep = round(random.uniform(7.2, 9.0), 1)
        else:
            sleep = round(random.uniform(6.0, 8.2), 1)

        # Water intake (liters)
        water = round(random.uniform(1.8, 3.4), 2)

        # Heart rate
        hr = random.randint(62, 74)

        # Mood assignment based on sleep and activity
        if sleep >= 7.5 and base_steps >= 9000:
            mood = random.choice(["Energetic", "Great", "Good"])
        elif sleep < 6.5:
            mood = random.choice(["Tired", "Normal"])
        else:
            mood = random.choice(["Good", "Normal"])

        # Notes
        notes_options = [
            "Morning jog in park",
            "Gym strength workout",
            "Busy workday, took evening walk",
            "Rest day and light stretching",
            "Weekend hike with friends",
            "Stayed well hydrated today",
            "Evening yoga session",
            "Cycling commute",
            "Relaxing recovery day",
            ""
        ]
        note = random.choice(notes_options)

        records.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "steps": int(base_steps),
            "calories": float(calories),
            "sleep_hours": float(sleep),
            "water_liters": float(water),
            "resting_heart_rate": int(hr),
            "mood": mood,
            "notes": note
        })

    return records
