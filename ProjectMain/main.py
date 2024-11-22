import cv2
from flask import Flask, Response, render_template, jsonify
import pyaudio
import numpy as np
import threading
import time

# Audio initialization------------------------
FORMAT = pyaudio.paInt16  # 16-bit depth
CHANNELS = 1  # Mono
RATE = 44100  # Samples per second (44.1kHz)
CHUNK = 1024  # Number of frames per buffer (1024 samples per frame)
VOLUME_THRESHOLD = 500  # Volume threshold to print (optional, can be adjusted)

# Create a PyAudio object
p = pyaudio.PyAudio()

# Open the audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Flask initialization -------------
app = Flask(__name__, template_folder='templates')

# Initialize the camera (assuming the camera is at index 0)
camera = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

# Global variable to store the current audio volume
current_volume = 0

# Function to generate the video stream
def get_volume():
    global current_volume
    while True:
        # Read data from microphone
        data = stream.read(CHUNK)
        # Convert the byte data to numpy array of integers
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Calculate the root-mean-square (RMS) which is a measure of the audio volume
        current_volume = np.sqrt(np.mean(np.square(audio_data)))
        print(f"Current volume: {current_volume}")
        time.sleep(1)  # Sleep for 100ms to prevent overwhelming the CPU

# Start the thread to monitor the microphone volume
volume_thread = threading.Thread(target=get_volume)
volume_thread.daemon = True  # Allow the program to exit if this is the only thread running
volume_thread.start()

# Function to generate video stream
def generate_video():
    while True:
        ret, frame = camera.read()

        if not ret:
            break

        # Encode the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)

        if not ret:
            continue

        # Convert the frame to bytes and yield it as part of the multipart response
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Define the route to stream video
@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Define the route to get the current audio volume
@app.route('/get_volume')
def get_audio_volume():
    # Return the current audio volume as JSON
    return jsonify(volume=current_volume)

# Index route to display the video
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Close the stream when done
stream.stop_stream()
stream.close()
p.terminate()
