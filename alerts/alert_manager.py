from plyer import notification
from datetime import datetime

COOLDOWN_MINUTES = 5
last_alert_time  = None

def send_alert(cpu, ram, score):
    global last_alert_time

    now = datetime.now()
    if last_alert_time:
        diff = (now - last_alert_time).seconds / 60
        if diff < COOLDOWN_MINUTES:
            return

    notification.notify(
        title   = "🚨 AI Monitor — Anomaly Detected",
        message = f"CPU: {cpu}%  |  RAM: {ram}%\nAI Score: {score}",
        app_name= "AI System Monitor",
        timeout = 10
    )

    last_alert_time = now
    print(f"✅ Desktop notification sent at {now.strftime('%H:%M:%S')}")