"""
recommendations.py - Health Insights & Recommendation Engine for Personal Health Tracker.
Evaluates user activity, sleep, hydration, and calorie patterns to provide personalized,
evidence-based lifestyle recommendations.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np


def generate_health_recommendations(df: pd.DataFrame, goals: Dict[str, float]) -> List[Dict[str, str]]:
    """
    Evaluates historical user data (focusing on the latest 7 to 14 days)
    and produces actionable insights and categorized recommendations.
    """
    if df.empty:
        return [
            {
                "category": "Getting Started",
                "status": "info",
                "title": "Start Logging Daily Activities",
                "message": "Begin logging your steps, sleep, water, and calories daily to receive personalized health recommendations.",
                "action": "Add your first entry or load the demo dataset from the sidebar."
            }
        ]

    df_clean = df.copy()
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    df_clean = df_clean.sort_values(by='date')

    # Take latest 7 days or all if less than 7
    recent = df_clean.tail(min(7, len(df_clean)))

    avg_steps = recent['steps'].mean()
    avg_sleep = recent['sleep_hours'].mean()
    avg_water = recent['water_liters'].mean()
    avg_cals = recent['calories'].mean()

    min_sleep = recent['sleep_hours'].min()
    sleep_std = recent['sleep_hours'].std() if len(recent) > 1 else 0.0

    sedentary_days = (recent['steps'] < 5000).sum()
    low_water_days = (recent['water_liters'] < 2.0).sum()

    recommendations = []

    # 1. SLEEP INSIGHTS & RECOMMENDATIONS
    if avg_sleep < 6.5:
        recommendations.append({
            "category": "Sleep Health",
            "status": "warning",
            "title": "Sleep Debt Detected (Under 6.5 hrs avg)",
            "message": f"Your 7-day average sleep is {avg_sleep:.1f} hours, which is below the recommended 7–9 hours for cognitive restoration and metabolic recovery.",
            "action": "Set a firm bedtime 45 minutes earlier tonight. Avoid bright screens and heavy meals within 1 hour of sleep."
        })
    elif avg_sleep > 9.5:
        recommendations.append({
            "category": "Sleep Health",
            "status": "info",
            "title": "Extended Sleep Duration Detected",
            "message": f"You are averaging {avg_sleep:.1f} hours of sleep. While rest is essential, prolonged sleeping can indicate recovery debt or irregular sleep timing.",
            "action": "Ensure consistent wake-up times throughout the week to stabilize your circadian rhythm."
        })
    elif sleep_std is not None and sleep_std > 1.8:
        recommendations.append({
            "category": "Sleep Health",
            "status": "warning",
            "title": "High Sleep Schedule Variability",
            "message": f"Your sleep duration varies significantly (std dev ±{sleep_std:.1f}h). Irregular sleep cycles can trigger daytime fatigue.",
            "action": "Aim to keep your sleep and wake times within a 30-minute window every day, including weekends."
        })
    else:
        recommendations.append({
            "category": "Sleep Health",
            "status": "success",
            "title": "Optimal Sleep Pattern Maintained",
            "message": f"Great job! Your average sleep of {avg_sleep:.1f} hours is in the prime restorative zone (7–9 hours).",
            "action": "Maintain your current wind-down routine to keep energy and immunity high."
        })

    # 2. ACTIVITY / STEPS INSIGHTS & RECOMMENDATIONS
    step_target = goals.get("steps", 10000)
    if avg_steps >= step_target:
        recommendations.append({
            "category": "Physical Activity",
            "status": "success",
            "title": "Outstanding Activity Level!",
            "message": f"You are averaging {int(avg_steps):,} steps/day, exceeding your daily goal of {int(step_target):,} steps.",
            "action": "Incorporate light stretching and muscle recovery into your routine to prevent joint stiffness."
        })
    elif avg_steps >= 7500:
        recommendations.append({
            "category": "Physical Activity",
            "status": "info",
            "title": "Moderately Active Lifestyle",
            "message": f"You are averaging {int(avg_steps):,} steps/day. You are close to your {int(step_target):,} step goal.",
            "action": "A brief 15-minute post-dinner walk will easily add 1,500 steps and help you consistently surpass your target."
        })
    else:
        recommendations.append({
            "category": "Physical Activity",
            "status": "warning",
            "title": "Step Goal Opportunity (Sedentary Trend)",
            "message": f"Your average daily steps ({int(avg_steps):,}) fall short of the active threshold. You logged {sedentary_days} day(s) below 5,000 steps.",
            "action": "Take 5-minute active movement breaks every 90 minutes during work or switch to a standing desk."
        })

    # 3. HYDRATION INSIGHTS & RECOMMENDATIONS
    water_target = goals.get("water_liters", 2.5)
    if avg_water >= water_target:
        recommendations.append({
            "category": "Hydration",
            "status": "success",
            "title": "Excellent Hydration Habits",
            "message": f"You average {avg_water:.2f} liters/day (~{int(avg_water * 4)} glasses). Proper hydration boosts cognitive focus and stamina.",
            "action": "Keep keeping a refillable water bottle handy at your workspace."
        })
    elif avg_water < 1.8:
        recommendations.append({
            "category": "Hydration",
            "status": "danger",
            "title": "Low Hydration Alert",
            "message": f"You drank an average of only {avg_water:.2f} L/day, falling well below your target of {water_target:.1f} L.",
            "action": "Drink a full glass of water first thing in the morning and pair each meal with a glass of water."
        })
    else:
        recommendations.append({
            "category": "Hydration",
            "status": "info",
            "title": "Hydration Approaching Target",
            "message": f"You are averaging {avg_water:.2f} L/day. Adding just 1–2 more glasses will hit your {water_target:.1f} L goal.",
            "action": "Infuse water with lemon or cucumber slices to make hitting your goal easier."
        })

    # 4. CALORIES & METABOLISM INSIGHTS
    cal_target = goals.get("calories", 2200.0)
    if avg_cals >= cal_target:
        recommendations.append({
            "category": "Caloric Burn",
            "status": "success",
            "title": "Target Caloric Expenditure Reached",
            "message": f"You burned an average of {int(avg_cals):,} kcal/day over the last 7 days, meeting your daily target.",
            "action": "Ensure adequate protein intake (1.2–1.6g per kg) to support muscle repair."
        })
    else:
        diff = int(cal_target - avg_cals)
        recommendations.append({
            "category": "Caloric Burn",
            "status": "info",
            "title": "Calorie Burn Below Goal",
            "message": f"Your average burn of {int(avg_cals):,} kcal is {diff} kcal below your target.",
            "action": "Incorporate low-impact cardio, brisk walking, or staircase climbing to boost daily energy expenditure."
        })

    return recommendations
