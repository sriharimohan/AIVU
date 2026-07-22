import sqlite3
import pandas as pd
import os
import numpy as np
import joblib

# 1. Cross-platform path resolution
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "aivu_analytics.db")
MODEL_PATH = os.path.join(PROJECT_DIR, "aivu_pipeline.pkl")

class AIVULinearRegression:
    """
    Custom ordinary least squares (OLS) linear regression model.
    Solves the normal equation using closed-form matrix operations.
    """
    def __init__(self):
        self.weights = None
        self.intercept = None

    def fit(self, X, y):
        # Add a bias column of 1s to handle the intercept
        X_mat = np.hstack([np.ones((X.shape[0], 1)), X])
        
        # Solve the normal equation: beta = (X^T * X)^(-1) * X^T * y
        try:
            # Standard algebraic inverse
            beta = np.linalg.inv(X_mat.T @ X_mat) @ X_mat.T @ y
        except np.linalg.LinAlgError:
            print("⚠️ Singular matrix encountered. Falling back to Moore-Penrose pseudo-inverse.")
            # Fallback pseudo-inverse to ensure pipeline execution safety
            beta = np.linalg.pinv(X_mat.T @ X_mat) @ X_mat.T @ y
            
        self.intercept = float(beta[0])
        self.weights = beta[1:].astype(float)

    def predict(self, X):
        return np.dot(X, self.weights) + self.intercept


def calculate_diagnostics(y_true, y_pred):
    """Computes basic model metrics to evaluate performance."""
    mse = np.mean((y_true - y_pred) ** 2)
    # Coefficient of Determination (R²)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    return mse, r2


def train_predictive_engine():
    # Establish connection with error safety
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.OperationalError as e:
        print(f"❌ Connection failed. Ensure the database has been created first. Error: {e}")
        return

    # Extract rolling event metrics for training
    query = """
    SELECT 
        AVG(expected_goals) OVER (PARTITION BY player_id ORDER BY gameweek ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3wk_xG,
        AVG(expected_assists) OVER (PARTITION BY player_id ORDER BY gameweek ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3wk_xA,
        actual_points AS target_performance
    FROM match_performance
    WHERE minutes_played >= 45;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("\n" + "="*60)
    print("🤖 INITIATING AIVU PREDICTIVE MODEL TRAINING")
    print("="*60)
    print("\n--- Extracted Dataset for Model Training ---")
    print(df.to_string(index=False))
    
    if len(df) < 2:
        print("\n❌ Error: Not enough data in database to fit linear regression. Ingest more match events.")
        return

    # Isolate independent features and dependent target
    X = df[['rolling_3wk_xG', 'rolling_3wk_xA']].to_numpy()
    y = df['target_performance'].to_numpy()
    
    print(f"\nTraining analytical matrices on {len(df)} tracking vectors...")
    
    # Initialize and fit custom OLS model
    model = AIVULinearRegression()
    model.fit(X, y)
    
    # Generate in-sample predictions for performance metrics
    predictions = model.predict(X)
    mse, r2 = calculate_diagnostics(y, predictions)
    
    print("\n" + "-"*40)
    print("📊 MODEL COEF & PERFORMANCE DIAGNOSTICS")
    print("-"*40)
    print(f"• Intercept:  {round(model.intercept, 4)}")
    print(f"• Weights:    {np.round(model.weights, 4)} [rolling_xG, rolling_xA]")
    print(f"• In-sample MSE: {round(mse, 4)}")
    print(f"• In-sample R²:  {round(r2, 4)}")
    print("-"*40)
    
    # Save model artifact locally
    joblib.dump(model, MODEL_PATH)
    print(f"\n✅ Production model artifact saved cleanly to:\n📍 {MODEL_PATH}")
    print("="*60 + "\n")


if __name__ == "__main__":
    train_predictive_engine()