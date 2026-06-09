import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os

print("Loading data...")
df = pd.read_csv("data/metrics_history.csv")

# Keep only the metric columns
features = ["cpu_percent", "ram_percent", "disk_percent", "net_sent_mb"]
df = df[features].dropna()

print(f"Training on {len(df)} rows with features: {features}")

# Scale the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Train Isolation Forest
# contamination=0.05 means we expect ~5% of data to be anomalies
model = IsolationForest(
    n_estimators=100,
    contamination=0.02,
    random_state=42
)
model.fit(X_scaled)

# Test it on the training data
predictions = model.predict(X_scaled)
anomaly_count = (predictions == -1).sum()
print(f"Found {anomaly_count} anomalies in training data ({anomaly_count/len(df)*100:.1f}%)")

# Save the model and scaler
os.makedirs("models/saved", exist_ok=True)
with open("models/saved/isolation_forest.pkl", "wb") as f:
    pickle.dump(model, f)
with open("models/saved/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("✅ Model saved to models/saved/")
print("Training complete!")