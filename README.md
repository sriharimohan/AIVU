# ⚽ AIVU: Predictive Football Analytics Engine & Decision Support System

AIVU (derived from the Tamil word **ஆய்வு**, meaning systematic research or deep analysis) is an open-source predictive data pipeline and decision-support engine. Built outside of my formal academic curriculum, this platform is designed to strip luck and variance out of professional football statistics, translating messy historical match logs into forward-looking, actionable performance projections.

Traditional baseline analytics look blindly at past point totals or final scores. AIVU addresses this flaw by evaluating underlying threat vectors—specifically Expected Goals (xG) and Expected Assists (xA)—and blending them programmatically with dynamic player momentum. This helps users spot emerging form streaks and make highly optimized, data-backed selections for match forecasting and fantasy sports.

---

## 🛠️ Tech Stack & Key Architectures

- **Core Engine:** Python (Programming Language)
- **Database Architecture:** SQLite, Relational Star Schema Design
- **Advanced Querying:** SQL Window Functions (`OVER`, `PARTITION BY`, `LAG`)
- **Machine Learning Layer:** Scikit-Learn (Linear Regression, Train-Test Split validation)
- **Environment Safety:** Native Python `os` library for absolute path portability

---

## 🏗️ System Architecture & Data Pipeline

AIVU is structured using a strict **Goal ➔ Logic ➔ Tool** framework to ensure production-grade software hygiene:

### 1. Relational Pipeline Ingestion (ETL)
The pipeline ingests raw, granular gameweek records and structures them into a clean relational **Star Schema** within an SQLite database. This isolates player dimension attributes from individual match performance fact logs, ensuring clean relational data integrity.

### 2. Analytical Momentum Generation (Advanced SQL Window Functions)
To measure true, evolving player form rather than lagging season averages, the database layer calculates a rolling momentum matrix. Using advanced SQL window functions combined with moving aggregation frames, the system evaluates dynamic rolling performance vectors:

```sql
SELECT 
    p.FullName,
    f.Gameweek,
    f.TotalPoints AS CurrentWeekPoints,
    LAG(f.TotalPoints, 1) OVER (PARTITION BY f.PlayerID ORDER BY f.Gameweek) AS PreviousWeekPoints,
    
    -- 3-Week Sliding Aggregation Window
    AVG(f.TotalPoints) OVER (
        PARTITION BY f.PlayerID 
        ORDER BY f.Gameweek 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS RollingFormAverage
FROM fact_player_gameweek_performance f
JOIN dim_players p ON f.PlayerID = p.PlayerID;
```

### 3. Machine Learning Feature Matrix & Validation
The calculated rolling form metrics are dynamically injected into a Scikit-Learn multi-feature regression matrix (X) alongside core performance threat vectors:

Input Features: ['PreviousWeekPoints', 'ExpectedGoals', 'ExpectedAssists', 'RollingFormAverage']

Target Variable: ['CurrentWeekPoints']

To prevent overfitting and guarantee real-world generalization capability, the data is passed through a strict 80/20 train-test validation split before evaluating baseline metrics like Mean Absolute Error (MAE).

### 4. Cross-Platform Execution Safety (os Path Decoupling)
To ensure the codebase can be instantly cloned and executed on any operating system (Windows, Mac, or Linux cloud servers) without configuration adjustments, all directory tracking is handled dynamically at runtime using Python's built-in os module:

Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fpl_analytics.db")

FullName,Gameweek,CurrentWeekPoints,ExpectedGoals,ExpectedAssists,PreviousWeekPoints
Cole Palmer,1,8,0.65,0.15,0.0
Cole Palmer,2,9,0.12,0.85,8.0
Cole Palmer,3,16,1.10,0.40,9.0
Erling Haaland,1,17,1.85,0.00,0.0
Erling Haaland,2,6,0.95,0.10,17.0
Erling Haaland,3,2,0.40,0.00,6.0
--- MODEL PERFORMANCE METRICS ---
Mean Absolute Error (MAE): 1.1163 points
Learned Weights (PrevPoints, xG, xA, RollingForm): [-0.1155, 9.7219, 11.6797, 4.3120]

🚀 Installation & Local Execution
Clone the repository:

Bash
git clone https://github.com/sriharimohan/AIVU.git
cd AIVU
Install required analytics dependencies:

Bash
pip install pandas scikit-learn
Run the dynamic pipeline engine:

Bash
python run_analytics.py