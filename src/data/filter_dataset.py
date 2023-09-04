#!/usr/bin/env python

import sys
from pathlib import Path
import pandas as pd

df = pd.read_csv(sys.stdin, index_col=0)
df = df[~df.index.duplicated(keep="first")]
outpath = Path("./data/processed/")
print(df.bp_pi10.describe())

sizes = {}
# ------ REMOVE segmentations with errors
sizes["total"] = len(df)
df = df[~df.bp_seg_error]
sizes["error"] = sizes["total"] - len(df)
df = df[(df.bp_leak_score != 0) | (df.bp_segmental_score != 0) |
        (df.bp_subsegmental_score != 0)]
sizes["screened"] = sizes["total"] - sizes["error"] - len(df)
# ------ REMOVE missing smoking status
sizes["missing-shx"] = len(df[df.smoking_status.isna()])
df = df.dropna(subset=["smoking_status"])
# ------ SAVE DF
df.to_csv(str(outpath / "final_bp_db.csv"))

print(f"Removed:\n {sizes}")

