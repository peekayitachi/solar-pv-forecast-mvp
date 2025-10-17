#!/usr/bin/env python3
import argparse, requests, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="ISO e.g. 2025-01-01T00:00Z")
    ap.add_argument("--end", required=True, help="ISO e.g. 2025-01-08T00:00Z")
    ap.add_argument("--regionid", type=int, default=0, help="0=national")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    url = f"https://api.pvlive.uk/v4/pvlive?start={args.start}&end={args.end}&regionid={args.regionid}"
    j = requests.get(url, timeout=60).json()["data"]
    df = pd.DataFrame(j, columns=["datetime_gmt","generation_mw","region_id","dataset"])
    df["ts"] = pd.to_datetime(df["datetime_gmt"], utc=True)
    df = df[["ts","generation_mw"]].rename(columns={"generation_mw":"pv_mw"})
    df.to_csv(args.out, index=False)
    print(f"Saved {df.shape} to {args.out}")

if __name__ == "__main__":
    main()
