# Audio Quality Test Automation
## Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [File Path Configuration](#file-path-configuration)
- [Usage](#usage)
- [Note](#note)
## Overview
- This repository demonstrates the implementation of the Audio Precision (APx500 series) Python API for **Stepped Frequency Sweep** and **Multitone Analyzer**.
- In `audio_quality_test.py`, **AudioQuality_FileAnalyze** at the following flow chart refers to the execution of both **Stepped Frequency Sweep** and **Multitone Analyzer**.
- `csv_analyze.py` analyzes multitone test data from raw CSV files to evaluate audio signal quality across multiple channels. It supports both 48kHz and 96kHz sampling rates and extracts peak frequency components to compute metrics such as maximum dBFS, minimum dBFS, deviation, and tone bin matching.
- **Python 3.6 or higher.**  
```bash
pip install -r requirements.txt
```
![alt text](/image/flow_chart.png)
---
## Features
- **AudioQuality_EVK_I2S**
  - Plays test tones from a mobile device via ADB.
  - Measures dynamic range and records stepped frequency sweep and multitone using APx500.
  - Automatically saves acquisition files.

- **tone_splitter**
  - Splits recorded audio into segments.
  - `manualSplitter.split_sweep_only()`: Extracts the first 6 minutes and 43 seconds of the audio as the stepped frequency sweep, and outputs the remaining multitone segment.
  - `silenceSplitter.pydub_split()`: Splits the multitone segment based on silence detection.  
  **💡Note: Silence is detected based on dBFS values, if the segmentation is incomplete, try the following:**    
    - Set the phone volume to maximum.
    - Adjust the `silence_thresh` parameter in the following code:  
    ```python
    chunks = split_on_silence(
        sound, min_silence_len=800, silence_thresh=sound.dBFS - 35, keep_silence=300
    )
    ```
- **AudioQuality_FileAnalyze**
  - Performs stepped frequency sweep and multitone analysis on segmented files.
- **csv_analyze.py**
  - **Peak Detection**: 
    - Supports 48kHz and 96kHz multitone analysis:
      - **48kHz mode**: Identifies the top 32 frequency peaks per channel within the 15 Hz to 22,300 Hz range.
      - **96kHz mode**: selects 64 peaks within 20Hz–45kHz and checks if the 60th peak falls within expected FFT bins.
  - **Deviation Analysis**: Calculates deviation between the strongest frequency and the 32nd strongest frequency.
  - **Pass/Fail Evaluation**: Flags with deviation greater than 10 dB as failed.
  - **Example output**:  
  For 48kHz, it can evaluate the following test items:  
    - All 32 left and right channel tones in the frequency range, 20Hz to 22kHz are represented.
    - The multitone peaks should not deviate from the expected level by more than 10dB.  
    ```
    48k Multitone 1_1 => Max: -40.05707 dB, Min: -48.05158 dB, 32nd tone bin: 121651(✅), Deviation: 7.99 dB ✅ Pass
    48k Multitone 1_2 => Max: -40.22347 dB, Min: -47.98895 dB, 32nd tone bin: 120739(✅), Deviation: 7.77 dB ✅ Pass
    48k Multitone 2_1 => Max: -40.03152 dB, Min: -48.29088 dB, 32nd tone bin: 121651(✅), Deviation: 8.26 dB ✅ Pass
    ...
    ```
    For 96kHz:
      - The 1st 60 out of 64 left and right channel tones in the frequency range, 20Hz to 42kHz are represented.
      - The multitone peaks in the frequency range, 20Hz to 40kHz should not deviate from the expected level by more than 10dB.
    ```
    96k Multitone 1_1 => Max: -35.45878 dB, Min dBFS at 20hz~40khz: -50.60499 dB, 60th tone bin: 114786(✅), Deviation: 15.15 dB ❌ Fail
    96k Multitone 1_2 => Max: -35.47156 dB, Min dBFS at 20hz~40khz: -50.67706 dB, 60th tone bin: 113089(✅), Deviation: 15.21 dB ❌ Fail
    96k Multitone 2_1 => Max: -35.40577 dB, Min dBFS at 20hz~40khz: -44.66262 dB, 60th tone bin: 114785(✅), Deviation: 9.26 dB ✅ Pass
    ...
    ```

---
## Requirements
- **Audio Precision APx500** version **8.1** or **9.1** installed.
- Python 3.6+
- `pythonnet` (`clr` module) for .NET API integration.
- APx500 API DLLs located at:
```
C:\Program Files\Audio Precision\APx500 9.1\API\
```
- [Controlling APx500 Software with Python](https://www.ap.com/blog/controlling-apx500-software-using-python)
- [Download APx500 Python API](https://www.ap.com/fileadmin-ap/technical-library/APx500_Python_Guide.zip)

---
## File Path Configuration
### PC-side Paths
Ensure the following paths are correctly set in `audio_quality_paths.json`:  
```json
{
    "project_path": "C:/path/to/your/project.approjx",
    "report_folder": "C:/path/to/save/report",
    "recording_file": {
        "48k": "C:/path/to/recorded_48k.wav",
        "96k": "C:/path/to/recorded_96k.wav"
    },
    "segment_result_folder": {
        "48k": "C:/path/to/segments_48k",
        "96k": "C:/path/to/segments_96k"
    },
    "csv_raw_data_files": {
        "48k": "path/to/your/48k_data.csv",
        "96k": "path/to/your/96k_data.csv"
    }
}
```

### Mobile-side Audio Files
```python
adb_command.audioFilePlay.play_audio()
```
- This function attempts to play a specified audio file on a connected Android device using ADB. It checks multiple predefined folders under `/storage/emulated/0/` to locate the file.
- File Lookup Logic :
  - Loop through each folder listed in the `audio_quality_paths.json` under `playback_folders`.
  - Check if the audio file exists in that folder using `adb shell ls`.
  - If found, send an intent to play the file using:
    ```
    adb shell am start -a android.intent.action.VIEW -d file://... -t audio/wav
    ```
  - The folders to be searched are defined in the `audio_quality_paths.json` under the key `playback_folders`. Example:
    ```json
    "playback_folders": [
        "Music",
        "Music/Source_DUT_48kHz",
        "Music/48k",
        "Music/Source_DUT_96kHz",
        "Music/96k"
    ]
    ```
  - These paths are relative to `/storage/emulated/0/`. The function will automatically check each of them in order until the file is found.  
  **💡 The `playback_folders` above are just default paths. You can modify them yourself in `audio_quality_paths.json`.**
  - The filenames of **dynamic range**, **stepped frequency sweep** and **multitone** used for the audio quality test can be modified in `audio_quality_paths.json`:
    ```json
    "dynamic_range_file": {
          "48k": "DNR_1kHz_48kHz24b2Ch.wav",
          "96k": "DNR_1kHz_96kHz24b2Ch.wav"
      },
      "measurement_recorder_files": {
          "48k": [
              "0dB_Freq_sweep_400LnPts_20HzTo24kHz_48k24b2Chs.wav",
              "4min_recording_48k_multitone.wav"
          ],
          "96k": [
              "0dB_Freq_sweep_400LnPts_20HzTo48kHz_96k24b2Chs.wav",
              "4min_96k_multitone.wav"
          ]
      },
    ```

#### Example Folder Structure on Device
```
/storage/emulated/0/  
├── Music/  
│   ├── Source_DUT_48kHz/  
│   │   └── test_tone.wav  
│   ├── 48k/  
│   │   └── test_tone.wav  
│   ├── Source_DUT_96kHz/  
│   │   └── test_tone.wav  
│   ├── 96k/  
│   │   └── test_tone.wav  
```

---
## Usage
Run the script from the command line:  
- For Audio Quality Testing:
  ```bash
  python audio_quality_test.py --fs 48k --step 1 2 3
  ```
    - **1** = audioQualityEvkI2s, **2** = manual+silenceSplitter, **3** = audioQualityFileAnalyze
    - If you only want to execute specific steps, you can run:
    ```bash
    python audio_quality_test.py --fs 48k --step 1
    ```
    or
    ```bash
    python audio_quality_test.py --fs 48k --step 2 3
    ```
- check the the usage of parameters:
  ```bash
  python audio_quality_test.py --help
  ```
- For multitone raw data analyzing:
  ```bash
  python csv_analyze.py --fs 48k
  ```
  or
  ```bash
  python your_script.py --fs 96k
  ```
Options:   
--fs: Sampling rate, either 48k or 96k.  

### Optional 
#### Report Saving & Display Behavior
audio_quality_test.audioQualityEvkI2s.generate_report() configures how the APx500 report is handled:
```python
def generate_report(self):
    self.APx.Sequence.Report.Checked = False
    self.APx.Sequence.Report.AutoSaveReportFileLocation = paths["report_folder"]
    self.APx.Sequence.Report.AutoSaveReport = False
    self.APx.Sequence.Report.ShowAutoSavedReport = False
```
- Enables report generation
- Sets the folder path for saving reports
- `AutoSaveReport`:  
  - `True` → Automatically saves the report after the sequence runs  
  - `False` → Does not save the report automatically
- `Report.Checked`:  
  - `True` → Opens the report automatically after testing  
  - `False` → Does not open the report after testing

---
## Note
- Debug mode must be enabled on the Android device to allow external communication.
- Root access is required for certain operations (e.g., stopping playback).
- Audio files must be preloaded into one of the known folders on the device.
- If the file is not found in either folder, playback will fail and a warning will be logged.
- CSV files should be formatted correctly, with valid data starting from row 5 (skiprows=4).
