"""
visualizer.py - Matplotlib graphical visualization engine for Personal Health Tracker.
Generates comprehensive multi-metric trend plots, weekly comparison charts,
correlation analysis, and daily goal progress visualizations.
"""

from typing import Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np

# Set clean aesthetic defaults
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8


def plot_health_trends(df: pd.DataFrame, goals: Dict[str, float]) -> plt.Figure:
    """
    Creates a 4-panel multi-metric trend visualization over time:
    - Steps walked with target threshold line
    - Calories burned with target line
    - Sleep duration with optimal 7-9 hr shaded healthy zone
    - Water intake with hydration goal line
    """
    if df.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.text(0.5, 0.5, "No data available to display trends.", ha='center', va='center', fontsize=14, color='#64748b')
        ax.axis('off')
        return fig

    plot_df = df.copy()
    plot_df['date'] = pd.to_datetime(plot_df['date'])
    plot_df = plot_df.sort_values(by='date')

    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    fig.patch.set_facecolor('#ffffff')

    dates = plot_df['date']

    # 1. STEPS SUBPLOT
    ax1 = axes[0]
    ax1.plot(dates, plot_df['steps'], marker='o', markersize=4, color='#2563eb', linewidth=2.2, label='Daily Steps')
    ax1.axhline(goals['steps'], color='#16a34a', linestyle='--', linewidth=1.5, label=f"Goal ({int(goals['steps']):,} steps)")
    ax1.fill_between(dates, plot_df['steps'], alpha=0.12, color='#2563eb')
    ax1.set_ylabel('Steps Walked', fontsize=11, fontweight='bold', color='#1e293b')
    ax1.set_title('Daily Health Parameters & Trends Over Time', fontsize=14, fontweight='bold', pad=12, color='#0f172a')
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0')

    # 2. CALORIES SUBPLOT
    ax2 = axes[1]
    ax2.plot(dates, plot_df['calories'], marker='s', markersize=4, color='#ea580c', linewidth=2.2, label='Calories Burned (kcal)')
    ax2.axhline(goals['calories'], color='#ca8a04', linestyle='--', linewidth=1.5, label=f"Goal ({int(goals['calories']):,} kcal)")
    ax2.fill_between(dates, plot_df['calories'], alpha=0.12, color='#ea580c')
    ax2.set_ylabel('Calories (kcal)', fontsize=11, fontweight='bold', color='#1e293b')
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left', frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0')

    # 3. SLEEP SUBPLOT
    ax3 = axes[2]
    ax3.plot(dates, plot_df['sleep_hours'], marker='^', markersize=4, color='#7c3aed', linewidth=2.2, label='Sleep Duration (hrs)')
    ax3.axhspan(7.0, 9.0, color='#22c55e', alpha=0.15, label='Recommended Optimal Range (7-9 hrs)')
    ax3.axhline(goals['sleep_hours'], color='#9333ea', linestyle='--', linewidth=1.4, label=f"Goal ({goals['sleep_hours']} hrs)")
    ax3.set_ylabel('Sleep (Hours)', fontsize=11, fontweight='bold', color='#1e293b')
    ax3.set_ylim(bottom=max(0, plot_df['sleep_hours'].min() - 1), top=min(24, max(10, plot_df['sleep_hours'].max() + 1)))
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.legend(loc='upper left', frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0')

    # 4. WATER SUBPLOT
    ax4 = axes[3]
    ax4.bar(dates, plot_df['water_liters'], width=0.6, color='#06b6d4', alpha=0.75, label='Water Intake (Liters)')
    ax4.axhline(goals['water_liters'], color='#0284c7', linestyle='--', linewidth=1.5, label=f"Goal ({goals['water_liters']:.1f} L)")
    ax4.set_ylabel('Water (Liters)', fontsize=11, fontweight='bold', color='#1e293b')
    ax4.set_xlabel('Date', fontsize=11, fontweight='bold', color='#1e293b')
    ax4.grid(True, linestyle=':', alpha=0.6)
    ax4.legend(loc='upper left', frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0')

    # Format Date Axis
    ax4.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=12))
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate(rotation=30, ha='right')

    plt.tight_layout()
    return fig


def plot_weekly_breakdown_bars(weekly_df: pd.DataFrame, goals: Dict[str, float]) -> plt.Figure:
    """
    Creates a grouped bar chart visualizing weekly total steps and weekly average sleep.
    """
    if weekly_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No weekly data available yet.", ha='center', va='center', fontsize=13)
        ax.axis('off')
        return fig

    # Reverse to plot chronologically from left to right
    data = weekly_df.iloc[::-1].copy().reset_index(drop=True)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#ffffff')

    x_labels = [d.strftime('%b %d') for d in pd.to_datetime(data['date'])]
    x = np.arange(len(x_labels))
    bar_width = 0.38

    # Primary axis: Average Daily Steps for the week
    bars1 = ax1.bar(x - bar_width/2, data['avg_steps'], width=bar_width, color='#3b82f6', label='Weekly Avg Steps/Day')
    ax1.axhline(goals['steps'], color='#1d4ed8', linestyle=':', linewidth=1.4, label='Daily Step Goal')
    ax1.set_ylabel('Average Daily Steps', color='#1e3a8a', fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#1e3a8a')
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    # Secondary axis: Average Sleep (hours)
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + bar_width/2, data['avg_sleep'], width=bar_width, color='#10b981', label='Weekly Avg Sleep/Day (hrs)')
    ax2.axhline(goals['sleep_hours'], color='#047857', linestyle='--', linewidth=1.4, label='Sleep Goal')
    ax2.set_ylabel('Average Sleep (Hours)', color='#064e3b', fontsize=11, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#064e3b')
    ax2.set_ylim(0, 12)

    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels, rotation=25, ha='right', fontsize=10)
    ax1.set_title('Weekly Performance Summary (Steps vs. Sleep)', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, linestyle=':', alpha=0.4)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1')

    plt.tight_layout()
    return fig


