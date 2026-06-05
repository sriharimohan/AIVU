import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fpl_analytics.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# 2. INSERT THE MISSING TEAM LOOKUP DATA FIRST (Dimension Data)
teams_data = [
    (1, "Chelsea", "CHE"),
    (2, "Arsenal", "ARS"),
    (3, "Manchester City", "MCI")
]

cursor.executemany("""
    INSERT OR IGNORE INTO dim_teams (TeamID, TeamName, TeamAbbreviation)
    VALUES (?, ?, ?);
""", teams_data)

# 3. Insert Core Player Lookup Records (Dimension Data)
players_data = [
    (122, "Cole Palmer", 10.5),
    (305, "Bukayo Saka", 10.0),
    (184, "Erling Haaland", 15.0)
]

cursor.executemany("""
    INSERT OR IGNORE INTO dim_players (PlayerID, FullName, CurrentPrice)
    VALUES (?, ?, ?);
""", players_data)

# 4. Insert Mock Multi-Gameweek Performance Records (Fact Data)
performance_data = [
    # PlayerID, TeamID, Gameweek, Minutes, Goals, Assists, xG, xA, TotalPoints
    (122, 1, 1, 90, 1, 0, 0.65, 0.15, 8),
    (122, 1, 2, 85, 0, 2, 0.12, 0.85, 9),
    (122, 1, 3, 90, 2, 1, 1.10, 0.40, 16),
    
    (305, 2, 1, 90, 0, 1, 0.25, 0.45, 5),
    (305, 2, 2, 90, 1, 0, 0.55, 0.10, 7),
    (305, 2, 3, 75, 0, 0, 0.10, 0.05, 2),
    
    (184, 3, 1, 90, 3, 0, 1.85, 0.00, 17),
    (184, 3, 2, 90, 1, 0, 0.95, 0.10, 6),
    (184, 3, 3, 90, 0, 0, 0.40, 0.00, 2)
]

cursor.executemany("""
    INSERT OR IGNORE INTO fact_player_gameweek_performance 
    (PlayerID, TeamID, Gameweek, MinutesPlayed, GoalsScored, Assists, ExpectedGoals, ExpectedAssists, TotalPoints)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
""", performance_data)

# 5. Safely write transaction changes to disk and close connection pipe
conn.commit()
conn.close()

print("Database populated with dimension and historical fact data successfully!")