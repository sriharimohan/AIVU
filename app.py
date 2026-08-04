import os
import pickle
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# ------------------------------------------------------------------
# 1. Page Configuration & Custom Styling
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AIVU | Sports Analytics Engine",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ AIVU — Advanced Football Performance Engine")
st.markdown("Closed-form Ridge OLS matrix projections and spatial event analysis.")

# ------------------------------------------------------------------
# 2. Safe Model Artifact Loading
# ------------------------------------------------------------------
MODEL_PATH = os.path.join("models", "aivu_pipeline.pkl")

@st.cache_resource
def load_aivu_model():
    if not os.path.exists(MODEL_PATH):
        st.error(f"⚠️ Model file missing at '{MODEL_PATH}'. Please run `python run_analytics.py` first.")
        st.stop()
    
    try:
        with open(MODEL_PATH, "rb") as f:
            payload = pickle.load(f)
        return payload
    except Exception as e:
        st.error(f"⚠️ Could not read model artifact: {e}")
        st.stop()

# Initialize global payload variables cleanly
model_payload = load_aivu_model()
beta_weights = model_payload["weights"]
feature_names = model_payload["feature_names"]
df_perf = model_payload["sample_data"]

# ------------------------------------------------------------------
# 3. Sidebar — Player Selection & Controls
# ------------------------------------------------------------------
st.sidebar.header("🔍 Player Selection")

player_list = sorted(df_perf["player_name"].dropna().unique().tolist())
selected_player = st.sidebar.selectbox("Select Player", player_list)

# Filter dataset for selected player
player_data = df_perf[df_perf["player_name"] == selected_player].sort_values("gameweek")

if player_data.empty:
    st.warning("No performance records found for this player.")
    st.stop()

player_pos = player_data["position"].iloc[0] if "position" in player_data.columns else "Unknown"
st.sidebar.markdown(f"**Position:** {player_pos}")
st.sidebar.markdown(f"**Matches Recorded:** {len(player_data)}")

# ------------------------------------------------------------------
# 4. KPI Summary Cards
# ------------------------------------------------------------------
st.subheader(f"📊 Summary Stats — {selected_player}")

col1, col2, col3, col4 = st.columns(4)

total_pts = player_data["actual_points"].sum() if "actual_points" in player_data.columns else 0
avg_xg = player_data["expected_goals"].mean() if "expected_goals" in player_data.columns else 0.0
avg_xa = player_data["expected_assists"].mean() if "expected_assists" in player_data.columns else 0.0
avg_mins = player_data["minutes_played"].mean() if "minutes_played" in player_data.columns else 0.0

col1.metric("Total Points", f"{int(total_pts)}")
col2.metric("Avg Expected Goals (xG)", f"{avg_xg:.2f}")
col3.metric("Avg Expected Assists (xA)", f"{avg_xa:.2f}")
col4.metric("Avg Minutes Played", f"{avg_mins:.0f} mins")

st.markdown("---")

# ------------------------------------------------------------------
# 5. OLS Model Prediction Engine
# ------------------------------------------------------------------
st.subheader("🤖 OLS Matrix Performance Projection")

# Latest match feature values for prediction
latest_row = player_data.iloc[-1]
latest_x = [latest_row[col] for col in feature_names]

# Matrix multiplication: Y_pred = beta0 + sum(beta_i * X_i)
predicted_score = beta_weights[0] + np.dot(latest_x, beta_weights[1:])

st.info(f"**Next Match Predicted Point Value:** **`{predicted_score:.2f}`** pts")

with st.expander("View OLS Regression Model Weights (Beta Parameters)"):
    weights_df = pd.DataFrame({
        "Feature": ["Intercept (Bias)"] + feature_names,
        "Beta Coefficient Weight": beta_weights
    })
    st.dataframe(weights_df, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------
# 6. Spatial Pitch Analysis & Heatmaps
# ------------------------------------------------------------------
st.subheader("🎯 Spatial Shot Location & Pitch Map")

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0e1117')
ax.set_facecolor('#0e1117')

pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5e0')
pitch.draw(ax=ax)

# Filter spatial shot data if available in table
shots = player_data[player_data["shot_x"].notnull()] if "shot_x" in player_data.columns else pd.DataFrame()

if not shots.empty:
    goals = shots[shots["was_goal"] == 1] if "was_goal" in shots.columns else pd.DataFrame()
    non_goals = shots[shots["was_goal"] == 0] if "was_goal" in shots.columns else shots

    # Non-goals (Red dots)
    if not non_goals.empty:
        pitch.scatter(non_goals["shot_x"], non_goals["shot_y"], ax=ax, c='red', alpha=0.6, s=100, label='Shot (Saved/Missed)')
    
    # Goals (Green dots)
    if not goals.empty:
        pitch.scatter(goals["shot_x"], goals["shot_y"], ax=ax, c='lime', alpha=0.9, s=200, marker='*', label='Goal')
    
    ax.legend(facecolor='#0e1117', edgecolor='none', labelcolor='white', loc='upper left')
else:
    ax.text(60, 40, "No spatial shot coordinates logged for this player.", color='white', ha='center', va='center', fontsize=12)

st.pyplot(fig)

# ------------------------------------------------------------------
# 7. Raw Match Logs Table
# ------------------------------------------------------------------
st.subheader("📜 Historical Match Performance Data")
display_cols = [c for c in ["gameweek", "expected_goals", "expected_assists", "minutes_played", "actual_points", "previous_week_points"] if c in player_data.columns]
st.dataframe(player_data[display_cols], use_container_width=True)