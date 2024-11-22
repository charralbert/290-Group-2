import pyaudio
import numpy as np
import threading
import time

# Parameters for audio input
FORMAT = pyaudio.paInt16  # 16-bit depth
CHANNELS = 1  # Mono
RATE = 44100  # Samples per second (44.1kHz)
CHUNK = 1024  # Number of frames per buffer (1024 samples per frame)
VOLUME_THRESHOLD = 500  # Volume threshold to print (optional, can be adjusted)

# Create a PyAudio object
p = pyaudio.PyAudio()

# Function to calculate the volume of the audio
def get_volume():
    while True:
        # Read data from microphone
        data = stream.read(CHUNK)
        # Convert the byte data to numpy array of integers
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Calculate the root mean square (RMS) which is a measure of the audio volume
        volume = np.sqrt(np.mean(np.square(audio_data)))
        print(f"Current volume: {volume}")
        time.sleep(0.1)  # Sleep for 100ms to prevent overwhelming the CPU

# Open the audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Start the thread to monitor the microphone volume
volume_thread = threading.Thread(target=get_volume)
volume_thread.daemon = True  # Allow the program to exit if this is the only thread running
volume_thread.start()

# Keep the main program running so the thread can continue to monitor the microphone
try:
    while True:
        time.sleep(1)  # Main thread does nothing, just sleeps
except KeyboardInterrupt:
    print("Program interrupted. Exiting...")

# Close the stream when done
stream.stop_stream()
stream.close()
p.terminate()
