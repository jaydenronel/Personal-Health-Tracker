"""
app.py - Main Streamlit Web Application for the Personal Health Tracker.
Implements the interactive UI, dashboards, daily logging form, visual charts,
weekly summaries, daily reports, and health insights recommendation engine.
"""

import os
from datetime import date, datetime
import pandas as pd
import streamlit as st

from database import (
    init_db,
    save_health_entry,
    get_all_entries,
    get_entry_by_date,
    delete_entry_by_date,
    reset_database,
    DEFAULT_DB_PATH
)
from data_manager import (
    validate_health_entry,
    import_csv_data,
    export_to_csv
)
from analytics import (
    calculate_overall_metrics,
    calculate_health_score,
    generate_weekly_summary_dataframe,
    DEFAULT_GOALS
)
from visualizer import (
    plot_health_trends,
    plot_weekly_breakdown_bars,
    plot_correlations,
    plot_single_day_gauge
)
from recommendations import generate_health_recommendations
from sample_data import generate_sample_health_records
from database import bulk_insert_entries

# Page Configuration
st.set_page_config(
    page_title="Personal Health Tracker",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Schema
init_db()


def load_data() -> pd.DataFrame:
    """Fetch current health data from SQLite database."""
    return get_all_entries()


# --- SIDEBAR: GOALS & ACTIONS ---
with st.sidebar:
    st.title("⚙️ Health Settings")
    st.markdown("Set your daily personal targets:")

    goal_steps = st.number_input("Daily Step Goal", min_value=1000, max_value=50000, value=10000, step=500)
    goal_calories = st.number_input("Daily Calorie Burn Goal (kcal)", min_value=500, max_value=6000, value=2200, step=50)
    goal_sleep = st.number_input("Daily Sleep Goal (hours)", min_value=4.0, max_value=12.0, value=8.0, step=0.5)
    goal_water = st.number_input("Daily Water Goal (liters)", min_value=0.5, max_value=6.0, value=2.5, step=0.1)

    user_goals = {
        "steps": float(goal_steps),
        "calories": float(goal_calories),
        "sleep_hours": float(goal_sleep),
        "water_liters": float(goal_water)
    }

    st.markdown("---")
    st.subheader("📦 Data Management")

    col_demo, col_clear = st.columns(2)
    with col_demo:
        if st.button("Load Demo Data", use_container_width=True, help="Load 30 days of realistic sample data"):
            records = generate_sample_health_records(days=30)
            bulk_insert_entries(records)
            st.success("Loaded 30-day demo records!")
            st.rerun()

    with col_clear:
        if st.button("Reset All", use_container_width=True, type="secondary", help="Clear all stored logs"):
            reset_database()
            st.warning("All records cleared.")
            st.rerun()

    # CSV Export
    current_df = load_data()
    if not current_df.empty:
        csv_data = export_to_csv(current_df)
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv_data,
            file_name=f"health_tracker_export_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # CSV Import
    uploaded_file = st.file_uploader("Upload CSV Backup", type=["csv"], help="Upload previously exported or compatible CSV")
    if uploaded_file is not None:
        if st.button("Import Uploaded CSV", use_container_width=True):
            success, msg, count = import_csv_data(uploaded_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.85em; color: #64748b; text-align: center;'>"
        "Personal Health Tracker<br>Built with Python, Pandas, Matplotlib & Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


# --- MAIN HEADER ---
st.markdown(
    """
    <div style='background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;'>
        <h1 style='margin: 0; font-size: 2.2rem; font-weight: 700;'>🏃 Personal Health Tracker Application</h1>
        <p style='margin: 0.3rem 0 0 0; font-size: 1.05rem; opacity: 0.9;'>
            Track daily activities, monitor essential health metrics, visualize trends, and receive evidence-based wellness insights.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

df = load_data()
metrics = calculate_overall_metrics(df, user_goals) if not df.empty else {}

# Main Tabs
tab_overview, tab_log, tab_visuals, tab_reports, tab_insights = st.tabs([
    "📊 Dashboard Overview",
    "✍️ Log Daily Data",
    "📈 Visual Trends & Charts",
    "📋 Daily & Weekly Reports",
    "💡 Health Insights & Tips"
])


# ==========================================
# TAB 1: DASHBOARD OVERVIEW
# ==========================================
with tab_overview:
    if df.empty:
        st.info("👋 Welcome! You haven't logged any health activities yet. Use the **Log Daily Data** tab or click **'Load Demo Data'** in the sidebar to get started immediately.")
    else:
        st.subheader("🎯 Latest Daily Highlights & Health Score")

        score_info = metrics.get("latest_score", {})
        score_val = score_info.get("score", 0)
        score_cat = score_info.get("category", "N/A")
        score_color = score_info.get("color", "#3b82f6")

        col_score, col_steps, col_cals, col_sleep, col_water = st.columns([1.2, 1, 1, 1, 1])

        with col_score:
            st.markdown(
                f"""
                <div style='background: #f8fafc; border: 2px solid {score_color}; border-radius: 10px; padding: 1rem; text-align: center;'>
                    <div style='font-size: 0.85rem; color: #475569; font-weight: 600;'>LATEST HEALTH SCORE</div>
                    <div style='font-size: 2.2rem; font-weight: 800; color: {score_color};'>{score_val} <span style='font-size: 1rem;'>/ 100</span></div>
                    <div style='font-size: 0.85rem; font-weight: 700; color: {score_color};'>{score_cat}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_steps:
            st.metric(
                label="Steps Walked",
                value=f"{metrics.get('latest_steps', 0):,}",
                delta=f"{metrics.get('pct_change_steps', 0)}% vs prev week" if metrics.get('pct_change_steps') is not None else None,
                help=f"Target: {int(user_goals['steps']):,} steps"
            )

        with col_cals:
            st.metric(
                label="Calories Burned",
                value=f"{metrics.get('latest_calories', 0):,.0f} kcal",
                delta=f"{metrics.get('pct_change_cals', 0)}% vs prev week" if metrics.get('pct_change_cals') is not None else None,
                help=f"Target: {int(user_goals['calories']):,} kcal"
            )

        with col_sleep:
            st.metric(
                label="Sleep Duration",
                value=f"{metrics.get('latest_sleep', 0):.1f} hrs",
                delta=f"{round(metrics.get('latest_sleep', 0) - user_goals['sleep_hours'], 1)} hrs vs goal",
                help=f"Target: {user_goals['sleep_hours']} hours"
            )

        with col_water:
            st.metric(
                label="Water Intake",
                value=f"{metrics.get('latest_water', 0):.2f} L",
                delta=f"{round(metrics.get('latest_water', 0) - user_goals['water_liters'], 2)} L vs goal",
                help=f"Target: {user_goals['water_liters']} L (~{int(user_goals['water_liters'] * 4)} glasses)"
            )

        st.markdown("---")

        # 7-Day Performance & Streaks Row
        col_summary, col_streaks = st.columns([2, 1])

        with col_summary:
            st.subheader("📅 7-Day Rolling Averages")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Daily Steps", f"{int(metrics.get('avg_7_steps', 0)):,}")
            c2.metric("Avg Calories", f"{int(metrics.get('avg_7_cals', 0)):,} kcal")
            c3.metric("Avg Sleep", f"{metrics.get('avg_7_sleep', 0):.1f} hrs")
            c4.metric("Avg Water", f"{metrics.get('avg_7_water', 0):.2f} L")

            # Progress toward goals
            st.markdown("##### Goal Success Rate (All Logged Days)")
            st.write(f"🚶 Step Target Hit: **{metrics.get('step_success_rate', 0)}%** of days")
            st.progress(min(1.0, metrics.get('step_success_rate', 0) / 100))

            st.write(f"😴 Healthy Sleep (7-9h): **{metrics.get('sleep_success_rate', 0)}%** of days")
            st.progress(min(1.0, metrics.get('sleep_success_rate', 0) / 100))

            st.write(f"💧 Water Target Hit: **{metrics.get('water_success_rate', 0)}%** of days")
            st.progress(min(1.0, metrics.get('water_success_rate', 0) / 100))

        with col_streaks:
            st.subheader("🔥 Consistency & Records")
            st.markdown(
                f"""
                <div style='background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem;'>
                    <div style='font-weight: 700; color: #1e293b;'>🚶 Step Goal Streak</div>
                    <div style='font-size: 1.5rem; font-weight: 800; color: #2563eb;'>{metrics.get('step_streak', 0)} consecutive days</div>
                </div>
                <div style='background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem;'>
                    <div style='font-weight: 700; color: #1e293b;'>💧 Hydration Goal Streak</div>
                    <div style='font-size: 1.5rem; font-weight: 800; color: #0284c7;'>{metrics.get('water_streak', 0)} consecutive days</div>
                </div>
                <div style='background: #f1f5f9; padding: 1rem; border-radius: 8px;'>
                    <div style='font-weight: 700; color: #1e293b;'>🏆 All-Time Records</div>
                    <div style='font-size: 0.9rem; color: #334155; margin-top: 4px;'>
                        Max Steps: <b>{metrics.get('all_time_max_steps', 0):,}</b><br>
                        Max Calories: <b>{int(metrics.get('all_time_max_cals', 0)):,} kcal</b><br>
                        Total Steps Logged: <b>{metrics.get('total_steps', 0):,}</b><br>
                        Total Days Tracked: <b>{metrics.get('total_days', 0)} days</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ==========================================
# TAB 2: LOG DAILY DATA
# ==========================================
with tab_log:
    st.subheader("✍️ Enter Daily Health Activity")
    st.markdown("Record your daily metrics below. If an entry for the selected date already exists, it will be updated.")

    with st.form("health_entry_form", clear_on_submit=False):
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            entry_date = st.date_input("Entry Date", value=date.today())
            date_str = entry_date.strftime("%Y-%m-%d")

            # Check if record already exists to prefill
            existing = get_entry_by_date(date_str)
            if existing:
                st.info(f"ℹ️ An entry for {date_str} already exists. Submitting will update it.")

            steps_val = st.number_input(
                "Steps Walked",
                min_value=0,
                max_value=100000,
                value=int(existing['steps']) if existing else 8500,
                step=250,
                help="Total steps tracked from your phone, watch, or pedometer"
            )

            calories_val = st.number_input(
                "Calories Burned (kcal)",
                min_value=0.0,
                max_value=12000.0,
                value=float(existing['calories']) if existing else 2100.0,
                step=50.0,
                help="Total active and basal metabolic energy expenditure in kcal"
            )

        with col_f2:
            sleep_val = st.number_input(
                "Sleep Duration (hours)",
                min_value=0.0,
                max_value=24.0,
                value=float(existing['sleep_hours']) if existing else 7.5,
                step=0.25,
                help="Total hours of sleep logged last night"
            )

            water_val = st.number_input(
                "Water Intake (liters)",
                min_value=0.0,
                max_value=15.0,
                value=float(existing['water_liters']) if existing else 2.5,
                step=0.1,
                help="Daily water consumption (1 liter ≈ 4 glasses)"
            )
            st.caption(f"Equivalent to approximately **{int(water_val * 4)} glasses** of water (250ml each).")

        st.markdown("##### Optional Health Parameters")
        col_f3, col_f4 = st.columns(2)

        with col_f3:
            hr_default = int(existing['resting_heart_rate']) if (existing and existing.get('resting_heart_rate')) else 70
            heart_rate = st.number_input(
                "Resting Heart Rate (bpm) (Optional)",
                min_value=35,
                max_value=220,
                value=hr_default,
                help="Resting heart rate in beats per minute"
            )
            mood_options = ["Energetic", "Great", "Good", "Normal", "Tired", "Stressed"]
            current_mood = existing['mood'] if (existing and existing.get('mood') in mood_options) else "Good"
            mood = st.selectbox("Daily Energy & Mood", options=mood_options, index=mood_options.index(current_mood))

        with col_f4:
            notes_val = existing['notes'] if (existing and existing.get('notes')) else ""
            notes = st.text_area(
                "Activity Notes / Workout Details",
                value=notes_val,
                placeholder="e.g. 5km evening jog, strength training, feeling well-rested..."
            )

        submit_btn = st.form_submit_button("💾 Save Daily Health Record", use_container_width=True, type="primary")

        if submit_btn:
            is_valid, err_msg = validate_health_entry(
                date_str=date_str,
                steps=steps_val,
                calories=calories_val,
                sleep_hours=sleep_val,
                water_liters=water_val,
                resting_heart_rate=heart_rate
            )

            if not is_valid:
                st.error(f"⚠️ Validation Error: {err_msg}")
            else:
                save_health_entry(
                    date=date_str,
                    steps=steps_val,
                    calories=calories_val,
                    sleep_hours=sleep_val,
                    water_liters=water_val,
                    resting_heart_rate=heart_rate,
                    mood=mood,
                    notes=notes
                )
                st.success(f"✅ Health record for {date_str} successfully saved!")
                st.rerun()

    # Quick table of recent 5 entries
    if not df.empty:
        st.markdown("---")
        st.subheader("📋 Recently Logged Entries")
        display_df = df.sort_values(by='date', ascending=False).head(5).copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True, hide_index=True)


# ==========================================
# TAB 3: VISUAL TRENDS & CHARTS (MATPLOTLIB)
# ==========================================
with tab_visuals:
    st.subheader("📈 Graphical Visualization of Health Trends")
    st.markdown("Visual insights powered by **Matplotlib** to understand long-term activity patterns.")

    if df.empty:
        st.info("No data available to plot. Please add records or load demo data.")
    else:
        # Time Filter
        col_filt1, col_filt2 = st.columns([1, 3])
        with col_filt1:
            time_filter = st.selectbox(
                "Filter Timeframe",
                options=["All History", "Last 7 Days", "Last 14 Days", "Last 30 Days"],
                index=0
            )

        filtered_df = df.copy()
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])

        if time_filter == "Last 7 Days":
            filtered_df = filtered_df.tail(7)
        elif time_filter == "Last 14 Days":
            filtered_df = filtered_df.tail(14)
        elif time_filter == "Last 30 Days":
            filtered_df = filtered_df.tail(30)

        # 4-Panel Health Trend Plot
        st.markdown("#### 1. Multi-Parameter Health Trends")
        fig_trends = plot_health_trends(filtered_df, user_goals)
        st.pyplot(fig_trends, use_container_width=True)

        st.markdown("---")

        # Correlation & Distribution Analysis
        st.markdown("#### 2. Activity Correlation & Sleep Distribution Analysis")
        fig_corr = plot_correlations(filtered_df)
        st.pyplot(fig_corr, use_container_width=True)


# ==========================================
# TAB 4: DAILY & WEEKLY REPORTS
# ==========================================
with tab_reports:
    st.subheader("📋 Daily Reports & Weekly Summaries")
    st.markdown("Detailed breakdown of weekly aggregated trends and deep-dive daily evaluations.")

    if df.empty:
        st.info("No data available. Add daily entries or load demo data to view reports.")
    else:
        rep_tab1, rep_tab2 = st.tabs(["📅 Weekly Summaries", "🔍 Detailed Daily Report"])

        # SUB-TAB 1: WEEKLY SUMMARIES
        with rep_tab1:
            weekly_df = generate_weekly_summary_dataframe(df)
            if not weekly_df.empty:
                st.markdown("#### Weekly Aggregate Performance")
                fig_weekly = plot_weekly_breakdown_bars(weekly_df, user_goals)
                st.pyplot(fig_weekly, use_container_width=True)

                st.markdown("#### Weekly Data Table")
                formatted_weekly = weekly_df.copy()
                formatted_weekly['date'] = pd.to_datetime(formatted_weekly['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(
                    formatted_weekly[[
                        'week_label', 'days_logged', 'total_steps', 'avg_steps',
                        'total_calories', 'avg_calories', 'avg_sleep', 'total_water', 'avg_water'
                    ]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Not enough data to calculate weekly summaries.")

        # SUB-TAB 2: DAILY REPORT
        with rep_tab2:
            st.markdown("#### Single Day Evaluation")
            sorted_dates = df['date'].dt.strftime('%Y-%m-%d').tolist()[::-1]
            selected_date_str = st.selectbox("Select Date to View Daily Report", options=sorted_dates)

            day_entry = df[df['date'].dt.strftime('%Y-%m-%d') == selected_date_str]
            if not day_entry.empty:
                row = day_entry.iloc[0]
                day_score = calculate_health_score(
                    row['steps'], row['calories'], row['sleep_hours'], row['water_liters'], user_goals
                )

                st.markdown(
                    f"""
                    <div style='background: #f8fafc; border-left: 5px solid {day_score['color']}; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;'>
                        <h3 style='margin: 0; color: #0f172a;'>Report for {pd.to_datetime(row['date']).strftime('%A, %B %d, %Y')}</h3>
                        <p style='margin: 0.2rem 0 0 0; color: #475569;'>
                            Daily Health Score: <b style='color: {day_score['color']}; font-size: 1.2rem;'>{day_score['score']}/100 ({day_score['category']})</b> |
                            Mood: <b>{row.get('mood', 'N/A')}</b> |
                            Heart Rate: <b>{row.get('resting_heart_rate', 'N/A')} bpm</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Gauge / Bar chart of goal completion
                fig_gauge = plot_single_day_gauge(row, user_goals)
                st.pyplot(fig_gauge, use_container_width=True)

                # Daily Detail Cards
                c_d1, c_d2, c_d3, c_d4 = st.columns(4)
                c_d1.metric("Steps", f"{int(row['steps']):,}", f"{int(row['steps'] - user_goals['steps']):,} vs target")
                c_d2.metric("Calories", f"{int(row['calories']):,} kcal", f"{int(row['calories'] - user_goals['calories']):,} vs target")
                c_d3.metric("Sleep", f"{row['sleep_hours']:.1f} hrs", f"{round(row['sleep_hours'] - user_goals['sleep_hours'], 1)} hrs vs target")
                c_d4.metric("Water", f"{row['water_liters']:.2f} L", f"{round(row['water_liters'] - user_goals['water_liters'], 2)} L vs target")

                if row.get('notes'):
                    st.info(f"📝 **Notes logged for this day:** {row['notes']}")

                # Delete entry option
                if st.button("🗑️ Delete this day's entry", type="secondary"):
                    delete_entry_by_date(selected_date_str)
                    st.warning(f"Deleted entry for {selected_date_str}.")
                    st.rerun()


# ==========================================
# TAB 5: HEALTH INSIGHTS & RECOMMENDATIONS
# ==========================================
with tab_insights:
    st.subheader("💡 Health Insights & Automated Recommendations")
    st.markdown(
        "Our analytical engine evaluates your 7-day activity, sleep, and hydration patterns "
        "to deliver personalized, evidence-based recommendations."
    )

    if df.empty:
        st.info("Log health data or load demo data to unlock personalized recommendations.")
    else:
        recommendations = generate_health_recommendations(df, user_goals)

        badge_colors = {
            "success": "#16a34a",
            "warning": "#d97706",
            "danger": "#dc2626",
            "info": "#2563eb"
        }

        for rec in recommendations:
            cat_color = badge_colors.get(rec.get("status", "info"), "#2563eb")
            st.markdown(
                f"""
                <div style='background: white; border: 1px solid #e2e8f0; border-left: 6px solid {cat_color}; border-radius: 8px; padding: 1.1rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;'>
                        <span style='font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: {cat_color}; letter-spacing: 0.5px;'>{rec['category']}</span>
                    </div>
                    <h4 style='margin: 0 0 0.4rem 0; color: #0f172a; font-size: 1.1rem;'>{rec['title']}</h4>
                    <p style='margin: 0 0 0.6rem 0; color: #475569; font-size: 0.95rem; line-height: 1.5;'>{rec['message']}</p>
                    <div style='background: #f8fafc; padding: 0.6rem 0.8rem; border-radius: 6px; font-size: 0.9rem; color: #1e293b; border-left: 3px solid #94a3b8;'>
                        <b>💡 Actionable Recommendation:</b> {rec['action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown("#### 🌟 Core Principles for Healthy Habit Maintenance")
        st.markdown(
            """
            1. **Consistent Sleep Schedule:** Going to sleep and waking up at consistent hours supports hormonal balance and metabolism.
            2. **Daily Micro-Movements:** Breaking up sedentary desk hours with 5-minute walks improves glycemic control and mental alertness.
            3. **Preemptive Hydration:** Drink water steadily throughout the day rather than waiting for feelings of intense thirst.
            4. **Progress Over Perfection:** Consistent 80% goal attainment yields sustainable long-term health improvements.
            """
        )
