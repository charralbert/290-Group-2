import numpy as np
import matplotlib
import cv2 as cv
import pyaudio
import threading


# runs audio on second thread
def audio_stream():
    RATE = 44100
    CHUNK = 1024

    p = pyaudio.PyAudio()

    player = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True,
                    frames_per_buffer=CHUNK)
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while True:  # run forever
        player.write(np.frombuffer(stream.read(CHUNK), dtype=np.int16), CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()


# start secondary thread
secondary_thread = threading.Thread(target=audio_stream)
secondary_thread.start()

# Video output on main thread
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv.imshow('frame', frame)
    cv.imshow('frame2', gray)
    if cv.waitKey(1) == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()