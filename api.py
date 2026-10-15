"""
api.py - Dedicated REST API Backend for Personal Health Tracker.
Provides RESTful endpoints for CRUD operations, analytics metrics,
weekly summaries, and personalized health recommendations using FastAPI.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import (
    init_db,
    save_health_entry,
    get_all_entries,
    get_entry_by_date,
    delete_entry_by_date,
    bulk_insert_entries,
    reset_database
)
from analytics import (
    calculate_overall_metrics,
    calculate_health_score,
    generate_weekly_summary_dataframe,
    DEFAULT_GOALS
)
from recommendations import generate_health_recommendations
from sample_data import generate_sample_health_records

app = FastAPI(
    title="Personal Health Tracker REST API",
    description="Backend service providing health tracking, analytics, and recommendation endpoints.",
    version="1.0.0"
)

# Enable CORS for external frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema
init_db()


class HealthRecordModel(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2026-10-15")
    steps: int = Field(..., ge=0, le=100000, description="Steps walked", example=8500)
    calories: float = Field(..., ge=0.0, le=12000.0, description="Calories burned in kcal", example=2150.0)
    sleep_hours: float = Field(..., ge=0.0, le=24.0, description="Sleep duration in hours", example=7.5)
    water_liters: float = Field(..., ge=0.0, le=15.0, description="Water consumed in liters", example=2.5)
    resting_heart_rate: Optional[int] = Field(None, ge=30, le=220, description="Heart rate in bpm", example=68)
    mood: Optional[str] = Field("Good", description="Mood / Energy level", example="Energetic")
    notes: Optional[str] = Field("", description="Activity notes", example="5km morning jog")


@app.get("/", tags=["Health"])
def health_check():
    """Verify backend API service status."""
    return {
        "status": "online",
        "service": "Personal Health Tracker Backend API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/api/records", tags=["Records"])
def get_records():
    """Fetch all stored health logs."""
    df = get_all_entries()
    if df.empty:
        return []
    df_copy = df.copy()
    df_copy['date'] = df_copy['date'].dt.strftime('%Y-%m-%d')
    return df_copy.to_dict(orient="records")


@app.get("/api/records/{record_date}", tags=["Records"])
def get_record(record_date: str):
    """Retrieve health log for a specific date (YYYY-MM-DD)."""
    entry = get_entry_by_date(record_date)
    if not entry:
        raise HTTPException(status_code=404, detail=f"No record found for date {record_date}")
    return entry


@app.post("/api/records", tags=["Records"])
def create_or_update_record(record: HealthRecordModel):
    """Create or update a daily health record."""
    success = save_health_entry(
        date=record.date,
        steps=record.steps,
        calories=record.calories,
        sleep_hours=record.sleep_hours,
        water_liters=record.water_liters,
        resting_heart_rate=record.resting_heart_rate,
        mood=record.mood,
        notes=record.notes
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save record.")
    return {"message": f"Record for {record.date} successfully saved."}


@app.delete("/api/records/{record_date}", tags=["Records"])
def delete_record(record_date: str):
    """Delete a health record by date."""
    deleted = delete_entry_by_date(record_date)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Record for {record_date} not found.")
    return {"message": f"Record for {record_date} deleted."}


@app.get("/api/metrics", tags=["Analytics"])
def get_metrics(
    goal_steps: float = 10000.0,
    goal_calories: float = 2200.0,
    goal_sleep: float = 8.0,
    goal_water: float = 2.5
):
    """Calculate overall KPIs, 7-day rolling averages, and latest health score."""
    df = get_all_entries()
    if df.empty:
        return {"message": "No data available."}

    goals = {
        "steps": goal_steps,
        "calories": goal_calories,
        "sleep_hours": goal_sleep,
        "water_liters": goal_water
    }
    return calculate_overall_metrics(df, goals)


@app.get("/api/weekly-summary", tags=["Analytics"])
def get_weekly_summary():
    """Retrieve weekly aggregate trends."""
    df = get_all_entries()
    if df.empty:
        return []

    weekly_df = generate_weekly_summary_dataframe(df)
    weekly_copy = weekly_df.copy()
    weekly_copy['date'] = weekly_copy['date'].dt.strftime('%Y-%m-%d')
    return weekly_copy.to_dict(orient="records")


@app.get("/api/recommendations", tags=["Insights"])
def get_recommendations(
    goal_steps: float = 10000.0,
    goal_calories: float = 2200.0,
    goal_sleep: float = 8.0,
    goal_water: float = 2.5
):
    """Generate personalized health recommendations based on recent patterns."""
    df = get_all_entries()
    goals = {
        "steps": goal_steps,
        "calories": goal_calories,
        "sleep_hours": goal_sleep,
        "water_liters": goal_water
    }
    return generate_health_recommendations(df, goals)


@app.post("/api/seed-demo-data", tags=["Data Management"])
def seed_demo_data(days: int = Query(30, ge=1, le=90)):
    """Generate and insert realistic sample records."""
    records = generate_sample_health_records(days=days)
    count = bulk_insert_entries(records)
    return {"message": f"Successfully seeded {count} demo records."}
