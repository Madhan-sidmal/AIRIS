"""
P5: Google Trends — AI search interest, Karnataka, 2020-2025.
Downloads state-level search interest for:
  - "ChatGPT"
  - "artificial intelligence"
  - "machine learning"
  - "AI tools"

Output: data/raw/google_trends/ka_ai_trends_2020_2025.csv
"""
from pytrends.request import TrendReq
import pandas as pd
from pathlib import Path
import time

OUT_DIR = Path("data/raw/google_trends")
OUT_DIR.mkdir(parents=True, exist_ok=True)

pytrends = TrendReq(hl="en-US", tz=330, timeout=(10, 25))

TERMS = [
    ["ChatGPT", "artificial intelligence"],
    ["machine learning", "AI tools"],
]

TIMEFRAMES = [
    ("2020-01-01 2021-12-31", "2020_2021"),
    ("2022-01-01 2023-12-31", "2022_2023"),
    ("2024-01-01 2025-12-31", "2024_2025"),
]

all_frames = []

for terms in TERMS:
    for tf, label in TIMEFRAMES:
        print(f"Fetching {terms} | {label} ...")
        try:
            pytrends.build_payload(
                terms,
                cat=0,
                timeframe=tf,
                geo="IN-KA",   # Karnataka
                gprop=""
            )
            df = pytrends.interest_over_time()
            if not df.empty:
                df = df.drop(columns=["isPartial"], errors="ignore")
                df["geo"] = "IN-KA"
                df["state"] = "Karnataka"
                df["timeframe"] = label
                all_frames.append(df)
                print(f"  Got {len(df)} rows")
            time.sleep(2)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)

if all_frames:
    result = pd.concat(all_frames, axis=0).reset_index()
    out = OUT_DIR / "ka_ai_trends_2020_2025.csv"
    result.to_csv(out, index=False)
    print(f"\nSaved: {out}")
    print(result.tail(10).to_string())
else:
    print("No data retrieved.")
