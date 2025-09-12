import clr, time, sys
import threading
import argparse
import glob
import json
from adb_command import audioFilePlay
from tone_splitter import silenceSplitter

# Add a reference to the APx API
clr.AddReference(
    r"C:\\Program Files\\Audio Precision\\APx500 9.1\\API\\AudioPrecision.API2.dll"
)
clr.AddReference(
    r"C:\\Program Files\\Audio Precision\\APx500 9.1\\API\\AudioPrecision.API.dll"
)
from AudioPrecision.API import *

with open("audio_quality_paths.json", "r") as f:
    paths = json.load(f)


def project_init(path=None):
    APx = APx500_Application()
    APx.Visible = True
    if path:
        APx.OpenProject(path)
    else:
        print(f"file path not exist")
    return APx


class audioQualityEvkI2s:
    def __init__(self, APx, fs):
        self.APx = APx
        self.fs = fs  # sample rate

    def dynamic_range(self):
        DNR = self.APx.Sequence.GetMeasurement(
            "AudioQuality_EVK_I2S", "Dynamic Range - AES17"
        )
        DNR.Checked = True
        DNR.Run()

    def measurement_recorder(self):
        recorder = self.APx.Sequence.GetMeasurement(
            "AudioQuality_EVK_I2S", "Measurement Recorder"
        )
        recorder.Checked = True
        recorder.Run()
        self.APx.MeasurementRecorder.SaveAcquisitionToFile = True
        self.APx.MeasurementRecorder.SavedAcquisitionFolderName = paths["report_folder"]
        self.APx.MeasurementRecorder.SavedAcquisitionFileName = f"{self.fs}Hz.wav"

    def generate_report(self):
        self.APx.Sequence.Report.Checked = True
        self.APx.Sequence.Report.AutoSaveReportFileLocation = paths["report_folder"]
        self.APx.Sequence.Report.AutoSaveReport = False
        self.APx.Sequence.Report.ShowAutoSavedReport = True

    def dynamic_range_files(self):
        player = audioFilePlay()
        if player.play_audio(paths["dynamic_range_file"]):
            time.sleep(30)
            player.app_cancel()

    def measurement_recorder_files(self):
        player = audioFilePlay()
        if self.fs == "48k":
            player.play_audio(paths["measurement_recorder_files"]["48k"][0])
            time.sleep(403)
            player.app_cancel()

            player.play_audio(paths["measurement_recorder_files"]["48k"][1])
            time.sleep(303)
            player.app_cancel()

        elif self.fs == "96k":
            player.play_audio(paths["measurement_recorder_files"]["96k"][0])
            time.sleep(404)
            player.app_cancel()

            player.play_audio(paths["measurement_recorder_files"]["96k"][1])
            time.sleep(306)
            player.app_cancel()

    def run_sequence(self):
        self.generate_report()

        DNR_thread = threading.Thread(target=self.dynamic_range)
        DNR_player_thread = threading.Thread(target=self.dynamic_range_files)

        DNR_player_thread.start()
        DNR_thread.start()

        DNR_player_thread.join()
        DNR_thread.join()

        recorder_thread = threading.Thread(target=self.measurement_recorder)
        player_thread = threading.Thread(target=self.measurement_recorder_files)

        recorder_thread.start()
        player_thread.start()

        recorder_thread.join()
        player_thread.join()


class audioQualityFileAnalyze:
    def __init__(self, APx, fs):
        self.APx = APx
        self.fs = fs

        segment_folder = paths["segment_result_folder"][self.fs]
        self.freq_sweep_files = [f"{segment_folder}/{self.fs}_segment_1.wav"]
        self.multitone_files = sorted(
            glob.glob(f"{segment_folder}/{self.fs}_segment_*.wav")
        )[1:]

    def choose_files(self, measurement_name: str, wav_file_path: list):
        measurement = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", measurement_name
        )
        measurement.Checked = True
        measurement.Run()

        if measurement_name == f"{self.fs}Hz_Stepped Frequency Sweep":
            setting = self.APx.SteppedFrequencySweep.FileAnalysisSettings
            setting.WavFiles = wav_file_path
            self.APx.SteppedFrequencySweep.AnalyzeFiles = True

        elif measurement_name == f"{self.fs}Hz_Multitone Analyzer":
            setting = self.APx.MultitoneAnalyzer.FileAnalysisSettings
            setting.WavFiles = wav_file_path
            self.APx.MultitoneAnalyzer.AnalyzeFiles = True

    def freq_sweep(self):
        measurement_name = f"{self.fs}Hz_Stepped Frequency Sweep"
        freq_sweep = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", measurement_name
        )
        freq_sweep.Checked = True
        self.choose_files(measurement_name, self.freq_sweep_files)
        freq_sweep.Run()

    def multitone_analyzer(self):
        measurement_name = f"{self.fs}Hz_Multitone Analyzer"
        analyzer = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", measurement_name
        )
        analyzer.Checked = True
        self.choose_files(measurement_name, self.multitone_files)
        analyzer.Run()

    def run_sequence(self):
        self.freq_sweep()
        self.multitone_analyzer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Quality Test")
    parser.add_argument(
        "--fs",
        type=str,
        choices=["48k", "96k"],
        default="48k",
        help="Sampling rate (48k or 96k)",
    )
    args = parser.parse_args()

    APx = project_init(paths["project_path"])

    # tester = audioQualityEvkI2s(APx, args.fs)
    # tester.run_sequence()

    recording_file_path = paths["recording_file"][args.fs]
    spliter = silenceSplitter(recording_file_path)
    spliter.pydub_split()

    analyzer = audioQualityFileAnalyze(APx, args.fs)
    analyzer.run_sequence()
