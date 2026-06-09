from influxdb_client import InfluxDBClient
import pandas as pd

INFLUX_URL    = "http://localhost:8086"
INFLUX_TOKEN  = "RSlYJebICNsJtmoOXp3BROMi_R8LSP1SdrnzRj_Bnq5rtC3-hgS_pEA0eqgbXZlta0ZIt9G1YZXFzFh71L7S_w=="
INFLUX_ORG    = "myorg"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

query = '''
from(bucket: "system_metrics")
  |> range(start: -3h)
  |> filter(fn: (r) => r._measurement == "system_metrics")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> keep(columns: ["_time", "cpu_percent", "ram_percent", "disk_percent", "net_sent_mb"])
'''

print("Exporting data from InfluxDB...")
df = query_api.query_data_frame(query)
df.to_csv("data/metrics_history.csv", index=False)
print(f"Done! Exported {len(df)} rows to data/metrics_history.csv")