import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import Scale
from scipy.signal import sawtooth, square

# Global variables
sample_rate = 44100  # Audio sample rate
duration = 2.0      # Duration of the note in seconds
frequency = 440     # Default frequency (A4 note)

# Function to generate ADSR envelope
# FIX
def generate_adsr_envelope(attack, decay, sustain, release, sample_rate, note_length):
    attack_samples = int(sample_rate * attack)
    decay_samples = int(sample_rate * decay)
    sustain_samples = int(sample_rate * note_length) - attack_samples - decay_samples
    release_samples = int(sample_rate * release)

    envelope = np.concatenate([
        np.linspace(0, 1, attack_samples),  # Attack
        np.linspace(1, sustain, decay_samples),  # Decay
        np.full(sustain_samples, sustain),  # Sustain
        np.linspace(sustain, 0, release_samples)  # Release
    ])
    return envelope[:int(sample_rate * note_length)]

# Oscillator functions
def sine_wave(freq, t):
    return np.sin(freq * t * 2 * np.pi)

def sawtooth_wave(freq, t):
    return sawtooth(2 * np.pi * freq * t)

def square_wave(freq, t):
    return square(2 * np.pi * freq * t)

# Function to play waveform with ADSR
def play_wave_with_adsr(wave_function, freq, attack, decay, sustain, release, duration=duration):
    envelope = generate_adsr_envelope(attack, decay, sustain, release, sample_rate, duration)
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = wave_function(freq, t)
    modulated_wave = wave * envelope[:len(wave)]  # Apply the envelope to the wave
    sd.play(modulated_wave, samplerate=sample_rate)
    sd.wait()

# Function to calculate note frequencies based on chromatic scale
def get_frequency(note_index, base_octave):
    A4_index = 0
    A4_frequency = 440
    return A4_frequency * (2 ** ((note_index - A4_index + (base_octave - 4) * 12) / 12))

# Function to play waveform with ADSR based on keyboard input
def play_waveform_with_adsr(waveform, freq):
    play_wave_with_adsr(
        waveform, freq,
        attack_slider.get(), decay_slider.get(),
        sustain_slider.get(), release_slider.get()
    )

# Creating the GUI
window = tk.Tk()
window.title("Software Synthesizer with ADSR")

# ADSR parameter sliders
attack_slider = Scale(window, from_=0, to=1, resolution=0.01, label="Attack")
attack_slider.pack()
decay_slider = Scale(window, from_=0, to=1, resolution=0.01, label="Decay")
decay_slider.pack()
sustain_slider = Scale(window, from_=0, to=1, resolution=0.01, label="Sustain")
sustain_slider.pack()
release_slider = Scale(window, from_=0, to=1, resolution=0.01, label="Release")
release_slider.pack()

# Octave selection widget
octave_slider = Scale(window, from_=0, to=8, resolution=1, label="Octave", orient=tk.HORIZONTAL)
octave_slider.set(4)  # Default to the 4th octave
octave_slider.pack()

# Current waveform variable and function
current_waveform = sine_wave

def set_waveform(waveform):
    global current_waveform
    current_waveform = waveform

# Waveform buttons
sine_button = tk.Button(window, text="Sine Wave", command=lambda: set_waveform(sine_wave))
sine_button.pack()
sawtooth_button = tk.Button(window, text="Sawtooth Wave", command=lambda: set_waveform(sawtooth_wave))
sawtooth_button.pack()
square_button = tk.Button(window, text="Square Wave", command=lambda: set_waveform(square_wave))
square_button.pack()

# Keyboard event handling
def on_key_press(event):
    key_mapping = {'a': 0, 'w': 1, 's': 2, 'e': 3, 'd': 4, 'f': 5, 't': 6, 'g': 7, 'y': 8, 'h': 9, 'u': 10, 'j': 11}
    if event.char in key_mapping:
        note_index = key_mapping[event.char]
        freq = get_frequency(note_index, octave_slider.get())
        play_waveform_with_adsr(current_waveform, freq)

window.bind("<KeyPress>", on_key_press)

# Run the GUI
window.mainloop()
