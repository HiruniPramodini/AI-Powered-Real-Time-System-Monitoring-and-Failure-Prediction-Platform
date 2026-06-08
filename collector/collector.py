import psutil
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL    = "http://localhost:8086"
INFLUX_TOKEN  = "RSlYJebICNsJtmoOXp3BROMi_R8LSP1SdrnzRj_Bnq5rtC3-hgS_pEA0eqgbXZlta0ZIt9G1YZXFzFh71L7S_w=="
INFLUX_ORG    = "myorg"
INFLUX_BUCKET = "system_metrics"

client    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def collect_metrics():
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage('C:/').percent
    net  = psutil.net_io_counters()
    net_mb = round(net.bytes_sent / 1024 / 1024, 2)

    point = (
        Point("system_metrics")
        .tag("host", "my-pc")
        .field("cpu_percent",  cpu)
        .field("ram_percent",  ram)
        .field("disk_percent", disk)
        .field("net_sent_mb",  net_mb)
        .time(datetime.utcnow())
    )

    write_api.write(bucket=INFLUX_BUCKET, record=point)
    print(f"{datetime.now().strftime('%H:%M:%S')} | CPU: {cpu}% | RAM: {ram}% | Disk: {disk}%")

print("✅ Collector started. Press Ctrl+C to stop.")
while True:
    collect_metrics()
    time.sleep(5)