def plot_correlations(df: pd.DataFrame) -> plt.Figure:
    """
    Creates a 2-panel chart showing:
    1. Steps vs Calories scatter with linear regression fit
    2. Sleep hours vs Daily Health Score
    """
    if len(df) < 2:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.text(0.5, 0.5, "At least 2 days of data are needed for correlation analysis.", ha='center', va='center', fontsize=13)
        ax.axis('off')
        return fig

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
    fig.patch.set_facecolor('#ffffff')

    # 1. Steps vs Calories
    x = df['steps'].values
    y = df['calories'].values
    ax1.scatter(x, y, color='#2563eb', alpha=0.7, edgecolors='black', linewidth=0.5, s=60)
    if len(df) >= 3 and np.std(x) > 0:
        poly_coeff = np.polyfit(x, y, 1)
        poly_fn = np.poly1d(poly_coeff)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax1.plot(x_line, poly_fn(x_line), color='#dc2626', linestyle='--', linewidth=2, label=f'Fit (m={poly_coeff[0]:.3f})')
        ax1.legend(loc='lower right')

    ax1.set_title('Steps Walked vs. Calories Burned', fontsize=12, fontweight='bold', pad=8)
    ax1.set_xlabel('Daily Steps', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Calories Burned (kcal)', fontsize=10, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)

    # 2. Sleep Hours Distribution Histogram
    ax2.hist(df['sleep_hours'], bins=8, color='#8b5cf6', edgecolor='white', alpha=0.85)
    ax2.axvline(df['sleep_hours'].mean(), color='#4c1d95', linestyle='--', linewidth=2, label=f"Mean: {df['sleep_hours'].mean():.1f}h")
    ax2.axvspan(7.0, 9.0, color='#10b981', alpha=0.15, label='Recommended (7-9h)')
    ax2.set_title('Sleep Duration Distribution', fontsize=12, fontweight='bold', pad=8)
    ax2.set_xlabel('Sleep Hours', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Frequency (Days)', fontsize=10, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='upper right')

    plt.tight_layout()
    return fig


def plot_single_day_gauge(row: pd.Series, goals: Dict[str, float]) -> plt.Figure:
    """
    Renders a clean horizontal achievement bar chart for a single daily report,
    showing percent of goal reached for each health parameter.
    """
    metrics = ['Steps Walked', 'Calories Burned', 'Sleep Duration', 'Water Intake']
    values = [
        min(150.0, (row['steps'] / max(1, goals['steps'])) * 100.0),
        min(150.0, (row['calories'] / max(1, goals['calories'])) * 100.0),
        min(150.0, (row['sleep_hours'] / max(0.1, goals['sleep_hours'])) * 100.0),
        min(150.0, (row['water_liters'] / max(0.1, goals['water_liters'])) * 100.0)
    ]

    colors = []
    for val in values:
        if val >= 100:
            colors.append('#10b981')  # Green (Goal met)
        elif val >= 75:
            colors.append('#3b82f6')  # Blue (Close)
        else:
            colors.append('#f59e0b')  # Amber (Needs improvement)

    fig, ax = plt.subplots(figsize=(9, 3.2))
    fig.patch.set_facecolor('#ffffff')

    y_pos = np.arange(len(metrics))
    bars = ax.barh(y_pos, values, color=colors, height=0.55, edgecolor='#475569', linewidth=0.5)
    ax.axvline(100.0, color='#dc2626', linestyle='--', linewidth=1.5, label='100% Daily Target')

    # Add data labels
    for bar, val in zip(bars, values):
        ax.text(val + 2, bar.get_y() + bar.get_height()/2, f"{val:.1f}%", va='center', ha='left', fontsize=9, fontweight='bold', color='#1e293b')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics, fontsize=10, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlim(0, 160)
    ax.set_xlabel('Goal Completion Percentage (%)', fontsize=10, fontweight='bold')
    ax.set_title(f"Target Achievement for {pd.to_datetime(row['date']).strftime('%B %d, %Y')}", fontsize=12, fontweight='bold', pad=8)
    ax.grid(True, linestyle=':', alpha=0.5, axis='x')
    ax.legend(loc='lower right', frameon=True)

    plt.tight_layout()
    return fig
