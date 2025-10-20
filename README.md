# SunShift – Energy Estimator Based on Daily Peak Sun Hours

A single-file **Streamlit** app that estimates **Peak Sun Hours (PSH)** and **energy output** from free **Open-Meteo** data for major Indian metros and global cities.

## Quickstart (Windows PowerShell)

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
streamlit run .app\PSHExplorer.py
```

## Features
- PSH Today (kWh/m²), kWh at 1 kWp (editable PR), Solar Day Class (percentile vs 30 days), Confidence (cloud variability)
- Best 2-hour window for solar-aligned usage
- Charts: hourly radiation today, 30-day PSH sparkline
- Impact: ₹ savings and CO₂ avoided for user system size
