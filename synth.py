import numpy as np
import pyaudio

# Define parameters
sample_rate = 44100  # Sample rate in Hz
duration = 1.0       # Duration of each note in seconds

# Define frequencies for notes (e.g., A4, B4, C5, etc.)
note_frequencies = {
    'A4': 440.00,
    'B4': 493.88,
    'C5': 523.25,
    'D5': 587.33,
    'E5': 659.25,
    'F5': 698.46,
    'G5': 783.99,
    'A5': 880.00,
}

def generate_sine_wave(frequency, duration, sample_rate):
    """Generate a sine wave for a given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

def play_wave(wave, sample_rate):
    """Play a wave using PyAudio."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    stream.write(wave.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    # Example: Play a sequence of notes
    notes = ['A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5']
    
    for note in notes:
        frequency = note_frequencies[note]
        wave = generate_sine_wave(frequency, duration, sample_rate)
        play_wave(wave, sample_rate)
