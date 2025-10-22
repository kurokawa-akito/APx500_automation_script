import pandas as pd
import numpy as np
import json
import argparse


def find_peak_48k(df, channel_index):
    freq_col = df.columns[channel_index * 2]
    dbfs_col = df.columns[channel_index * 2 + 1]

    freq = pd.to_numeric(df[freq_col], errors="coerce")
    dbfs = pd.to_numeric(df[dbfs_col], errors="coerce")
    df_pair = pd.DataFrame({"Frequency": freq, "dBFS": dbfs}).dropna()

    df_filtered = df_pair[
        (df_pair["Frequency"] >= 15) & (df_pair["Frequency"] <= 22300)
    ].reset_index(drop=True)
    df_sorted = df_filtered.sort_values(by="dBFS", ascending=False).reset_index(
        drop=True
    )

    min_spacing_hz = 50
    selected_peaks = []
    for j in range(len(df_sorted)):
        freq_val = df_sorted.loc[j, "Frequency"]
        dbfs_val = df_sorted.loc[j, "dBFS"]
        if all(abs(freq_val - sel[0]) >= min_spacing_hz for sel in selected_peaks):
            selected_peaks.append((freq_val, dbfs_val))
        if len(selected_peaks) == 32:
            break

    dbfs_values = [dbfs for _, dbfs in selected_peaks]
    max_db = max(dbfs_values)
    min_db = min(dbfs_values)
    deviation = max_db - min_db

    selected_peaks_sorted = sorted(selected_peaks, key=lambda x: x[0])
    fs = 48000
    fft_size = 262144
    bin_width = fs / fft_size
    peak_freq = selected_peaks_sorted[31][0]
    tone_bin = round(peak_freq / bin_width)
    expected_bins = [121651, 120739]
    tolerance = 100
    bin_match = any(
        abs(tone_bin - expected_bin) <= tolerance for expected_bin in expected_bins
    )

    return {
        "Max_dBFS": round(max_db, 5),
        "Min_dBFS": round(min_db, 5),
        "Deviation_dB": round(deviation, 2),
        "Deviation Pass": deviation <= 10.0,
        "Tone Bin": tone_bin,
        "Bin Match": "✅" if bin_match else "❌",
    }


def find_peak_96k(df, channel_index):
    freq_col = df.columns[channel_index * 2]
    dbfs_col = df.columns[channel_index * 2 + 1]

    freq = pd.to_numeric(df[freq_col], errors="coerce")
    dbfs = pd.to_numeric(df[dbfs_col], errors="coerce")
    df_pair = pd.DataFrame({"Frequency": freq, "dBFS": dbfs}).dropna()

    df_filtered = df_pair[
        (df_pair["Frequency"] >= 20) & (df_pair["Frequency"] <= 45000)
    ].reset_index(drop=True)
    df_sorted = df_filtered.sort_values(by="dBFS", ascending=False).reset_index(
        drop=True
    )

    min_spacing_hz = 50
    selected_peaks = []
    for _, row in df_sorted.iterrows():
        freq_val = row["Frequency"]
        dbfs_val = row["dBFS"]
        if all(abs(freq_val - sel[0]) >= min_spacing_hz for sel in selected_peaks):
            selected_peaks.append((freq_val, dbfs_val))
        if len(selected_peaks) == 64:
            break

    selected_peaks_sorted = sorted(selected_peaks, key=lambda x: x[0])

    filtered_peaks = [peak for peak in selected_peaks_sorted if 20 <= peak[0] <= 40000]
    # Calculate max, min, and deviation
    if filtered_peaks:
        dbfs_values = [peak[1] for peak in filtered_peaks]
        max_db = max(dbfs_values)
        min_db = min(dbfs_values)
        deviation = max_db - min_db
    else:
        max_db = min_db = deviation = float("nan")

    fs = 96000
    fft_size = 262144
    bin_width = fs / fft_size
    peak_freq = selected_peaks_sorted[59][0]
    tone_bin = round(peak_freq / bin_width)
    expected_bins = [114785, 113077]
    tolerance = 100
    bin_match = any(
        abs(tone_bin - expected_bin) <= tolerance for expected_bin in expected_bins
    )

    return {
        "Max_dBFS": round(max_db, 5),
        "Min_dBFS": round(min_db, 5),
        "Deviation_dB": round(deviation, 2),
        "Deviation Pass": deviation <= 10.0,
        "Tone Bin": tone_bin,
        "Bin Match": "✅" if bin_match else "❌",
    }


def run(fs):
    with open("audio_quality_paths.json", "r") as f:
        paths = json.load(f)

    df = pd.read_csv(paths["csv_raw_data_files"][fs], skiprows=4)
    results = {}

    for i in range(16):
        if fs == "96k":
            result = find_peak_96k(df, i)
        else:
            result = find_peak_48k(df, i)
        results[f"Channel_{i+1}"] = result

    for i, res in enumerate(results.values()):
        pair_num = i // 2 + 1
        sub_num = i % 2 + 1
        label = f"{fs} Multitone {pair_num}_{sub_num}"

        if "Error" in res:
            print(f"{label} => ⚠️ {res['Error']}")
        else:
            min_label = res["Min_dBFS"]

            if fs == "48k":
                output = f"{label} => Max: {res['Max_dBFS']} dB, Min: {min_label} dB"
                output += f", 32nd tone bin: {res['Tone Bin']}({res['Bin Match']})"
            else:
                output = f"{label} => Max: {res['Max_dBFS']} dB, Min dBFS at 20hz~40khz: {min_label} dB, 60th tone bin: {res['Tone Bin']}({res['Bin Match']})"
            output += f", Deviation: {res['Deviation_dB']} dB"
            output += " ✅ Pass" if res["Deviation Pass"] else " ❌ Fail"

            print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multitone raw data analyze")
    parser.add_argument(
        "--fs",
        type=str,
        choices=["48k", "96k"],
        default="48k",
        help="Sampling rate (48k or 96k)",
    )
    args = parser.parse_args()

    run(args.fs)
