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
⚠️ Note: All paths must be absolute and accessible from the PC running APx500.  

### Mobile-side Audio Files
- class audioFilePlay in adbCommand.py
  - This module provides functionality to locate and play audio files stored on an Android device using **ADB (Android Debug Bridge)**.
- File Lookup Logic
  - The script attempts to locate the specified audio file in the following folders on the mobile device:
    1. `/storage/emulated/0/Music/Source_DUT_48kHz`
    2. `/storage/emulated/0/Music/48k`
    3. `/storage/emulated/0/Music/Source_DUT_96kHz`
    4. `/storage/emulated/0/Music/96k`
  - If the audio file is not found through these paths, the script will show a failed message.
  - If you want to place the audio file in another directory, add your desired path to the list in the for loop inside the play_audio() function:
  ```python
  for folder in ["Music/Source_DUT_48kHz", "Music/48k"]:
  ```

#### Example Folder Structure on Device
/storage/emulated/0/  
├── Music/  
│   ├── Source_DUT_48kHz/  
│   │   └── test_tone.wav  
│   ├── 48k/  
│   │   └── test_tone.wav  

---
## Usage
Run the script from the command line:  
```bash
python audio_quality_test.py --fs 48k
```
Options:   
--fs: Sampling rate, either 48k or 96k.  

### Optional 
#### Disable Report Display
If you do not want to show the report after the test, comment out the following line in audioQualityEvkI2s.run_sequence():  
```python
self.generate_report()
```
This will prevent the APx500 GUI from displaying the report.

---
## Note
- The device must be connected via USB and accessible through ADB.
- Root access is required for certain operations (e.g., stopping playback).
- Audio files must be preloaded into one of the known folders on the device.
- If the file is not found in either folder, playback will fail and a warning will be logged.
