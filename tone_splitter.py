import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence

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


# slower than librosa, but quality sounds same as original tone
class silenceSplitter:
    def __init__(self, audio_path, paths):
        self.audio_path = audio_path
        self.paths = paths

    def pydub_split(self):
        sound = AudioSegment.from_wav(self.audio_path)

        filename = os.path.basename(self.audio_path)
        if "48k" in filename:
            prefix = "48k"
            output_dir = self.paths["segment_result_folder"]["48k"]
        elif "96k" in filename:
            prefix = "96k"
            output_dir = self.paths["segment_result_folder"]["96k"]
        else:
            raise ValueError(
                "Filename must contain '48k' or '96k' to determine output folder."
            )
        os.makedirs(output_dir, exist_ok=True)
        sweep_path = os.path.join(output_dir, f"{prefix}_freq_sweep.wav")
        sweep_exists = os.path.exists(sweep_path)

        chunks = split_on_silence(
            sound, min_silence_len=800, silence_thresh=sound.dBFS - 35, keep_silence=0
        )
        
        for i, chunk in enumerate(chunks):
            if not sweep_exists and i == 0:
                out_file = os.path.join(output_dir, f"{prefix}_freq_sweep.wav")
            else:
                index = i + 1 if sweep_exists else i
                out_file = os.path.join(output_dir, f"{prefix}_multitone_{index}.wav")
            chunk.export(out_file, format="wav")
            print(f"Save as: {out_file}")


class manualSplitter:
    def __init__(self, audio_path, paths):
        self.audio_path = audio_path
        self.paths = paths
        self.sound = AudioSegment.from_wav(audio_path)

    def split_sweep_only(self):
            filename = os.path.basename(self.audio_path)
            if "48k" in filename:
                prefix = "48k"
                output_dir = self.paths["segment_result_folder"]["48k"]
            elif "96k" in filename:
                prefix = "96k"
                output_dir = self.paths["segment_result_folder"]["96k"]
            else:
                raise ValueError(
                    "Filename must contain '48k' or '96k' to determine output folder."
                )
            os.makedirs(output_dir, exist_ok=True)

            sweep_end = (6 * 60 + 44) * 1000
            sweep_segment = self.sound[:sweep_end]

            out_file = os.path.join(output_dir, f"{prefix}_freq_sweep.wav")
            sweep_segment.export(out_file, format="wav")
            print(f"Saved as: {out_file}")

            remaining_audio_path = os.path.join(output_dir, f"{prefix}_recording_multitone.wav")
            remaining_segment = self.sound[sweep_end:]
            remaining_segment.export(remaining_audio_path, format="wav")

            return remaining_audio_path
