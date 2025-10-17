# Solar PV Probabilistic Forecast — Local MVP

A polished **Streamlit** app that downloads **PV Live (GB)** and **NASA POWER** data, trains a **LightGBM quantile** model in seconds, and plots **P10/P50/P90** bands with basic metrics.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Fetch 1 week of PV + NASA POWER
python scripts/fetch_pvlive.py --start 2025-01-01T00:00Z --end 2025-01-08T00:00Z --out data/pvlive_gb.csv
python scripts/fetch_nasapower.py --lat 51.5 --lon -0.1 --start 20250101 --end 20250108 --out data/nasa_power_hourly.csv

# Run the app
streamlit run app/ForecastApp.py
```

## What you get
- **P10/P50/P90** probabilistic forecasts (quantiles) using **LightGBM quantile**.
- Metrics: **nMAE**, **Coverage** (P10–P90), and a simple **ramp alert**.
- Clean, single-page Streamlit UI.

## Notes
- PV Live is **GB aggregate PV** at 30-minute cadence (CC BY 4.0).
- NASA POWER provides **hourly** solar/meteorology via a free REST API.
- This is an MVP; add satellite nowcasting (NSRDB/INSAT), conformal calibration, and TFT later.
