import streamlit as st, pandas as pd, numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error
import pvlib

st.set_page_config(page_title="Solar PV Forecast (MVP)", layout="wide")
st.title("☀️ Solar PV Probabilistic Forecast (Local MVP)")

st.sidebar.header("Inputs")
lat = st.sidebar.number_input("Latitude", value=51.5, step=0.1, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-0.1, step=0.1, format="%.4f")

st.markdown("""
**What this does**  
• Pulls **PV Live (GB)** target PV (30-min).  
• Pulls **NASA POWER** hourly covariates.  
• Builds **pvlib** solar features.  
• Trains **LightGBM quantile** (P10/P50/P90) in seconds.  
• Shows bands + coverage + a simple ramp alarm.
""")

@st.cache_data(show_spinner=False)
def load_pv(path="data/pvlive_gb.csv"):
    df = pd.read_csv(path, parse_dates=["ts"]).set_index("ts").sort_index()
    return df.asfreq("30min")

@st.cache_data(show_spinner=False)
def load_power(path="data/nasa_power_hourly.csv"):
    df = pd.read_csv(path, parse_dates=["ts"]).set_index("ts").sort_index()
    return df.asfreq("H").interpolate()

def build_pvlib_features(idx, lat, lon):
    idx = pd.DatetimeIndex(idx.tz_localize("UTC"))
    solpos = pvlib.solarposition.get_solarposition(idx, lat, lon)
    loc = pvlib.location.Location(lat, lon)
    cs = loc.get_clearsky(idx)
    feats = pd.DataFrame({
        "zenith": solpos["zenith"],
        "azimuth": solpos["azimuth"],
        "ghi_clear": cs["ghi"],
        "dni_clear": cs["dni"],
        "dhi_clear": cs["dhi"],
    }, index=idx)
    return feats

# Load data (assumes you've run scripts to fetch them)
try:
    pv = load_pv()
    wx = load_power()
except Exception as e:
    st.error("Data files not found. Run the two fetch scripts in README first.")
    st.stop()

# Align to hourly for speed
pv_h = pv.resample("H").mean().dropna()
df = pv_h.join(wx, how="inner").dropna()

# pvlib features on the joined index
pvlib_feats = build_pvlib_features(df.index, lat, lon)
df = df.join(pvlib_feats, how="left")

# Feature engineering
for k in [1,2,3,6,12,24]:
    df[f"lag_{k}"] = df["pv_mw"].shift(k)
df["hour"] = df.index.hour
df["doy"] = df.index.dayofyear
df = df.dropna()

# Train/test split (last 24h = test)
train = df.iloc[:-24].copy()
test  = df.iloc[-24:].copy()
Xtr, ytr = train.drop(columns=["pv_mw"]), train["pv_mw"]
Xte, yte = test.drop(columns=["pv_mw"]), test["pv_mw"]

def fit_q(alpha):
    params = {"objective":"quantile","alpha":alpha,"learning_rate":0.05,"num_leaves":64}
    dtrain = lgb.Dataset(Xtr, label=ytr)
    return lgb.train(params, dtrain, num_boost_round=300)

with st.spinner("Training quantile models…"):
    m10, m50, m90 = fit_q(0.1), fit_q(0.5), fit_q(0.9)
    p10 = m10.predict(Xte); p50 = m50.predict(Xte); p90 = m90.predict(Xte)

# Metrics
nmae = mean_absolute_error(yte, p50) / (ytr.max()+1e-9)
coverage = np.mean((yte.values >= p10) & (yte.values <= p90))
col1, col2 = st.columns(2)
col1.metric("nMAE (vs P50)", f"{nmae:.3f}")
col2.metric("Coverage (P10–P90)", f"{coverage*100:.1f}%")

st.subheader("Forecast bands")
plot = pd.DataFrame({"Actual": yte, "P10": p10, "P50": p50, "P90": p90}, index=yte.index)
st.line_chart(plot)

# Simple ramp alert: predict drop ≥25% within next hour by P10
if len(p10) > 1 and p50[0] > 0:
    risk = (p10[-1] - p50[0]) / (p50[0] + 1e-6) < -0.25
    st.success("Ramp risk next hour: HIGH ⚠️" if risk else "Ramp risk next hour: LOW ✅")
else:
    st.info("Not enough points for ramp check.")
