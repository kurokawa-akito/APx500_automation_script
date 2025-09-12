# Audio Quality Test Automation
## Overview
- This repository demonstrates the implementation of the Audio Precision (APx500 series) Python API for **Stepped Frequency Sweep** and **Multitone Analyzer**.
- **AudioQuality_FileAnalyze** at the following flow chart refers to the execution of both **Stepped Frequency Sweep** and **Multitone Analyzer**.
- **Python 3.6 or higher.**  
```bash
pip install -r requirements.txt
```
---
## Features
- **AudioQuality_EVK_I2S**
  - Plays test tones from a mobile device via ADB.
  - Measures dynamic range and records audio using APx500.
  - Automatically saves acquisition files.

- **AudioQuality_FileAnalyze**
  - Splits recorded audio into segments.
  - Performs stepped frequency sweep and multitone analysis on segmented files.

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
    }
}
```

### Mobile-side Audio Files
```python
adb_command.audioFilePlay.play_audio()
```
  - This function attempts to play a specified audio file on a connected Android device using ADB. It checks multiple predefined folders under `/storage/emulated/0/` to locate the file.
- File Lookup Logic
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
  - **💡 The `playback_folders` above are just default paths. You can modify them yourself in `audio_quality_paths.json`.**

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
```bash
python audio_quality_test.py --fs 48k
```
Options:   
--fs: Sampling rate, either 48k or 96k.  

### Optional 
#### Report Saving & Display Behavior
audio_quality_test.audioQualityEvkI2s.generate_report() configures how the APx500 report is handled:
```python
def generate_report(self):
    self.APx.Sequence.Report.Checked = True
    self.APx.Sequence.Report.AutoSaveReportFileLocation = paths["report_folder"]
    self.APx.Sequence.Report.AutoSaveReport = False
    self.APx.Sequence.Report.ShowAutoSavedReport = True
```
- Enables report generation
- Sets the folder path for saving reports
- `AutoSaveReport`:  
  - `True` → Automatically saves the report after the sequence runs  
  - `False` → Does not save the report automatically
- `ShowAutoSavedReport`:  
  - `True` → Opens the report automatically after testing  
  - `False` → Does not open the report after testing

---
## Note
- The device must be connected via USB and accessible through ADB.
- Root access is required for certain operations (e.g., stopping playback).
- Audio files must be preloaded into one of the known folders on the device.
- If the file is not found in either folder, playback will fail and a warning will be logged.
