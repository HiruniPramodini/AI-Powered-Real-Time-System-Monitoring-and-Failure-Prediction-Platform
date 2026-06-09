# AI-Powered Real-Time System Monitoring & Failure Prediction Platform

A real-time system monitoring platform with AI-based anomaly detection 
and failure prediction, built as a 3rd year university project.

## Features
- Live CPU, RAM, disk, and network monitoring
- Time-series data storage with InfluxDB
- AI anomaly detection using Isolation Forest & LSTM
- Predictive forecasting with Facebook Prophet
- Real-time web dashboard
- Smart alerting system

## Tech Stack
- Python, Flask, psutil
- InfluxDB (time-series database)
- scikit-learn, PyTorch, Prophet
- Chart.js (frontend)

## Project Phases
-  Phase 1 — Data pipeline & live dashboard
-  Phase 2 — Data collection & export
-  Phase 3 — Anomaly detection model
-  Phase 4 — Predictive forecasting
-  Phase 5 — Alerts & auto-remediation

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python collector/collector.py
python dashboard/app.py
```

## Author
Hiruni Pramodini — 3rd Year undergraduate project
