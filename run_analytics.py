import os
import pickle
import sqlite3
import numpy as np
import pandas as pd

# 1. Connect to Database & Run SQL Query with LAG Window Function
DB_PATH = "aivu_analytics.db"

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"Database file '{DB_PATH}' not found.")

conn = sqlite3.connect(DB_PATH)

sql_query = """
SELECT 
    m.player_id,
    p.player_name,
    p.position,
    m.gameweek,
    m.expected_goals,
    m.expected_assists,
    m.minutes_played,
    m.actual_points,
    m.shot_x,
    m.shot_y,
    m.was_goal,
    LAG(m.actual_points, 1) OVER (
        PARTITION BY m.player_id 
        ORDER BY m.gameweek
    ) AS previous_week_points
FROM match_performance m
JOIN players p ON m.player_id = p.player_id;
"""

df = pd.read_sql_query(sql_query, conn)
conn.close()

# 2. Handle missing values
df["previous_week_points"] = df["previous_week_points"].fillna(0)

feature_cols = ["expected_goals", "expected_assists", "minutes_played", "previous_week_points"]
for col in feature_cols:
    df[col] = df[col].fillna(0.0)

print(f"✅ Successfully loaded {len(df)} performance records from SQL database.")

# 3. Closed-Form OLS Engine (Matrix Math)
def train_ridge_ols(X, y, l2_penalty=0.01):
    bias = np.ones((X.shape[0], 1))
    X_design = np.hstack([bias, X])
    
    n_features = X_design.shape[1]
    I = np.eye(n_features)
    I[0, 0] = 0.0  # Don't penalize bias term
    
    XT_X = np.dot(X_design.T, X_design)
    penalty_term = l2_penalty * I
    XT_y = np.dot(X_design.T, y)
    
    weights = np.linalg.solve(XT_X + penalty_term, XT_y)
    return weights

X_data = df[feature_cols].values
y_data = df["actual_points"].values

beta_weights = train_ridge_ols(X_data, y_data, l2_penalty=0.1)

print("\n--- Model Training Completed ---")
print(f"Intercept (Bias): {beta_weights[0]:.4f}")
for col, w in zip(feature_cols, beta_weights[1:]):
    print(f"Weight for '{col}': {w:.4f}")

# 4. Save Artifact for App
os.makedirs("models", exist_ok=True)
pipeline_artifact = {
    "weights": beta_weights,
    "feature_names": feature_cols,
    "sample_data": df
}

artifact_path = os.path.join("models", "aivu_pipeline.pkl")
with open(artifact_path, "wb") as f:
    pickle.dump(pipeline_artifact, f)

print(f"\n✅ Saved pipeline artifact to '{artifact_path}'. Ready for app.py!")