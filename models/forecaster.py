import pandas as pd
import pickle
import warnings
warnings.filterwarnings("ignore")
from prophet import Prophet
from datetime import datetime

# Load fresh data
print("Loading data...")
df = pd.read_csv("data/metrics_history.csv")
df = df[["_time", "cpu_percent", "ram_percent"]].dropna()
df["_time"] = pd.to_datetime(df["_time"], utc=True).dt.tz_localize(None)

# Clip CPU values to valid range 0-100
df["cpu_percent"] = df["cpu_percent"].clip(0, 100)
df["ram_percent"] = df["ram_percent"].clip(0, 100)

# CPU Forecast
print("Training CPU forecast model...")
cpu_df = df[["_time", "cpu_percent"]].rename(columns={"_time": "ds", "cpu_percent": "y"})
cpu_model = Prophet(
    interval_width=0.80,
    daily_seasonality=False,
    weekly_seasonality=False,
    changepoint_prior_scale=0.01
)
cpu_model.fit(cpu_df)

# RAM Forecast
print("Training RAM forecast model...")
ram_df = df[["_time", "ram_percent"]].rename(columns={"_time": "ds", "ram_percent": "y"})
ram_model = Prophet(
    interval_width=0.80,
    daily_seasonality=False,
    weekly_seasonality=False,
    changepoint_prior_scale=0.01
)
ram_model.fit(ram_df)

# Save models
import os
os.makedirs("models/saved", exist_ok=True)
with open("models/saved/cpu_prophet.pkl", "wb") as f:
    pickle.dump(cpu_model, f)
with open("models/saved/ram_prophet.pkl", "wb") as f:
    pickle.dump(ram_model, f)

# Test prediction from NOW
print("\nCPU forecast for next 30 minutes:")
now = datetime.now()
future_times = pd.date_range(start=now, periods=6, freq="5min")
future = pd.DataFrame({"ds": future_times})
forecast = cpu_model.predict(future)

for _, row in forecast.iterrows():
    cpu_pred = max(0, min(100, row["yhat"]))
    print(f"  {row['ds'].strftime('%H:%M')} → predicted CPU: {cpu_pred:.1f}%")

print("\n✅ Forecast models saved!")