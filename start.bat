@echo off
echo Starting AI Monitoring System...
start "InfluxDB" C:\Users\hirun\Downloads\influxdb2-2.7.10-windows\influxd.exe
timeout /t 3
start "Collector" cmd /k "cd C:\Users\hirun\ai-monitoring-project && venv\Scripts\activate && python collector/collector.py"
timeout /t 2
start "Dashboard" cmd /k "cd C:\Users\hirun\ai-monitoring-project && venv\Scripts\activate && python dashboard/app.py"
echo All services started! Open http://localhost:5000