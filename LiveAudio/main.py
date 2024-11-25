import cv2
from flask import Flask, Response, render_template
import time
import pyaudio
import numpy as np
import threading

# Audio initialization------------------------
# Parameters for audio input
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
app = Flask(__name__)

# Initialize the camera (assuming the camera is at index 0)
# You can adjust the index if there are multiple cameras connected.
camera = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not camera.isOpened():
   print("Error: Could not open camera.")
   exit()

#retrieve FPS
fps = camera.get(cv2.CAP_PROP_FPS)

#set resolution and fps
fps = 60  # Set FPS
camera.set(cv2.CAP_PROP_FPS, fps)

# Set compression quality for JPEG
#encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Lower quality for better performance



# Function to generate the video stream
def get_volume():
   while True:
       # Read data from microphone
       data = stream.read(CHUNK)
       # Convert the byte data to numpy array of integers
       audio_data = np.frombuffer(data, dtype=np.int16)
       # Calculate the root-mean-square (RMS) which is a measure of the audio volume
       volume = np.sqrt(np.mean(np.square(audio_data)))
       print(f"Current volume: {volume}")
       time.sleep(0.1)  # Sleep for 100ms to prevent overwhelming the CPU


# Start the thread to monitor the microphone volume
volume_thread = threading.Thread(target=get_volume)
volume_thread.daemon = True  # Allow the program to exit if this is the only thread running
volume_thread.start()


# Function to generate the video stream
def generate_video():
   while True:
       # Read a frame from the camera
       ret, frame = camera.read()

       if not ret:
           break

           # Get current timestamp
       timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

           # Put timestamp on the frame (similar to FPS)
      # cv2.putText(frame, timestamp, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        # Put FPS on the frame
       #cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
                   #cv2.LINE_AA)

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


# Index route to display the video
@app.route('/')

def index():
   return render_template('index.html')



if __name__ == '__main__':
   # Run the app on the local network, accessible from other devices
   app.run(host='0.0.0.0', port=5000)

   # Close the stream when done
   stream.stop_stream()
   stream.close()
   p.terminate()

