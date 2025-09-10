import clr, time, sys
import threading
import argparse
import glob
from adbCommand import audioFilePlay
from toneSplitter import silenceSplitter

# Add a reference to the APx API
clr.AddReference(
    r"C:\\Program Files\\Audio Precision\\APx500 9.1\\API\\AudioPrecision.API2.dll"
)
clr.AddReference(
    r"C:\\Program Files\\Audio Precision\\APx500 9.1\\API\\AudioPrecision.API.dll"
)
from AudioPrecision.API import *


# open an existing porject or create a new project
def project_init(path=None):
    APx = APx500_Application()
    APx.Visible = True
    if path:
        APx.OpenProject(path)
    else:
        # APx.CreateNewProject()
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
        self.APx.MeasurementRecorder.SavedAcquisitionFolderName = (
            "C:\\Users\\chimtsen\\APx500_Python_Guide\\audio_report"
        )
        self.APx.MeasurementRecorder.SavedAcquisitionFileName = f"{self.fs}Hz.wav"

    def generate_report(self):
        self.APx.Sequence.Report.Checked = True
        self.APx.Sequence.Report.AutoSaveReportFileLocation = (
            "C:\\Users\\chimtsen\\APx500_Python_Guide\\audio_report"
        )
        self.APx.Sequence.Report.AutoSaveReport = False
        self.APx.Sequence.Report.ShowAutoSavedReport = True

    def dynamic_range_files(self):
        player = audioFilePlay()
        if player.play_audio("DNR_1kHz_48kHz24b2Ch.wav"):
            time.sleep(30)
            player.app_cancel()

    def measurement_recorder_files(self):
        player = audioFilePlay()
        if self.fs == "48k":
            player.play_audio("0dB_Freq_sweep_400LnPts_20HzTo24kHz_48k24b2Chs.wav")
            time.sleep(403)
            player.app_cancel()

            player.play_audio("4min_48k_multitone.wav")
            time.sleep(303)
            player.app_cancel()

        elif self.fs == "96k":
            player.play_audio("Freq_sweep_400LnPts_20HzTo48kHz_0dB_96k24b2Chs.wav")
            time.sleep(404)
            player.app_cancel()

            player.play_audio("4min_96k_multitone.wav")
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

        self.freq_sweep_48k_files = [
            "C:\\Users\\chimtsen\\APx500_Python_Guide\\audio_report\\48k_segment_result\\48k_segment_1.wav"
        ]
        self.multitone_split_48k_files = sorted(
            glob.glob(
                "C:\\Users\\chimtsen\\APx500_Python_Guide\\audio_report\\48k_segment_result\\48k_segment_*.wav"
            )[1:]
        )
        self.freq_sweep_96k_files = [
            "C:\\Users\\chimtsen\\APx500_Python_Guide\\audio_report\\96k_segment_result\\96k_segment_1.wav"
        ]
        self.multitone_split_96k_files = sorted(
            glob.glob(
                "C:\\Users\\chimtsen\\APx500_Python_Guide\\audio_report\\96k_segment_result\\96k_segment_*.wav"
            )[1:]
        )

    def choose_files(self, measurement_name: str, wav_file_path: list):
        measurement = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", measurement_name
        )
        measurement.Checked = True
        measurement.Run()

        if measurement_name in [
            "48kHz_Stepped Frequency Sweep",
            "96kHz_Stepped Frequency Sweep",
        ]:
            setting = self.APx.SteppedFrequencySweep.FileAnalysisSettings
            setting.WavFiles = wav_file_path
            self.APx.SteppedFrequencySweep.AnalyzeFiles = True
        elif measurement_name in [
            "48kHz_Multitone Analyzer",
            "96kHz_Multitone Analyzer",
        ]:
            setting = self.APx.MultitoneAnalyzer.FileAnalysisSettings
            setting.WavFiles = wav_file_path
            self.APx.MultitoneAnalyzer.AnalyzeFiles = True

    def freq_sweep_48khz(self):
        freq_sweep = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", "48kHz_Stepped Frequency Sweep"
        )
        freq_sweep.Checked = True
        self.choose_files("48kHz_Stepped Frequency Sweep", self.freq_sweep_48k_files)
        freq_sweep.Run()

    def freq_sweep_96khz(self):
        freq_sweep = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", "96kHz_Stepped Frequency Sweep"
        )
        freq_sweep.Checked = True
        self.choose_files("96kHz_Stepped Frequency Sweep", self.freq_sweep_96k_files)
        freq_sweep.Run()

    def multitone_analyzer_48khz(self):
        analyzer = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", "48kHz_Multitone Analyzer"
        )
        analyzer.Checked = True
        self.choose_files("48kHz_Multitone Analyzer", self.multitone_split_48k_files)
        analyzer.Run()

    def multitone_analyzer_96khz(self):
        analyzer = self.APx.Sequence.GetMeasurement(
            "AudioQuality_FileAnalyze", "96kHz_Multitone Analyzer"
        )
        analyzer.Checked = True
        self.choose_files("96kHz_Multitone Analyzer", self.multitone_split_96k_files)
        analyzer.Run()

    def run_sequence(self):
        if self.fs == "48k":
            self.freq_sweep_48khz()
            self.multitone_analyzer_48khz()
        if self.fs == "96k":
            self.freq_sweep_96khz()
            self.multitone_analyzer_96khz()


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

    # change the project path to yours
    APx = project_init(
        "C:\\Users\\chimtsen\\APx500_Python_Guide\\SourceAudioQualityTestTemplate.approjx"
    )

    tester = audioQualityEvkI2s(APx, args.fs)
    tester.run_sequence()

    recording_file_path = (
        f"C:\\Users\\chimtsen\\APx500_Python_Guide\\audio_report\\{args.fs}Hz.wav"
    )
    spliter = silenceSplitter(recording_file_path)
    spliter.pydub_split()

    analyzer = audioQualityFileAnalyze(APx, args.fs)
    analyzer.run_sequence()

    