import pandas as pd
import pickle
import warnings
warnings.filterwarnings("ignore")
from prophet import Prophet
from datetime import datetime

# Load data
print("Loading data...")
df = pd.read_csv("data/metrics_history.csv")
df = df[["_time", "cpu_percent", "ram_percent"]].dropna()
df["_time"] = pd.to_datetime(df["_time"], utc=True).dt.tz_localize(None)

# ── CPU Forecast ──────
print("Training CPU forecast model...")
cpu_df = df[["_time", "cpu_percent"]].rename(columns={"_time": "ds", "cpu_percent": "y"})
cpu_model = Prophet(interval_width=0.80, daily_seasonality=False, weekly_seasonality=False)
cpu_model.fit(cpu_df)

# ── RAM Forecast ──────
print("Training RAM forecast model...")
ram_df = df[["_time", "ram_percent"]].rename(columns={"_time": "ds", "ram_percent": "y"})
ram_model = Prophet(interval_width=0.80, daily_seasonality=False, weekly_seasonality=False)
ram_model.fit(ram_df)

# ── Save models ─────
with open("models/saved/cpu_prophet.pkl", "wb") as f:
    pickle.dump(cpu_model, f)
with open("models/saved/ram_prophet.pkl", "wb") as f:
    pickle.dump(ram_model, f)

# ── Quick test — predict next 30 minutes ────────
print("\nCPU forecast for next 30 minutes:")
future = cpu_model.make_future_dataframe(periods=6, freq="5min")
forecast = cpu_model.predict(future)
upcoming = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(6)
for _, row in upcoming.iterrows():
    print(f"  {row['ds'].strftime('%H:%M')} → predicted CPU: {row['yhat']:.1f}% (range: {row['yhat_lower']:.1f}–{row['yhat_upper']:.1f}%)")

print("\n✅ Forecast models saved to models/saved/")