from flask import Flask, jsonify, render_template_string
from influxdb_client import InfluxDBClient
import psutil

INFLUX_URL    = "http://localhost:8086"
INFLUX_TOKEN  = "RSlYJebICNsJtmoOXp3BROMi_R8LSP1SdrnzRj_Bnq5rtC3-hgS_pEA0eqgbXZlta0ZIt9G1YZXFzFh71L7S_w=="
INFLUX_ORG    = "myorg"
INFLUX_BUCKET = "system_metrics"

app = Flask(__name__)
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

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
        p.sub { text-align:center; color:#888; margin-bottom:24px; font-size:13px; }
        .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; }
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
        .status { text-align:center; margin-bottom:16px; }
        .dot { display:inline-block; width:8px; height:8px; background:#34d399; border-radius:50%; margin-right:6px; animation:pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    </style>
</head>
<body>
    <h1>⚡ AI System Monitor</h1>
    <p class="sub">Real-time metrics from your machine</p>
    <div class="status"><span class="dot"></span><span style="color:#34d399;font-size:13px">Live — updating every 3 seconds</span></div>

    <div class="cards">
        <div class="card"><div class="label">CPU Usage</div><div class="value cpu-val" id="cpu">--</div><div class="unit">percent</div></div>
        <div class="card"><div class="label">RAM Usage</div><div class="value ram-val" id="ram">--</div><div class="unit">percent</div></div>
        <div class="card"><div class="label">Disk Usage</div><div class="value disk-val" id="disk">--</div><div class="unit">percent</div></div>
        <div class="card"><div class="label">Network Sent</div><div class="value net-val" id="net">--</div><div class="unit">MB total</div></div>
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
    const time = new Date().toLocaleTimeString();
    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(value);
    if (chart.data.labels.length > 50) { chart.data.labels.shift(); chart.data.datasets[0].data.shift(); }
    chart.update();
};

const refresh = async () => {
    try {
        const r = await fetch('/metrics');
        const d = await r.json();
        document.getElementById('cpu').textContent  = d.cpu + '%';
        document.getElementById('ram').textContent  = d.ram + '%';
        document.getElementById('disk').textContent = d.disk + '%';
        document.getElementById('net').textContent  = d.net;
        addData(cpuChart, d.cpu);
        addData(ramChart, d.ram);
    } catch(e) { console.error(e); }
};

setInterval(refresh, 3000);
refresh();
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
    return jsonify(cpu=cpu, ram=ram, disk=disk, net=net)

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(debug=False, port=5000)