import pandas as pd
import numpy as np

def find_peak():
    df = pd.read_csv("multi.csv", skiprows=4, names=["Frequency", "dBFS"])

    df["Frequency"] = pd.to_numeric(df["Frequency"], errors="coerce")
    df["dBFS"] = pd.to_numeric(df["dBFS"], errors="coerce")
    df = df.dropna()

    df_filtered = df[(df["Frequency"] >= 15) & (df["Frequency"] <= 22300)].reset_index(drop=True)

    df_sorted = df_filtered.sort_values(by="dBFS", ascending=False).reset_index(drop=True)

    min_spacing_hz = 50
    selected_peaks = []

    for i in range(len(df_sorted)):
        freq = df_sorted.loc[i, "Frequency"]
        dbfs = df_sorted.loc[i, "dBFS"]
        if all(abs(freq - sel[0]) >= min_spacing_hz for sel in selected_peaks):
            selected_peaks.append((freq, dbfs))
        if len(selected_peaks) == 33:
            break

    print("Selected peaks with minimum spacing of 50Hz:")
    for freq, dbfs in selected_peaks:
        print(f"Frequency: {freq:.5f} Hz, dBFS: {dbfs:.2f} dB")

    return selected_peaks

def find_deviate(max_diff_db = 10.0):
    selected_peaks = find_peak()
    dbfs_values = [dbfs for _, dbfs in selected_peaks]
    max_db = max(dbfs_values)
    min_db = min(dbfs_values)
    diff = max_db - min_db

    print(f"Maximum dBFS: {max_db:.2f} dB")
    print(f"Minimum dBFS: {min_db:.2f} dB")
    print(f"deviation: {diff:.2f} dB")

    if diff <= max_diff_db:
        print("✅ pass, the deviation is less than 10 dB.")
    else:
        print("❌ failed, the deviation is more than 10 dB.")

find_deviate()


