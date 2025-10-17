#!/usr/bin/env python3
import argparse, requests, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--start", required=True, help="YYYYMMDD")
    ap.add_argument("--end", required=True, help="YYYYMMDD")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    url=(
        "https://power.larc.nasa.gov/api/temporal/hourly/point"
        f"?latitude={args.lat}&longitude={args.lon}&start={args.start}&end={args.end}"
        "&community=RE&parameters=T2M,WS10M,ALLSKY_SFC_SW_DWN&format=JSON"
    )
    j = requests.get(url, timeout=60).json()
    params = j.get("properties", {}).get("parameter", {})
    rows = []
    for var, vals in params.items():
        for t, v in vals.items():
            rows.append({"ts": pd.to_datetime(t, utc=True), "var": var, "val": v})
    df = pd.DataFrame(rows).pivot(index="ts", columns="var", values="val").reset_index()
    df.to_csv(args.out, index=False)
    print(f"Saved {df.shape} to {args.out}")

if __name__ == "__main__":
    main()
