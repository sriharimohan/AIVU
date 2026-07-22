import sqlite3
import os

# 1. Dynamically locate the directory where this script runs
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "aivu_analytics.db")

def populate_database():
    # Establish connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enforce database schema constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    print(f"🔄 Connected to database at: {DB_PATH}")
    print("🚀 Initiating database setup & data ingestion...")

    # -------------------------------------------------------------
    # 2. SCHEMA DEFINITION LAYER (Creates tables if missing)
    # -------------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY,
        player_name TEXT NOT NULL,
        position TEXT NOT NULL,
        current_club TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS match_performance (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        gameweek INTEGER,
        expected_goals REAL,
        expected_assists REAL,
        minutes_played INTEGER,
        actual_points INTEGER,
        shot_x REAL,
        shot_y REAL,
        was_goal INTEGER,
        FOREIGN KEY (player_id) REFERENCES players (player_id)
    );
    """)
    print("✅ Database schema verified and ready.")

    # -------------------------------------------------------------
    # 3. DATA INGESTION LAYER
    # -------------------------------------------------------------
    # Player profiles
    mock_players = [
        (1, 'Srihari', 'Midfielder', 'Chennaiyin FC'),
        (2, 'Jagdish', 'Striker', 'Bengaluru FC'),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO players VALUES (?, ?, ?, ?);
    """, mock_players)
    print(f"✅ Ingested {len(mock_players)} player dimension records.")

    # Match Performance Logs with Spatial Coordinates (shot_x, shot_y, was_goal)
    # Format: (performance_id, player_id, gameweek, xG, xA, mins, points, shot_x, shot_y, was_goal)
    mock_matches = [
        # Srihari (Player 1) Match Logs
        (None, 1, 1, 0.1, 0.0, 90, 2, 105.0, 38.0, 0),
        (None, 1, 2, 0.3, 0.1, 85, 5, 112.0, 41.0, 1),
        (None, 1, 3, 0.5, 0.2, 90, 8, 114.0, 36.0, 1),
        
        # Jagdish (Player 2) Match Logs
        (None, 2, 1, 0.2, 0.2, 90, 3, 98.0,  30.0, 0),
        (None, 2, 2, 0.5, 0.3, 90, 6, 108.0, 44.0, 1),
        (None, 2, 3, 0.4, 0.2, 80, 4, 102.0, 25.0, 0),
        (None, 2, 4, 0.6, 0.4, 90, 7, 115.0, 40.0, 1)
    ]
    
    # Insert performance metrics (matching 10 table columns)
    cursor.executemany("""
        INSERT INTO match_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, mock_matches)
    print(f"✅ Ingested {len(mock_matches)} performance transaction records.")

    # Commit transactions cleanly
    conn.commit()
    conn.close()
    print("🏁 Data ingestion transaction committed and connection closed cleanly.")

if __name__ == "__main__":
    populate_database()