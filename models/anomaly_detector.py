import psutil
import pickle
import pandas as pd
import time
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# Load saved model and scaler
with open("models/saved/isolation_forest.pkl", "rb") as f:
    model = pickle.load(f)
with open("models/saved/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

print(" AI Model loaded. Watching for anomalies...\n")

def get_metrics():
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage('C:/').percent
    net  = round(psutil.net_io_counters().bytes_sent / 1024 / 1024, 2)
    return pd.DataFrame([[cpu, ram, disk, net]],
           columns=["cpu_percent", "ram_percent", "disk_percent", "net_sent_mb"])

while True:
    metrics_df = get_metrics()
    scaled     = scaler.transform(metrics_df)
    result     = model.predict(scaled)[0]
    score      = model.decision_function(scaled)[0]

    cpu  = metrics_df["cpu_percent"].values[0]
    ram  = metrics_df["ram_percent"].values[0]
    status = "🚨 ANOMALY DETECTED" if result == -1 else "✅ Normal"

    print(f"{datetime.now().strftime('%H:%M:%S')} | CPU: {cpu}% | RAM: {ram}% | {status} (score: {score:.3f})")
    time.sleep(5)