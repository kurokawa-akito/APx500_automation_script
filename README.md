# IOP_audio_script
## Overview
- This repository demonstrates the implementation of the Audio Precision (APx500 series) Python API for **Stepped Frequency Sweep** and **Multitone Analyzer**.
- **AudioQuality_FileAnalyze** at the following flow chart refers to the execution of both **Stepped Frequency Sweep** and **Multitone Analyzer**.
<img width="612" height="757" alt="image" src="https://github.com/user-attachments/assets/fe8b6e6f-197a-4345-8c1e-ca10ad0303bc" />


- **Python 3.6 or higher.**  
```bash
pip install -r requirements.txt
```

## toneSplitter.py
### Overview
This Python script provides tools for analyzing and segmenting WAV audio files. It includes waveform visualization and two methods for silence-based segmentation using `librosa` and `pydub`. Each detected audio segment is saved as a separate WAV file.  

⚠️ **Note:** `pydub` is recommended to use.  
⚠️ **Note:** Although `librosa` offers fast segmentation, it may alter the audio quality due to internal processing and resampling. Therefore, it is **not recommended** for splitting audio files when preserving original sound quality is important.
### Features
- 📈 Visualize waveform of the audio file using `librosa.display`
- ✂️ Split audio into segments based on silence:
  - `librosaSplitter`: Fast segmentation using `librosa.effects.split`, but may alter audio quality
  - `pydubSplitter`: Slower segmentation using `pydub.silence.split_on_silence`, preserves original audio quality
### Requirements
- Python 3.6 or higher (Python 3.12 recommended)
- Required Python packages:
  - `numpy`
  - `matplotlib`
  - `librosa`
  - `soundfile`
  - `pydub`
  - `scipy`
