import sqlite3
import pandas as pd
import os

# 1. Dynamically locate the directory where this script runs
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "aivu_analytics.db")

def extract_rolling_momentum():
    # Establish connection with error safety
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.OperationalError as e:
        print(f"❌ Database connection failed. Ensure db_setup.py has run. Error: {e}")
        return pd.DataFrame()

    # Analytical Query utilizing SQL Window Functions for feature engineering
    query = """
    SELECT 
        player_id,
        gameweek,
        minutes_played,
        expected_goals,
        expected_assists,
        AVG(expected_goals) OVER (
            PARTITION BY player_id
            ORDER BY gameweek
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3wk_xG,
        AVG(expected_assists) OVER (
            PARTITION BY player_id
            ORDER BY gameweek
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3wk_xA,
        actual_points AS target_performance
    FROM match_performance
    WHERE minutes_played >= 45;
    """

    # Read analytical data directly into a pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

if __name__ == "__main__":
    print("=" * 60)
    print("📈 EXTRACTING FEATURE VECTORS FROM THE DATABASE...")
    print("=" * 60)
    
    features_df = extract_rolling_momentum()

    if not features_df.empty:
        # Display the formatted feature dataframe with proper alignment
        print(features_df.to_string(index=False))
        print("=" * 60)
        print(f"✅ Successfully engineered feature vectors for {len(features_df)} rows.")
    else:
        print("⚠️ No features extracted. Ensure you have populated the database first!")
    print("=" * 60)