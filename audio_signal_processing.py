import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, lfilter, freqz

class AudioProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.sample_rate = None
        self.data = None

    def load_audio(self):
        self.sample_rate, self.data = wavfile.read(self.filename)
        if self.data.ndim > 1:
            self.data = self.data.mean(axis=1)  # Convert to mono if stereo
        print(f"Loaded {self.filename} with sample rate: {self.sample_rate} Hz")

    def play_audio(self):
        try:
            import sounddevice as sd
            sd.play(self.data, self.sample_rate)
            sd.wait()
        except ImportError:
            print("Install sounddevice package to play audio.")

    def plot_waveform(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.data)
        plt.title("Waveform")
        plt.xlabel("Samples")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()

    def butter_filter(self, lowcut, highcut, order=5):
        nyq = 0.5 * self.sample_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a
    
    def apply_filter(self, lowcut, highcut):
        b, a = self.butter_filter(lowcut, highcut)
        self.data = lfilter(b, a, self.data)
        print(f"Applied bandpass filter with lowcut={lowcut} and highcut={highcut}")

    def compute_fft(self):
        n = len(self.data)
        freq = np.fft.rfftfreq(n, 1/self.sample_rate)
        fft_magnitude = np.abs(np.fft.rfft(self.data))
        return freq, fft_magnitude

    def plot_fft(self):
        freq, fft_magnitude = self.compute_fft()
        plt.figure(figsize=(12, 6))
        plt.plot(freq, fft_magnitude)
        plt.title("FFT of Audio Signal")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.grid()
        plt.xlim(0, 20000)  # Limit x-axis to 20 kHz for better visibility
        plt.show()

    def save_audio(self, output_filename):
        wavfile.write(output_filename, self.sample_rate, self.data.astype(np.int16))
        print(f"Saved processed audio to {output_filename}")

def main():
    input_filename = 'input.wav'  # Change to your input file
    output_filename = 'output.wav'

    audio_processor = AudioProcessor(input_filename)
    audio_processor.load_audio()
    audio_processor.plot_waveform()
    audio_processor.apply_filter(lowcut=300, highcut=3000)  # Bandpass filter
    audio_processor.plot_waveform()
    audio_processor.plot_fft()
    audio_processor.save_audio(output_filename)
    audio_processor.play_audio()

if __name__ == "__main__":
    main()