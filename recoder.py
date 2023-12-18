import time
import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
from scipy.io.wavfile import write as write_wav


class VoiceRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recorder")

        self.is_recording = False
        self.recording_stream = None
        self.recorded_data = []

        # Create frames for organization
        frame1 = ttk.Frame(root)
        frame1.pack(padx=10, pady=10)

        frame2 = ttk.Frame(root)
        frame2.pack(padx=10, pady=10)

        # Put widgets in the frames
        self.record_button = ttk.Button(frame1, text="Record", command=self.toggle_recording)
        self.save_button = ttk.Button(frame1, text="Save", command=self.save_recording)
        self.timer_label = ttk.Label(frame2, text="Recording Time: 0s")
        self.status_label = ttk.Label(frame2, text="Status: Not Recording")

        self.record_button.grid(row=0, column=0, padx=5)
        self.save_button.grid(row=0, column=1, padx=5)
        self.timer_label.grid(row=0, column=0, padx=5)
        self.status_label.grid(row=0, column=1, padx=5)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="Stop Recording")
        self.status_label.config(text="Status: Recording")
        self.recording_stream = sd.InputStream(callback=self.callback)
        self.recording_stream.start()
        self.start_timer()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Record")
        self.status_label.config(text="Status: Not Recording")
        if self.recording_stream:
            self.recording_stream.stop()
            self.recording_stream.close()
        self.stop_timer()

    def callback(self, indata, frames, time, status):
        if status:
            print("Error in recording:", status)
            self.status_label.config(text="Status: Error in Recording")
            return
        self.recorded_data.append(indata.copy())

    def save_recording(self):
        if not self.recorded_data:
            print("No recording to save.")
            self.status_label.config(text="Status: No Recording to Save")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.stop_recording()

            # Ensure samplerate is an integer
            samplerate = int(self.recording_stream.samplerate)

            # Convert the recorded data to 16-bit integers
            recorded_audio = (np.concatenate(self.recorded_data, axis=0) * 32767).astype(np.int16)

            write_wav(file_path, samplerate, recorded_audio)
            print(f"Recording saved to {file_path}")
            self.status_label.config(text=f"Status: Recording saved to {file_path}")

    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def stop_timer(self):
        self.timer_label.config(text="Recording Time: 0s")

    def update_timer(self):
        if self.is_recording:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Recording Time: {elapsed_time}s")
            self.root.after(1000, self.update_timer)

    def on_closing(self):
        if self.is_recording:
            self.stop_recording()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceRecorder(root)
    root.mainloop()
