import subprocess
import shutil
import time
from colorama import init, Fore, Style

init(autoreset=True)

class audioFilePlay:
    def __init__(self):
        pass

    def log(self, level, message):
        color = {
            "SUCCESS": Fore.GREEN,
            "ERROR": Fore.RED,
            "WARNING": Fore.YELLOW,
            "CHECK": Fore.CYAN,
            "RESULT": Fore.MAGENTA,
            "FAILURE": Fore.RED,
            "FOUND": Fore.BLUE
        }.get(level, Fore.WHITE)
        print(f"{color}[{level}]{Style.RESET_ALL} {message}")

    def check_adb_installed(self):
        if not shutil.which("adb"):
            self.log("ERROR", "'adb' command not found. Please install Android Platform Tools and set up your environment.")
            return False
        return True

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.log("SUCCESS", f"Executed command: {command}\nOutput:\n{result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.log("ERROR", f"Failed to execute command: {command}\nError:\n{e.stderr.strip()}")
            return None

    def check_device_connected(self):
        output = self.run_command("adb devices")
        if output:
            lines = output.strip().splitlines()
            devices = [line for line in lines[1:] if "device" in line and not line.startswith("*")]
            if devices:
                self.log("CHECK", f"Connected devices: {devices}")
                return True
            else:
                self.log("WARNING", "No devices detected. Please ensure your device is connected and USB debugging is enabled.")
        return False

    def check_root_success(self):
        output = self.run_command("adb root")
        if output and ("adbd is already running as root" in output or "restarting adbd as root" in output):
            self.log("CHECK", "adb root succeeded.")
            return True
        else:
            self.log("ERROR", "adb root failed. Device may not support root or is not unlocked.")
            return False
        
    def check_file_exists(self, folder, audioFile):
        device_path = f"/storage/emulated/0/{folder}/{audioFile}"
        check_command = f"adb shell ls {device_path}"
        check_result = self.run_command(check_command)

        if check_result and audioFile in check_result:
            self.log("FOUND", f"File found: {device_path}")
            return True
        else:
            self.log("WARNING", f"File not found in {folder}/")
            return False

    def play_audio(self, audioFile):
        if not self.check_device_connected():
            return False
        if not self.check_root_success():
            return False

        self.log("CHECK", f"Attempting to play audio file: {audioFile}")
        mime_type = "audio/wav" if audioFile.lower().endswith(".wav") else "audio/mp3"

        for folder in ["Music/Source_DUT_48kHz", "Music/48k", "Music/Source_DUT_96kHz", "Music/96k"]:
            if self.check_file_exists(folder, audioFile):
                file_path = f"file:///storage/emulated/0/{folder}/{audioFile}"
                play_command = f"adb shell am start -a android.intent.action.VIEW -d {file_path} -t {mime_type}"
                result = self.run_command(play_command)

                if result:
                    self.log("SUCCESS", f"Playback command sent for: {audioFile} in {folder}/")
                    return True
                else:
                    self.log("FAILURE", f"Found file in {folder}/ but failed to play.")
                    return False

        self.log("FAILURE", f"Audio file '{audioFile}' not found in known locations.")
        return False

    def app_cancel(self):
        package_name = "com.shaiban.audioplayer.mplayer"
        self.log("CHECK", f"Attempting to stop app: {package_name}")
        
        command = f"adb shell am force-stop {package_name}"
        result = self.run_command(command)

        if result is not None:
            self.log("SUCCESS", f"App {package_name} has been stopped.")
            return True
        else:
            self.log("FAILURE", f"Failed to stop app: {package_name}")
            return False
