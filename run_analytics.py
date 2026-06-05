import sqlite3
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# --- STEP 1: DYNAMIC PATH AND DATA INGESTION ---
# Automatically resolve paths to avoid Windows directory drift
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fpl_analytics.db")

conn = sqlite3.connect(DB_PATH)

# Expanded SQL Query to select underlying advanced performance metrics
query = """
SELECT 
    p.FullName,
    f.Gameweek,
    f.TotalPoints AS CurrentWeekPoints,
    f.ExpectedGoals,
    f.ExpectedAssists,
    LAG(f.TotalPoints, 1) OVER (PARTITION BY f.PlayerID ORDER BY f.Gameweek) AS PreviousWeekPoints
FROM fact_player_gameweek_performance f
JOIN dim_players p ON f.PlayerID = p.PlayerID;
"""
df = pd.read_sql_query(query, conn)
conn.close()

# --- STEP 2: PANDAS DATA CLEANING ---
# Handle the missing lag value anomaly for Gameweek 1 records
df['PreviousWeekPoints'] = df['PreviousWeekPoints'].fillna(0)

# --- STEP 3: ADVANCED MACHINE LEARNING MATRIX ---
print("\n--- EXPANDED DATA SCIENCE FEATURE MATRIX ---")
print(df.to_string(index=False))

# Define our expanded multi-feature matrix (X) and our target output (y)
X = df[['PreviousWeekPoints', 'ExpectedGoals', 'ExpectedAssists']]
y = df['CurrentWeekPoints']

# Split data into 80% Training and 20% Evaluation testing splits
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate against real unseen validation sets
y_pred = model.predict(X_test)
error_rate = mean_absolute_error(y_test, y_pred)

print("\n--- MODEL PERFORMANCE METRICS ---")
print(f"Mean Absolute Error (MAE): {error_rate:.4f} points")
print(f"Learned Weights (PrevPoints, xG, xA): {model.coef_}")

# Test predict a custom player profile: 5 points last week, 0.85 xG, 0.45 xA
mock_features = [[5.0, 0.85, 0.45]]
prediction = model.predict(mock_features)
print(f"AI Prediction for target player: {prediction[0]:.2f} points next week")