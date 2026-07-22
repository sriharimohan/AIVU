import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fpl_analytics.db")

# Connect using the absolute, locked-in path
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Database initialized successfully!")

# 3. Create the Dimension Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_players (
    PlayerID INTEGER PRIMARY KEY,
    FullName TEXT NOT NULL,
    CurrentPrice REAL NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dim_teams (
    TeamID INTEGER PRIMARY KEY,
    TeamName TEXT NOT NULL,
    TeamAbbreviation TEXT NOT NULL
);
""")

# 4. Create the Central Fact Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS fact_player_gameweek_performance (
    PerformanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    PlayerID INTEGER,
    TeamID INTEGER,
    Gameweek INTEGER NOT NULL,
    MinutesPlayed INTEGER NOT NULL,
    GoalsScored INTEGER DEFAULT 0,
    Assists INTEGER DEFAULT 0,
    ExpectedGoals REAL,
    ExpectedAssists REAL,
    TotalPoints INTEGER NOT NULL,
    FOREIGN KEY (PlayerID) REFERENCES dim_players(PlayerID),
    FOREIGN KEY (TeamID) REFERENCES dim_teams(TeamID),
    UNIQUE(PlayerID, Gameweek)
);
""")

# Commit changes and close connection
conn.commit()
conn.close()
print("Star Schema tables created perfectly with zero installation!")