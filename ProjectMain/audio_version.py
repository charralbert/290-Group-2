import cv2
from flask import Flask, Response, render_template, jsonify
import time
import pyaudio
import numpy as np
import threading
import logging

# Audio initialization------------------------
FORMAT = pyaudio.paInt16  # 16-bit depth
CHANNELS = 1  # Mono
RATE = 44100  # Samples per second (44.1kHz)
CHUNK = 1024  # Number of frames per buffer (1024 samples per frame)
VOLUME_THRESHOLD = 60  # Volume threshold to trigger notification

# Create a PyAudio object
p = pyaudio.PyAudio()

# Open the audio stream
stream = p.open(format=FORMAT,
               channels=CHANNELS,
               rate=RATE,
               input=True,
               frames_per_buffer=CHUNK)

# Flask initialization -------------
app = Flask(__name__)

# Initialize the camera (assuming the camera is at index 0)
camera = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not camera.isOpened():
    logging.error("Error: Could not open camera.")
    exit()

# Retrieve FPS
fps = camera.get(cv2.CAP_PROP_FPS)

# Set resolution and fps
fps = 30  # Set FPS
camera.set(cv2.CAP_PROP_FPS, fps)

# Global variables for notification and audio level
volume_notification = ""  # Empty by default
current_volume = 0  # Default audio level

# Function to monitor the microphone volume
def get_volume():
    global volume_notification, current_volume
    while True:
        try:
            # Read data from microphone
            data = stream.read(CHUNK)
            # Convert the byte data to numpy array of integers
            audio_data = np.frombuffer(data, dtype=np.int16)
            # Calculate the root-mean-square (RMS) which is a measure of the audio volume
            volume = np.sqrt(np.mean(np.square(audio_data)))
            current_volume = volume *2  # Update the global audio level

            # Log the volume to verify it
            #logging.debug(f"Current audio volume: {volume}")

            # If the volume exceeds the threshold, set the notification message
            if volume > VOLUME_THRESHOLD:
                volume_notification = "Loud sound detected! Volume is too high."
            else:
                volume_notification = ""  # Clear notification if volume is below threshold

            time.sleep(0.1)  # Sleep for 100ms to prevent overwhelming the CPU
        except Exception as e:
            logging.error(f"Error in volume monitoring: {e}")
            break


# Start the thread to monitor the microphone volume
volume_thread = threading.Thread(target=get_volume)
volume_thread.daemon = True  # Allow the program to exit if this is the only thread running
volume_thread.start()


# Function to generate the video stream
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


# Define a route to get the current audio volume
@app.route('/get_audio_level')
def get_audio_level():
    global current_volume
    return jsonify({'volume': current_volume})


# Index route to display the video and live status
@app.route('/')
def index():
    global volume_notification, fps
    # We pass dynamic data to the template instead of embedding it directly in HTML
    return render_template('indextwo.html', fps=fps, volume_notification=volume_notification)


if __name__ == '__main__':
    # Enable logging for Flask
    #logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5000)

    # Close the stream when done
    stream.stop_stream()
    stream.close()
    p.terminate()
