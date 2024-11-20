from flask import Flask, Response
import subprocess

app = Flask(__name__)

# FFmpeg command to capture both video and audio from a camera
FFMPEG_COMMAND = [
    'ffmpeg',
    '-f', 'v4l2', '-i', '/dev/video0',  # Video input (adjust for your device)
    '-f', 'alsa', '-i', 'hw:0',  # Audio input (adjust for your microphone)
    '-c:v', 'libx264', '-c:a', 'aac',  # Encode video and audio
    '-f', 'mpegts', '-'  # Output format for streaming
]

@app.route('/video_feed')
def video_feed():
    def generate():
        with subprocess.Popen(FFMPEG_COMMAND, stdout=subprocess.PIPE, bufsize=10 ** 8) as process:
            while True:
                frame = process.stdout.read(1024)  # Stream chunks
                if not frame:
                    break
                yield frame

    return Response(generate(), mimetype='video/mp2t')  # MPEG-TS for video and audio

@app.route('/')
def index():
    return '''
        <html>
            <head><title>Camera Stream with Audio</title></head>
            <body>
                <h1>Camera Stream with Audio</h1>
                <video controls autoplay>
                    <source src="/video_feed" type="video/mp2t">
                    Your browser does not support the video tag.
                </video>
            </body>
        </html>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
