"""
analytics.py - Pandas-powered data analytics engine for Personal Health Tracker.
Calculates daily metrics, weekly summaries, rolling averages, streaks, and health scores.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


DEFAULT_GOALS = {
    "steps": 10000,
    "calories": 2200.0,
    "sleep_hours": 8.0,
    "water_liters": 2.5
}


def calculate_health_score(
    steps: float,
    calories: float,
    sleep_hours: float,
    water_liters: float,
    goals: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes a composite Daily Health Score (0-100) based on weighted parameters:
    - Steps: 30% (capped at 120% goal)
    - Sleep: 30% (optimal between 7 and 9 hours)
    - Water: 20% (hydration goal adherence)
    - Calories: 20% (calorie burn target)
    """
    g = goals or DEFAULT_GOALS

    # Steps score (30 points max)
    step_ratio = min(1.2, steps / max(1, g.get("steps", 10000)))
    step_pts = min(30.0, step_ratio * 25.0)
    if steps >= g.get("steps", 10000):
        step_pts = 30.0

    # Sleep score (30 points max)
    # 7-9 hours = full 30 points; gradual reduction for deficit or excessive sleep
    target_sleep = g.get("sleep_hours", 8.0)
    if 7.0 <= sleep_hours <= 9.0:
        sleep_pts = 30.0
    elif sleep_hours > 9.0:
        sleep_pts = max(15.0, 30.0 - (sleep_hours - 9.0) * 5.0)
    else:  # sleep < 7.0
        sleep_pts = max(5.0, (sleep_hours / 7.0) * 30.0)

    # Water score (20 points max)
    water_target = g.get("water_liters", 2.5)
    water_ratio = min(1.2, water_liters / max(0.5, water_target))
    water_pts = min(20.0, water_ratio * 20.0)

    # Calorie score (20 points max)
    cal_target = g.get("calories", 2200.0)
    cal_ratio = min(1.2, calories / max(500.0, cal_target))
    cal_pts = min(20.0, cal_ratio * 20.0)

    total_score = round(step_pts + sleep_pts + water_pts + cal_pts, 1)
    total_score = max(0.0, min(100.0, total_score))

    if total_score >= 85:
        category = "Excellent"
        color = "#22c55e"  # Green
    elif total_score >= 70:
        category = "Good"
        color = "#3b82f6"  # Blue
    elif total_score >= 50:
        category = "Moderate"
        color = "#f59e0b"  # Amber
    else:
        category = "Needs Attention"
        color = "#ef4444"  # Red

    return {
        "score": total_score,
        "category": category,
        "color": color,
        "step_pts": round(step_pts, 1),
        "sleep_pts": round(sleep_pts, 1),
        "water_pts": round(water_pts, 1),
        "cal_pts": round(cal_pts, 1)
    }


def calculate_streaks(df: pd.DataFrame, goal_column: str, threshold: float) -> int:
    """Calculate current consecutive streak days meeting or exceeding threshold."""
    if df.empty or goal_column not in df.columns:
        return 0

    sorted_df = df.sort_values(by="date", ascending=False).reset_index(drop=True)
    streak = 0
    for val in sorted_df[goal_column]:
        if val >= threshold:
            streak += 1
        else:
            break
    return streak


