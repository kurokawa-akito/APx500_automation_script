import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence

with open("audio_quality_paths.json", "r") as f:
    paths = json.load(f)

class wavFileAnalysis:
    def __init__(self, audio_path):
        self.audio_path = audio_path

    def draw_waveform(self):
        y, sr = librosa.load(self.audio_path)

        # draw
        plt.figure()
        librosa.display.waveshow(y, sr=sr)
        plt.title("nutcracker waveform")
        plt.show()


# fast, but quality sounds strange
class librosaSplitter:
    def __init__(self, audio_path, top_db=30):
        self.audio_path = audio_path
        self.top_db = top_db

    def librosa_split(self):
        y, sr = librosa.load(self.audio_path, sr=None)

        intervals = librosa.effects.split(y, top_db=self.top_db)
        print(f"detect {len(intervals)} voices")

        filename = os.path.basename(self.audio_path)
        if "48k" in filename:
            prefix = "48k_segment"
        elif "96k" in filename:
            prefix = "96k_segment"

        for i, (start, end) in enumerate(intervals):
            segment = y[start:end]
            output_filename = f"{prefix}_{i+1}.wav"
            sf.write(output_filename, segment, sr)
            print(f"saved: {output_filename}")


# slower than librosa, but quality sounds same as original tone
class silenceSplitter:
    def __init__(self, audio_path):
        self.audio_path = audio_path

    def pydub_split(self):
        sound = AudioSegment.from_wav(self.audio_path)

        filename = os.path.basename(self.audio_path)
        if "48k" in filename:
            prefix = "48k_segment"
            output_dir = paths["segment_result_folder"]["48k"]
        elif "96k" in filename:
            prefix = "96k_segment"
            output_dir = paths["segment_result_folder"]["96k"]
        else:
            raise ValueError(
                "Filename must contain '48k' or '96k' to determine output folder."
            )

        os.makedirs(output_dir, exist_ok=True)

        chunks = split_on_silence(
            sound, min_silence_len=800, silence_thresh=sound.dBFS - 35, keep_silence=300
        )

        for i, chunk in enumerate(chunks):
            out_file = os.path.join(output_dir, f"{prefix}_{i+1}.wav")
            chunk.export(out_file, format="wav")
            print(f"save as: {out_file}")


class manualSplitter:
    def __init__(self, audio_path):
        self.audio_path = audio_path
        self.sound = AudioSegment.from_wav(audio_path)

    def split_audio(self):
        filename = os.path.basename(self.audio_path)
        if "48k" in filename:
            prefix = "48k_segment"
            output_dir = paths["segment_result_folder"]["48k"]
        elif "96k" in filename:
            prefix = "96k_segment"
            output_dir = paths["segment_result_folder"]["96k"]
        else:
            raise ValueError(
                "Filename must contain '48k' or '96k' to determine output folder."
            )
        os.makedirs(output_dir, exist_ok=True)

        segments = []
        sweep_start = 0
        sweep_end = (6 * 60 + 43) * 1000
        segments.append((sweep_start, sweep_end))

        first_multitone_start = (7 * 60 + 44) * 1000
        for i in range(8):
            start = first_multitone_start + i * (16000 + 14000)
            end = start + 16000
            segments.append((start, end))

        for i, (start, end) in enumerate(segments):
            chunk = self.sound[start:end]
            out_file = os.path.join(output_dir, f"{prefix}_{i+1}.wav")
            chunk.export(out_file, format="wav")
            print(f"Saved: {out_file}")

