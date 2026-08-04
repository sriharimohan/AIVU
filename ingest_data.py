import sqlite3
import os
import pandas as pd
import numpy as np
from statsbombpy import sb

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "aivu_analytics.db")

def ingest_data():
    print("🌐 Connecting to StatsBomb Open Data API...")
    
    # Competition ID 43 = FIFA World Cup, Season ID 106 = 2022 Tournament
    comp_id = 43
    season_id = 106
    
    matches = sb.matches(competition_id=comp_id, season_id=season_id)
    print(f"🏆 Found {len(matches)} real 2022 World Cup matches!")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Reset schema for clean ingestion
    cursor.execute("DROP TABLE IF EXISTS match_performance;")
    cursor.execute("DROP TABLE IF EXISTS players;")
    
    cursor.execute("""
    CREATE TABLE players (
        player_id INTEGER PRIMARY KEY,
        player_name TEXT NOT NULL,
        position TEXT NOT NULL,
        current_club TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE match_performance (
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
    
    target_matches = matches['match_id'].tolist()
    
    player_dict = {}
    performance_records = []
    
    print("⏳ Parsing event streams for spatial shot vectors and xG metrics...")
    
    gameweek_counter = 1
    for match_id in target_matches:
        try:
            events = sb.events(match_id=match_id)
            shots = events[events['type'] == 'Shot'].copy()
            
            for _, shot in shots.iterrows():
                p_id = shot.get('player_id')
                p_name = shot.get('player')
                team_name = shot.get('team')
                position = shot.get('position', 'Forward')
                
                if pd.isna(p_id) or pd.isna(p_name):
                    continue
                
                p_id = int(p_id)
                if p_id not in player_dict:
                    player_dict[p_id] = (p_id, str(p_name), str(position), str(team_name))
                
                xg = float(shot['shot_statsbomb_xg']) if 'shot_statsbomb_xg' in shot and not pd.isna(shot['shot_statsbomb_xg']) else 0.05
                loc = shot.get('location')
                shot_x = float(loc[0]) if isinstance(loc, list) and len(loc) >= 2 else 105.0
                shot_y = float(loc[1]) if isinstance(loc, list) and len(loc) >= 2 else 34.0
                
                outcome = shot.get('shot_outcome')
                was_goal = 1 if outcome == 'Goal' else 0
                actual_pts = 6 if was_goal else 2
                
                performance_records.append((
                    None, p_id, gameweek_counter, round(xg, 2), 0.10, 90, actual_pts, shot_x, shot_y, was_goal
                ))
            
            gameweek_counter += 1
        except Exception as e:
            print(f"⚠️ Skipped match {match_id}: {e}")
            continue

    cursor.executemany("INSERT OR IGNORE INTO players VALUES (?, ?, ?, ?);", list(player_dict.values()))
    print(f"✅ Ingested {len(player_dict)} real player dimension records!")

    cursor.executemany("INSERT INTO match_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", performance_records)
    print(f"✅ Ingested {len(performance_records)} real spatial performance logs!")

    conn.commit()
    conn.close()
    print("🏁 2022 World Cup ingestion pipeline complete!")

if __name__ == "__main__":
    ingest_data()