def calculate_overall_metrics(df: pd.DataFrame, goals: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Calculate aggregate and comparison metrics across all logged records."""
    if df.empty:
        return {}

    g = goals or DEFAULT_GOALS
    df_clean = df.copy()
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    df_clean = df_clean.sort_values(by='date').reset_index(drop=True)

    total_days = len(df_clean)
    latest_row = df_clean.iloc[-1]

    # Last 7 days metrics
    last_7 = df_clean.tail(7)
    prev_7 = df_clean.iloc[-14:-7] if len(df_clean) >= 14 else pd.DataFrame()

    avg_7_steps = last_7['steps'].mean()
    avg_7_cals = last_7['calories'].mean()
    avg_7_sleep = last_7['sleep_hours'].mean()
    avg_7_water = last_7['water_liters'].mean()

    # Compare with previous 7 days if available
    pct_change_steps = None
    pct_change_cals = None
    if not prev_7.empty and prev_7['steps'].mean() > 0:
        pct_change_steps = round(((avg_7_steps - prev_7['steps'].mean()) / prev_7['steps'].mean()) * 100, 1)
        pct_change_cals = round(((avg_7_cals - prev_7['calories'].mean()) / prev_7['calories'].mean()) * 100, 1)

    # Goal adherence percentage
    step_success_rate = round((df_clean['steps'] >= g['steps']).mean() * 100, 1)
    sleep_success_rate = round(((df_clean['sleep_hours'] >= 7.0) & (df_clean['sleep_hours'] <= 9.0)).mean() * 100, 1)
    water_success_rate = round((df_clean['water_liters'] >= g['water_liters']).mean() * 100, 1)

    # Current streaks
    step_streak = calculate_streaks(df_clean, 'steps', g['steps'])
    water_streak = calculate_streaks(df_clean, 'water_liters', g['water_liters'])

    # Overall totals
    total_steps = int(df_clean['steps'].sum())
    total_calories = float(df_clean['calories'].sum())
    total_water = float(df_clean['water_liters'].sum())

    # Latest day health score
    latest_score = calculate_health_score(
        latest_row['steps'],
        latest_row['calories'],
        latest_row['sleep_hours'],
        latest_row['water_liters'],
        g
    )

    return {
        "total_days": total_days,
        "latest_date": latest_row['date'].strftime('%Y-%m-%d'),
        "latest_steps": int(latest_row['steps']),
        "latest_calories": float(latest_row['calories']),
        "latest_sleep": float(latest_row['sleep_hours']),
        "latest_water": float(latest_row['water_liters']),
        "latest_score": latest_score,
        "avg_7_steps": round(avg_7_steps, 0),
        "avg_7_cals": round(avg_7_cals, 0),
        "avg_7_sleep": round(avg_7_sleep, 1),
        "avg_7_water": round(avg_7_water, 2),
        "pct_change_steps": pct_change_steps,
        "pct_change_cals": pct_change_cals,
        "step_success_rate": step_success_rate,
        "sleep_success_rate": sleep_success_rate,
        "water_success_rate": water_success_rate,
        "step_streak": step_streak,
        "water_streak": water_streak,
        "total_steps": total_steps,
        "total_calories": round(total_calories, 1),
        "total_water": round(total_water, 1),
        "all_time_max_steps": int(df_clean['steps'].max()),
        "all_time_max_cals": float(df_clean['calories'].max()),
    }


def generate_weekly_summary_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups health records into weekly chunks (ending Sunday) with comprehensive aggregates.
    """
    if df.empty:
        return pd.DataFrame()

    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    df_copy = df_copy.set_index('date').sort_index()

    # Resample weekly
    weekly = df_copy.resample('W-SUN').agg(
        days_logged=('steps', 'count'),
        total_steps=('steps', 'sum'),
        avg_steps=('steps', 'mean'),
        max_steps=('steps', 'max'),
        total_calories=('calories', 'sum'),
        avg_calories=('calories', 'mean'),
        avg_sleep=('sleep_hours', 'mean'),
        min_sleep=('sleep_hours', 'min'),
        max_sleep=('sleep_hours', 'max'),
        total_water=('water_liters', 'sum'),
        avg_water=('water_liters', 'mean')
    ).reset_index()

    weekly['week_label'] = weekly['date'].apply(
        lambda d: f"Week ending {d.strftime('%b %d, %Y')}"
    )

    # Format numeric columns nicely
    weekly['avg_steps'] = weekly['avg_steps'].round(0)
    weekly['avg_calories'] = weekly['avg_calories'].round(1)
    weekly['avg_sleep'] = weekly['avg_sleep'].round(1)
    weekly['avg_water'] = weekly['avg_water'].round(2)
    weekly['total_calories'] = weekly['total_calories'].round(0)
    weekly['total_water'] = weekly['total_water'].round(1)

    return weekly.sort_values(by='date', ascending=False)
