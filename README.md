# Personal Health Tracker Application

A complete, interactive health tracking and analytics system developed based on the project abstract:
> **"Personal Health Tracker Application"**  
> *Developed to monitor and analyze daily health activities efficiently. Helps users maintain a healthy lifestyle by tracking essential health parameters: steps walked, calories burned, sleep duration, and water intake. Built with Python, Pandas, Matplotlib, and Streamlit.*

---

## 🌟 Key Features

### 1. ✍️ Daily Health Activity Logging (Frontend)
- **Interactive Web Interface:** Built using Streamlit for an intuitive, responsive user experience.
- **Core Parameters Tracked:**
  - 🚶 **Steps Walked:** Input pedometer / smartwatch counts.
  - 🔥 **Calories Burned (kcal):** Active energy expenditure + basal metabolic burn.
  - 😴 **Sleep Duration (hours):** Nightly sleep tracking with optimal zone indicators.
  - 💧 **Water Intake (liters):** Hydration monitoring with real-time glass equivalents.
  - 💓 **Optional Parameters:** Resting heart rate (bpm), daily mood/energy, and workout activity notes.
- **Input Validation:** Strict bounds checking to ensure physiological sanity and prevent invalid data entry.

### 2. 🗄️ Backend Data Management & REST API (SQLite, Pandas & FastAPI)
- **Persistent Storage:** SQLite database (`health_tracker.db`) with automatic indexing, schema constraints, and atomic upsert operations.
- **REST API Endpoints ([`api.py`](api.py)):** Built with FastAPI and Swagger UI documentation (`/docs`) offering endpoints for records, metrics, weekly summaries, and recommendations.
- **Data Manager:** Preprocessing layer handling data cleansing, CSV import/export, and schema validation.
- **Batch Data Operations:** One-click demo data generation (30 days of realistic synthetic records) for instant evaluation.

### 3. 📊 Analytics Engine (Pandas)
- **Composite Health Score (0–100):** Scientific weighted scoring algorithm evaluating steps (30%), sleep quality (30%), hydration (20%), and calories (20%).
- **Rolling Averages:** 7-day and 30-day moving averages with week-over-week performance comparisons.
- **Consistency Streaks:** Automatic tracking of consecutive days meeting step and hydration targets.
- **Aggregate Records:** All-time records for steps, calories, and total activity volume.

### 4. 📈 Graphical Visualization (Matplotlib)
- **Multi-Parameter Trend Plot:** 4-panel synchronized time-series visualization showing daily steps, calories, sleep, and water intake plotted alongside customizable personal targets.
- **Weekly Performance Comparison:** Grouped dual-axis bar charts comparing weekly step volumes and sleep patterns.
- **Correlation & Distribution Analysis:** Scatter plots with linear regression fit (Steps vs. Calories) and sleep duration distribution histograms.
- **Daily Target Achievement Gauges:** Normalized horizontal bar breakdown showing percentage of daily goals achieved.

### 5. 💡 Health Insights & Recommendation Dashboard
- Evaluates recent activity, sleep debt, and hydration trends against evidence-based benchmarks (e.g. WHO physical activity recommendations and National Sleep Foundation guidelines).
- Categorized actionable feedback:
  - 🛌 **Sleep Health:** Identifies sleep deficits (<6.5h) or erratic sleep schedules.
  - 👟 **Physical Activity:** Flags sedentary days and rewards step milestones.
  - 🥤 **Hydration:** Recommends fluid intake pacing.
  - 🔥 **Caloric Burn:** Analyzes metabolic expenditure against daily goals.

---

## 📂 Project Architecture

```
health_tracker/
├── app.py                  # Main Streamlit frontend & application orchestration
├── database.py             # SQLite backend persistence layer (CRUD, upserts, indexing)
├── data_manager.py         # Data validation, Pandas preprocessing, CSV import/export
├── analytics.py            # Analytics engine (KPIs, weekly aggregation, health scoring, streaks)
├── recommendations.py      # Health insights and evidence-based recommendation engine
├── visualizer.py           # Matplotlib visualization suite (Trends, Correlations, Bars, Gauges)
├── sample_data.py          # Realistic 30-day demo data generator
├── test_tracker.py         # Automated unit & integration test suite (100% passing)
├── requirements.txt        # Project dependencies
└── README.md               # Complete project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Applications

#### Option A: Run Full-Stack Web Frontend (Streamlit)
```bash
streamlit run app.py
```
Streamlit will automatically open your default browser at `http://localhost:8501`.

#### Option B: Run Standalone REST API Backend (FastAPI)
```bash
uvicorn api:app --reload --port 8000
```
Interactive Swagger API documentation will be available at `http://localhost:8000/docs`.

---

## 🌐 Deploying to Streamlit Community Cloud (Free Deployment)

1. Push this repository to your GitHub account (make sure it's public).
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"** / **"Create app"**.
4. Select your repository (`personal-health-tracker`), branch (`main`), and set the main file path to `app.py`.
5. Click **"Deploy!"**.
6. In ~60 seconds, your application will be live at a public URL (e.g. `https://<your-app-name>.streamlit.app`).

### 4. Running the Test Suite
To verify all backend, analytics, and visualization modules:
```bash
python -m unittest test_tracker.py
```

---

## 📝 Usage Guide
1. **Load Sample Data (Optional):** On first run, open the sidebar and click **"Load Demo Data"** to immediately populate 30 days of realistic health data.
2. **Customize Your Goals:** In the sidebar, set your personal targets for steps, calories, sleep, and water intake.
3. **Log Today's Activity:** Head to the **Log Daily Data** tab, enter your metrics, and click **Save Daily Health Record**.
4. **Inspect Insights & Trends:** Switch between the **Dashboard Overview**, **Visual Trends & Charts**, **Daily & Weekly Reports**, and **Health Insights & Tips** tabs to monitor your wellness progress!
