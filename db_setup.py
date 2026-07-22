import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "aivu_analytics.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY,
        player_name TEXT NOT NULL,
        position TEXT NOT NULL,
        current_club TEXT NOT NULL
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_performance (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        gameweek INTEGER NOT NULL,
        expected_goals REAL DEFAULT 0.0,
        expected_assists REAL DEFAULT 0.0,
        minutes_played INTEGER NOT NULL,
        actual_points INTEGER NOT NULL,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    );
''')

conn.commit()
conn.close()

print(f"✅ Database setup completed successfully!")
print(f"📍 Database path resolved to: {DB_PATH}")