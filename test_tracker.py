"""
test_tracker.py - Automated test suite verifying the database, data manager,
analytics, recommendations, and visualization pipeline.
"""

import os
import unittest
import pandas as pd
import matplotlib.pyplot as plt

from database import (
    init_db,
    save_health_entry,
    get_all_entries,
    get_entry_by_date,
    delete_entry_by_date,
    bulk_insert_entries,
    reset_database
)
from data_manager import validate_health_entry, export_to_csv
from analytics import calculate_health_score, calculate_overall_metrics, generate_weekly_summary_dataframe, DEFAULT_GOALS
from recommendations import generate_health_recommendations
from visualizer import plot_health_trends, plot_weekly_breakdown_bars, plot_correlations, plot_single_day_gauge
from sample_data import generate_sample_health_records

TEST_DB = os.path.join(os.path.dirname(__file__), "test_health_tracker.db")


class TestHealthTracker(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except Exception:
                pass

    def test_database_crud(self):
        # 1. Save entry
        saved = save_health_entry(
            date="2026-10-01",
            steps=10500,
            calories=2300.0,
            sleep_hours=7.5,
            water_liters=2.8,
            resting_heart_rate=65,
            mood="Energetic",
            notes="Morning run",
            db_path=TEST_DB
        )
        self.assertTrue(saved)

        # 2. Get entry by date
        entry = get_entry_by_date("2026-10-01", db_path=TEST_DB)
        self.assertIsNotNone(entry)
        self.assertEqual(entry['steps'], 10500)
        self.assertEqual(entry['calories'], 2300.0)

        # 3. Upsert entry (update same date)
        save_health_entry(
            date="2026-10-01",
            steps=12000,
            calories=2450.0,
            sleep_hours=8.0,
            water_liters=3.0,
            db_path=TEST_DB
        )
        updated = get_entry_by_date("2026-10-01", db_path=TEST_DB)
        self.assertEqual(updated['steps'], 12000)

        # 4. Get all entries dataframe
        df = get_all_entries(db_path=TEST_DB)
        self.assertEqual(len(df), 1)

        # 5. Delete entry
        deleted = delete_entry_by_date("2026-10-01", db_path=TEST_DB)
        self.assertTrue(deleted)
        self.assertIsNone(get_entry_by_date("2026-10-01", db_path=TEST_DB))

    def test_sample_data_and_analytics(self):
        records = generate_sample_health_records(days=14)
        self.assertEqual(len(records), 14)

        count = bulk_insert_entries(records, db_path=TEST_DB)
        self.assertEqual(count, 14)

        df = get_all_entries(db_path=TEST_DB)
        self.assertEqual(len(df), 14)

        # Test metrics
        metrics = calculate_overall_metrics(df, DEFAULT_GOALS)
        self.assertEqual(metrics['total_days'], 14)
        self.assertGreater(metrics['total_steps'], 50000)
        self.assertIn('latest_score', metrics)

        # Test weekly dataframe
        weekly_df = generate_weekly_summary_dataframe(df)
        self.assertFalse(weekly_df.empty)

        # Test recommendations
        recs = generate_health_recommendations(df, DEFAULT_GOALS)
        self.assertGreater(len(recs), 0)

    def test_validation(self):
        # Valid
        ok, msg = validate_health_entry("2026-10-01", 10000, 2000, 8.0, 2.5)
        self.assertTrue(ok)

        # Invalid steps
        ok, msg = validate_health_entry("2026-10-01", -50, 2000, 8.0, 2.5)
        self.assertFalse(ok)

        # Invalid sleep
        ok, msg = validate_health_entry("2026-10-01", 5000, 2000, 25.0, 2.5)
        self.assertFalse(ok)

    def test_health_scoring(self):
        score_good = calculate_health_score(10000, 2200, 8.0, 2.5, DEFAULT_GOALS)
        self.assertGreaterEqual(score_good['score'], 90)
        self.assertEqual(score_good['category'], "Excellent")

        score_low = calculate_health_score(2000, 1000, 4.0, 0.8, DEFAULT_GOALS)
        self.assertLess(score_low['score'], 55)

    def test_visualizer_figures(self):
        records = generate_sample_health_records(days=7)
        bulk_insert_entries(records, db_path=TEST_DB)
        df = get_all_entries(db_path=TEST_DB)

        # Trends figure
        fig1 = plot_health_trends(df, DEFAULT_GOALS)
        self.assertIsInstance(fig1, plt.Figure)
        plt.close(fig1)

        # Weekly breakdown
        weekly_df = generate_weekly_summary_dataframe(df)
        fig2 = plot_weekly_breakdown_bars(weekly_df, DEFAULT_GOALS)
        self.assertIsInstance(fig2, plt.Figure)
        plt.close(fig2)

        # Correlations
        fig3 = plot_correlations(df)
        self.assertIsInstance(fig3, plt.Figure)
        plt.close(fig3)

        # Single day gauge
        fig4 = plot_single_day_gauge(df.iloc[0], DEFAULT_GOALS)
        self.assertIsInstance(fig4, plt.Figure)
        plt.close(fig4)


if __name__ == '__main__':
    unittest.main()
