from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

frames = []
for csv in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(csv)
    df.columns = [c.strip().lower() for c in df.columns]

    def to_num(x):
        if pd.isna(x): return None
        if isinstance(x, (int, float)): return x
        s = str(x).replace("$", "").replace(",", "").strip()
        return pd.to_numeric(s, errors="coerce")

    df["quantity"] = df["quantity"].apply(to_num)
    df["price"] = df["price"].apply(to_num)

    # keep Pink Morsel(s)
    df = df[df["product"].astype(str).str.strip().str.lower().str.match(r"^pink\s+morsel(s)?$")]

    df["sales"] = df["quantity"] * df["price"]
    frames.append(df[["sales", "date", "region"]])

out = pd.concat(frames, ignore_index=True)
out["sales"] = out["sales"].round(2)
outfile = OUT_DIR / "pink_morsels_sales.csv"
out.to_csv(outfile, index=False)
print(f"Wrote {len(out)} rows -> {outfile}")
