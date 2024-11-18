import cv2
from flask import Flask, Response

app = Flask(__name__)

# Initialize the camera (assuming the camera is at index 0)
# You can adjust the index if there are multiple cameras connected.
camera = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()


# Function to generate the video stream
def generate_video():
    while True:
        # Read a frame from the camera
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


# Index route to display the video
@app.route('/')
def index():
    return '''
        <html>
            <head><title>USB Camera Stream</title></head>
            <body>
                <h1>USB Camera Stream</h1>
                <img src="/video_feed" width="640" height="480" />
            </body>
        </html>
    '''


if __name__ == '__main__':
    # Run the app on the local network, accessible from other devices
    app.run(host='0.0.0.0', port=5000)