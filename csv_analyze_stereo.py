import pandas as pd
import numpy as np

# Load the CSV file
df = pd.read_csv("multi_all.csv", skiprows=4)

# Function to find 32 peaks with minimum spacing of 50Hz from frequency and dBFS rows
def find_peaks_from_rows(freq_row, dbfs_row, min_spacing_hz=50):
    freq = pd.to_numeric(freq_row, errors="coerce")
    dbfs = pd.to_numeric(dbfs_row, errors="coerce")
    df = pd.DataFrame({"Frequency": freq, "dBFS": dbfs}).dropna()
    df = df[(df["Frequency"] >= 15) & (df["Frequency"] <= 22300)]
    df_sorted = df.sort_values(by="dBFS", ascending=False).reset_index(drop=True)

    selected_peaks = []
    for i in range(len(df_sorted)):
        f = df_sorted.loc[i, "Frequency"]
        d = df_sorted.loc[i, "dBFS"]
        if all(abs(f - sel[0]) >= min_spacing_hz for sel in selected_peaks):
            selected_peaks.append((f, d))
        if len(selected_peaks) == 32:
            break
    return selected_peaks

# Function to check peak-to-peak deviation

def check_peak_to_peak(peaks):
    dbfs_values = [d for _, d in peaks]
    max_db = max(dbfs_values)
    min_db = min(dbfs_values)
    diff = max_db - min_db
    return max_db, min_db, diff, diff <= 10.0

# Analyze each stereo path
results = []
for i in range(0, 16, 2):
    freq_row = df.iloc[i]
    dbfs_row = df.iloc[i + 1]
    peaks = find_peaks_from_rows(freq_row, dbfs_row)
    if len(peaks) == 32:
        max_db, min_db, diff, status = check_peak_to_peak(peaks)
        results.append((f"Channel {(i//2)+1}", max_db, min_db, diff, status))
    else:
        results.append((f"Channel {(i//2)+1}", None, None, None, False))

# Print results
for ch, max_db, min_db, diff, status in results:
    if max_db is not None:
        verdict = "✅ OK" if status else "❌ NG"
        print(f"{ch}: {verdict} (Max: {max_db:.2f} dB, Min: {min_db:.2f} dB, Diff: {diff:.2f} dB)")
    else:
        print(f"{ch}: ❌ Failed to extract 32 peaks")
