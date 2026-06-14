from flask import Flask, jsonify, render_template_string
from influxdb_client import InfluxDBClient
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from alerts.alert_manager import send_alert
import psutil
import pickle
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

INFLUX_URL    = "http://localhost:8086"
INFLUX_TOKEN  = "RSlYJebICNsJtmoOXp3BROMi_R8LSP1SdrnzRj_Bnq5rtC3-hgS_pEA0eqgbXZlta0ZIt9G1YZXFzFh71L7S_w=="
INFLUX_ORG    = "myorg"
INFLUX_BUCKET = "system_metrics"

app = Flask(__name__)
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

with open("models/saved/isolation_forest.pkl", "rb") as f:
    model = pickle.load(f)
with open("models/saved/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Monitor Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0f1117; color:#fff; font-family:'Segoe UI',sans-serif; padding:20px; }
        h1 { text-align:center; margin-bottom:6px; font-size:24px; color:#00d4ff; }
        p.sub { text-align:center; color:#888; margin-bottom:16px; font-size:13px; }
        .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px; }
        .card { background:#1a1d2e; border-radius:12px; padding:20px; text-align:center; border:1px solid #2a2d3e; }
        .card .label { font-size:12px; color:#888; margin-bottom:8px; text-transform:uppercase; letter-spacing:1px; }
        .card .value { font-size:36px; font-weight:700; }
        .card .unit  { font-size:13px; color:#888; margin-top:4px; }
        .cpu-val  { color:#00d4ff; }
        .ram-val  { color:#a78bfa; }
        .disk-val { color:#34d399; }
        .net-val  { color:#fb923c; }
        .charts { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
        .chart-box { background:#1a1d2e; border-radius:12px; padding:20px; border:1px solid #2a2d3e; }
        .chart-box h3 { font-size:13px; color:#888; margin-bottom:14px; text-transform:uppercase; letter-spacing:1px; }
        .status-bar { text-align:center; margin-bottom:16px; padding:12px; border-radius:10px; font-size:14px; font-weight:600; transition: all 0.3s; }
        .status-normal  { background:#0d2e1f; border:1px solid #34d399; color:#34d399; }
        .status-anomaly { background:#2e0d0d; border:1px solid #f87171; color:#f87171; animation: flashborder 1s infinite; }
        @keyframes flashborder { 0%,100%{border-color:#f87171} 50%{border-color:#7f1d1d} }
        .dot { display:inline-block; width:8px; height:8px; background:#34d399; border-radius:50%; margin-right:6px; animation:pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        .ai-score { text-align:center; color:#888; font-size:12px; margin-bottom:16px; }
        .forecast-box { background:#1a1d2e; border-radius:12px; padding:20px; border:1px solid #2a2d3e; margin-bottom:20px; }
        .forecast-box h3 { font-size:13px; color:#888; margin-bottom:14px; text-transform:uppercase; letter-spacing:1px; }
        table { width:100%; border-collapse:collapse; }
        th { color:#888; font-size:12px; text-align:left; padding:8px; border-bottom:1px solid #2a2d3e; }
        td { font-size:13px; padding:8px; border-bottom:1px solid #1a1d2e; }
        tr:hover td { background:#1f2235; }
    </style>
</head>
<body>
    <h1> AI System Monitor</h1>
    <p class="sub">Real-time metrics + AI anomaly detection</p>

    <div class="status-bar status-normal" id="statusBar">
        <span class="dot"></span>  All systems normal
    </div>
    <div class="ai-score" id="aiScore">AI confidence score: --</div>

    <div class="cards">
        <div class="card"><div class="label">CPU Usage</div><div class="value cpu-val" id="cpu">--</div><div class="unit">percent</div></div>
        <div class="card"><div class="label">RAM Usage</div><div class="value ram-val" id="ram">--</div><div class="unit">percent</div></div>
        <div class="card"><div class="label">Disk Usage</div><div class="value disk-val" id="disk">--</div><div class="unit">percent</div></div>
        <div class="card"><div class="label">Network Sent</div><div class="value net-val" id="net">--</div><div class="unit">MB total</div></div>
    </div>

    <div class="forecast-box">
        <h3>🔮 AI Forecast — Next 30 Minutes</h3>
        <table>
            <thead>
                <tr><th>Time</th><th>Predicted CPU</th><th>Predicted RAM</th></tr>
            </thead>
            <tbody id="forecastBody">
                <tr><td colspan="3" style="text-align:center;color:#888">Loading...</td></tr>
            </tbody>
        </table>
    </div>

    <div class="charts">
        <div class="chart-box"><h3>CPU % — Last 50 readings</h3><canvas id="cpuChart"></canvas></div>
        <div class="chart-box"><h3>RAM % — Last 50 readings</h3><canvas id="ramChart"></canvas></div>
    </div>

<script>
const makeChart = (id, color, label) => new Chart(document.getElementById(id), {
    type: 'line',
    data: { labels: [], datasets: [{ label, data: [], borderColor: color, backgroundColor: color+'22', borderWidth:2, pointRadius:0, tension:0.4, fill:true }] },
    options: { animation:false, scales: { x:{display:false}, y:{min:0, max:100, ticks:{color:'#888'}, grid:{color:'#2a2d3e'}} }, plugins:{legend:{display:false}} }
});

const cpuChart = makeChart('cpuChart', '#00d4ff', 'CPU %');
const ramChart = makeChart('ramChart', '#a78bfa', 'RAM %');

const addData = (chart, value) => {
    chart.data.labels.push(new Date().toLocaleTimeString());
    chart.data.datasets[0].data.push(value);
    if (chart.data.labels.length > 50) { chart.data.labels.shift(); chart.data.datasets[0].data.shift(); }
    chart.update();
};

let anomalyTimer = null;

const refresh = async () => {
    try {
        const r = await fetch('/metrics');
        const d = await r.json();
        document.getElementById('cpu').textContent  = d.cpu + '%';
        document.getElementById('ram').textContent  = d.ram + '%';
        document.getElementById('disk').textContent = d.disk + '%';
        document.getElementById('net').textContent  = d.net;
        document.getElementById('aiScore').textContent = 'AI anomaly score: ' + d.score;

        const bar = document.getElementById('statusBar');
        if (d.anomaly) {
            bar.className = 'status-bar status-anomaly';
            bar.innerHTML = ' ANOMALY DETECTED — Unusual system behaviour spotted by AI';
            if (anomalyTimer) clearTimeout(anomalyTimer);
            anomalyTimer = setTimeout(() => {
                bar.className = 'status-bar status-normal';
                bar.innerHTML = '<span class="dot"></span>  All systems normal';
            }, 8000);
        } else {
            if (!anomalyTimer) {
                bar.className = 'status-bar status-normal';
                bar.innerHTML = '<span class="dot"></span>  All systems normal';
            }
        }
        addData(cpuChart, d.cpu);
        addData(ramChart, d.ram);
    } catch(e) { console.error(e); }
};

const refreshForecast = async () => {
    try {
        const r = await fetch('/forecast');
        const d = await r.json();
        if (d.error) return;
        const body = document.getElementById('forecastBody');
        body.innerHTML = d.forecast.map(row => `
            <tr>
                <td style="color:#888">${row.time}</td>
                <td style="color:#00d4ff">${row.cpu}%</td>
                <td style="color:#a78bfa">${row.ram}%</td>
            </tr>
        `).join('');
    } catch(e) { console.error(e); }
};

setInterval(refresh, 3000);
setInterval(refreshForecast, 30000);
refresh();
refreshForecast();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/metrics')
def metrics():
    cpu  = psutil.cpu_percent(interval=0.5)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage('C:/').percent
    net  = round(psutil.net_io_counters().bytes_sent / 1024 / 1024, 2)

    df     = pd.DataFrame([[cpu, ram, disk, net]],
             columns=["cpu_percent","ram_percent","disk_percent","net_sent_mb"])
    scaled = scaler.transform(df)
    result = model.predict(scaled)[0]
    score  = round(model.decision_function(scaled)[0], 3)
    is_anomaly = bool(result == -1 and score < -0.05)

    if is_anomaly:
        try:
            send_alert(cpu, ram, score)
        except Exception:
            pass

    return jsonify(cpu=cpu, ram=ram, disk=disk, net=net,
                   anomaly=is_anomaly, score=score)

@app.route('/forecast')
def forecast():
    try:
        with open("models/saved/cpu_prophet.pkl", "rb") as f:
            cpu_model = pickle.load(f)
        with open("models/saved/ram_prophet.pkl", "rb") as f:
            ram_model = pickle.load(f)

        now = datetime.now()
        future_times = pd.date_range(start=now, periods=6, freq="5min")
        future = pd.DataFrame({"ds": future_times})

        cpu_forecast = cpu_model.predict(future)
        ram_forecast = ram_model.predict(future)

        result = []
        for i in range(6):
            cpu_val = round(max(0, min(100, cpu_forecast.iloc[i]["yhat"])), 1)
            ram_val = round(max(0, min(100, ram_forecast.iloc[i]["yhat"])), 1)
            result.append({
                "time": cpu_forecast.iloc[i]["ds"].strftime("%H:%M"),
                "cpu":  cpu_val,
                "ram":  ram_val
            })
        return jsonify(forecast=result)
    except Exception as e:
        return jsonify(error=str(e))

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5001")
    app.run(debug=False, port=5001)