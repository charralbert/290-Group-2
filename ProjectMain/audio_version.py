import cv2
from flask import Flask, Response, render_template, request
import time
import pyaudio
import numpy as np
import threading

app = Flask(__name__)

# Initialize the camera (assuming the camera is at index 0)
camera = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not camera.isOpened():
   print("Error: Could not open camera.")
   exit()

# Retrieve FPS
fps = camera.get(cv2.CAP_PROP_FPS)

# Set resolution and fps
fps = 60  # Set FPS
camera.set(cv2.CAP_PROP_FPS, fps)

# PyAudio configuration for both capture and playback
p = pyaudio.PyAudio()

# Setup audio stream for capturing
stream_input = p.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=44100,
                     input=True,
                     frames_per_buffer=1024)

# Setup audio stream for playback
stream_output = p.open(format=pyaudio.paInt16,
                      channels=1,
                      rate=44100,
                      output=True,
                      frames_per_buffer=1024)

# Global variable to control audio playback
audio_playing = False

# Function to generate the video stream
def generate_video():
   while True:
       ret, frame = camera.read()
       if not ret:
           break

       # Get current timestamp
       timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

       # Encode the frame as JPEG
       ret, jpeg = cv2.imencode('.jpg', frame)
       if not ret:
           continue

       # Convert the frame to bytes and yield it as part of the multipart response
       frame = jpeg.tobytes()
       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Function to calculate the volume level
def get_audio_level():
   data = np.frombuffer(stream_input.read(1024), dtype=np.int16)
   volume_norm = np.linalg.norm(data) / 1024  # Normalize the volume
   return min(volume_norm, 1.0)  # Ensure the volume is between 0 and 1

# Function to play audio in real-time
def play_audio():
   global audio_playing
   while True:
       if audio_playing:
           data = stream_input.read(1024)
           stream_output.write(data)
       time.sleep(0.01)  # To reduce CPU usage

# Start the audio playback in a separate thread
audio_thread = threading.Thread(target=play_audio, daemon=True)
audio_thread.start()

# Define the route to stream video
@app.route('/video_feed')
def video_feed():
   return Response(generate_video(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# Index route to display the video and audio volume bar
@app.route('/')
def index():
   return render_template('indextwo.html')

# Routes to control audio playback
@app.route('/start_audio', methods=['POST'])
def start_audio():
   global audio_playing
   audio_playing = True
   return '', 204

@app.route('/stop_audio', methods=['POST'])
def stop_audio():
   global audio_playing
   audio_playing = False
   return '', 204

if __name__ == '__main__':
   # Run the app on the local network, accessible from other devices
   app.run(host='0.0.0.0', port=5000)