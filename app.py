import streamlit as st
import sqlite3
import pandas as pd
import numpy as np  # Fixed: changed 'mp' to 'np'
import os
import joblib
import matplotlib.pyplot as plt  # Fixed: changed 'matplotlib as plt' to 'matplotlib.pyplot as plt'
from mplsoccer import VerticalPitch

# Environment setup
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "aivu_analytics.db")
MODEL_PATH = os.path.join(PROJECT_DIR, "aivu_pipeline.pkl")

# Browser configuration
st.set_page_config(
    page_title="AIVU | Sports Analytics & Predictive Engine",
    page_icon="⚽",
    layout="wide"
)

# Custom namespace for unpickling our matrix model
class AIVULinearRegression:
    def __init__(self):
        self.weights = None
        self.intercept = None
    def predict(self, X):
        return np.dot(X, self.weights) + self.intercept

# Helper function to query the database safely
def run_query(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except sqlite3.OperationalError as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

st.title("⚽ AIVU : Sports Analytics & Predictive Engine")
st.markdown("---")

# Sidebar configuration
st.sidebar.header("Model Configuration")
model_loaded = False
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        st.sidebar.success("Custom ML Engine Active")
        model_loaded = True
    except Exception as e:
        st.sidebar.error(f"Pipeline load failed: {e}")
else:
    st.sidebar.warning("Model pkl not found. Run predictive_model.py!")

st.subheader("System-Wide Ingestion Statistics")
# Fixed SQL syntax error (removed extra closing parenthesis and fixed table name spelling)
stats_df = run_query("""
    SELECT
        COUNT(DISTINCT player_id) as total_players,
        COUNT(*) as total_matches,
        SUM(actual_points) as total_points
    FROM match_performance
""")

if not stats_df.empty and stats_df['total_players'][0] > 0:
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Players Tracked", int(stats_df['total_players'][0]))
    col2.metric("Match Profiles Processed", int(stats_df['total_matches'][0]))
    col3.metric("Total FPL Points Evaluated", int(stats_df['total_points'][0]))                                                   
st.markdown("---")

st.subheader("Player Profiling & Performance Intelligence")
players_df = run_query("SELECT player_id, player_name, current_club, position FROM players")

if not players_df.empty:
    player_options = {row['player_name']: row['player_id'] for _, row in players_df.iterrows()}
    selected_player_name = st.selectbox("Select Player Profile:", list(player_options.keys()))
    selected_player_id = player_options[selected_player_name]  # Fixed: defined selected_player_id

    # Fixed: indented metadata and query execution to stay inside 'if not players_df.empty' block
    meta = players_df[players_df['player_id'] == selected_player_id].iloc[0]
    st.caption(f"🏁 **Club:** {meta['current_club']} | 🏃‍♂️ **Position:** {meta['position']}")

    # Fixed typos in SQL window function syntax: PRECEDING and CURRENT
    perf_query = """
    SELECT
        gameweek as "GW",
        minutes_played as "Minutes",
        expected_goals as "xG",
        expected_assists as "xA",
        AVG(expected_goals) OVER (ORDER BY gameweek ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as "Rolling_xG",
        AVG(expected_assists) OVER (ORDER BY gameweek ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as "Rolling_xA",
        actual_points as "Actual_Points",
        shot_x, shot_y, was_goal
    FROM match_performance
    WHERE player_id = ?;
    """
    perf_df = run_query(perf_query, params=(int(selected_player_id),))

    if not perf_df.empty:
        col_table, col_ml, col_visuals = st.columns([1.6, 1.0, 1.4])

        with col_table:
            st.markdown("#### Match-by-Match Logs")
            st.dataframe(perf_df[["GW", "Minutes", "xG", "xA", "Actual_Points"]], hide_index=True)

        with col_ml:
            st.markdown("#### Predictive Inference")
            if model_loaded:
                latest = perf_df.iloc[-1]
                rxG = float(latest["Rolling_xG"])
                rxA = float(latest["Rolling_xA"])

                input_vector = np.array([[rxG, rxA]])
                predicted_pts = model.predict(input_vector)[0]

                st.metric(
                    label="Projected Points Next GW",
                    value=f"{round(predicted_pts, 2)} Pts",
                    delta=f"{round(predicted_pts - float(latest['Actual_Points']), 2)} vs Last Match"
                )
            else:
                st.warning("Model engine offline.")

        with col_visuals:
            tab_shot, tab_trend = st.tabs(["🎯 Opta-Style Shot Map", "📈 Performance Trends"])

            with tab_shot:
                shots = perf_df.dropna(subset=['shot_x', 'shot_y'])
                if not shots.empty:
                    pitch = VerticalPitch(half=True, pitch_color="#0e1117", line_color="#c7d5cc", goal_type="box")
                    fig, ax = pitch.draw(figsize=(5, 4))
                    fig.patch.set_facecolor("#0e1117")

                    goals = shots[shots['was_goal'] == 1]
                    misses = shots[shots['was_goal'] == 0]

                    # Fixed arguments and closing parenthesis syntax
                    pitch.scatter(
                        misses['shot_x'], misses['shot_y'], 
                        s=misses['xG']*600, edgecolors='#ff4b4b', 
                        facecolors='none', linewidth=1.5, ax=ax, label='Miss'
                    )
                    pitch.scatter(
                        goals['shot_x'], goals['shot_y'], 
                        s=goals['xG']*800, edgecolors='#00f0a2', 
                        facecolors='#00f0a2', marker='*', linewidth=1.5, ax=ax, label='Goal'
                    )
                    ax.legend(facecolor='#0e1117', edgecolor='none', labelcolor='white', loc='lower center')
                    st.pyplot(fig)
                else:
                    st.info("No spatial shot coordinates logged for this player.")

            with tab_trend:
                fig_trend, ax_trend = plt.subplots(figsize=(5, 3.5))
                fig_trend.patch.set_facecolor('#0e1117')
                ax_trend.set_facecolor('#0e1117')

                ax_trend.plot(perf_df["GW"], perf_df["Actual_Points"], marker='o', color='#00f0a2', linewidth=2, label="Actual points")
                # Fixed syntax error: changed 'linestyle==' to 'linestyle="--"'
                ax_trend.plot(perf_df["GW"], perf_df["xG"]*4, linestyle='--', color='#ff4b4b', alpha=0.7, label="xG Profile")
                
                ax_trend.set_title("Performance & Underlying Metric Volatility", color='white', fontsize=10)
                ax_trend.set_xlabel("Gameweek", color='white', fontsize=8)
                ax_trend.set_ylabel("Metrics / Points", color='white', fontsize=8)
                ax_trend.tick_params(colors='white', labelsize=8)
                ax_trend.grid(color='#262730', linestyle=':', alpha=0.5)
                ax_trend.legend(facecolor='#0e1117', edgecolor='none', labelcolor='white', fontsize=8)
                st.pyplot(fig_trend)