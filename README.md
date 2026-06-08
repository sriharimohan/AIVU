# ⚽ AIVU: Predictive Football Analytics Engine & Decision Support System

AIVU (derived from the Tamil word **ஆய்வு**, meaning systematic research or deep analysis) is an open-source predictive data pipeline and decision-support engine. Built outside of my formal academic curriculum, this platform is designed to strip luck and variance out of professional football statistics, translating messy historical match logs into forward-looking, actionable performance projections.

Traditional baseline analytics look blindly at past point totals or final scores. AIVU addresses this flaw by evaluating underlying threat vectors—specifically Expected Goals (xG) and Expected Assists (xA)—and blending them programmatically with dynamic player momentum. This helps users spot emerging form streaks and make highly optimized, data-backed selections for match forecasting and fantasy sports.

---

## 🛠️ Tech Stack & Key Architectures

- **Core Engine:** Python (Pandas, NumPy)
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
