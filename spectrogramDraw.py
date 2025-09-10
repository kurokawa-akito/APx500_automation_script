import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import os

# Function to perform spectral analysis and visualize the spectrogram
def analyze_audio_spectrum(file_path, target_freq=1000, tolerance=50):
    sample_rate, data = wav.read(file_path)

    # If stereo, convert to mono
    if len(data.shape) == 2:
        data = data.mean(axis=1)

    # Compute the FFT
    n = len(data)
    freqs = np.fft.rfftfreq(n, d=1/sample_rate)
    fft_spectrum = np.abs(np.fft.rfft(data))

    # Plot the spectrum
    plt.figure(figsize=(12, 6))
    plt.plot(freqs, fft_spectrum)
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.grid(True)

    # Highlight the 1kHz region and mark other frequencies
    plt.axvspan(target_freq - tolerance, target_freq + tolerance, color='green', alpha=0.3, label='Expected 1kHz Tone')
    plt.legend()
    plt.tight_layout()
    plt.savefig("spectrum_analysis.png")
    plt.show()

    # Identify significant non-1kHz components
    mask = (freqs < target_freq - tolerance) | (freqs > target_freq + tolerance)
    significant_freqs = freqs[mask][fft_spectrum[mask] > np.max(fft_spectrum) * 0.1]

    print("Significant non-1kHz frequency components detected:")
    for f in significant_freqs:
        print(f"{f:.1f} Hz")

# Example usage (replace 'your_audio.wav' with actual file path)
analyze_audio_spectrum("0dB_Freq_sweep_400LnPts_20HzTo24kHz_48k24b2Chs.wav")

