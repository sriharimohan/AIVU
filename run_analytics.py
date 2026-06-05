from operator import index
import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fpl_analytics.db")

conn = sqlite3.connect(DB_PATH)

query = """
SELECT 
    p.FullName,
    f.Gameweek,
    f.TotalPoints AS CurrentWeekPoints,
    SUM(f.TotalPoints) OVER (PARTITION BY f.PlayerID ORDER BY f.Gameweek) AS CumulativePoints,
    LAG(f.TotalPoints, 1) OVER (PARTITION BY f.PlayerID ORDER BY f.Gameweek) AS PreviousWeekPoints
FROM fact_player_gameweek_performance f
JOIN dim_players p ON f.PlayerID = p.PlayerID;
"""

df =  pd.read_sql_query(query, conn)
conn.close()

df['PreviousWeekPoints'] = df['PreviousWeekPoints'].fillna(0)

df['ValueMetric'] = df['CumulativePoints'] / (df['CurrentWeekPoints'] + 1)

print("n/--- CLEANED DATA FRAME FOR MACHINE LEARNING  READY ---")
print(df.to_string(index=False))




from sklearn.linear_model import LinearRegression

X = df[['PreviousWeekPoints', 'ValueMetric']]
y = df['CurrentWeekPoints']

model = LinearRegression()
model.fit(X, y)

print(f"Feature Weights (Coefficients): {model.coef_}")
print(f"Baseline Starting Value (Intercept): {model.intercept_}")

mock_player_features = [[10.0, 2.5]]
predicted_score = model.predict(mock_player_features)
print(f"Predicted Score for Mock Player: {predicted_score[0]}")