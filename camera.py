import cv2, time, numpy as np, pyaudio, wave
from datetime import datetime
import os

timeLimit = False # Set to true if timeLimit wanted
maxTime = 10 # Max time in seconds
detectionLimit = False # Set to true detectionLimit wanted
maxDetection = 3 # Number of max detections
videoPathFolder = "video"
audioPathFolder = "audio"
enableAudio = True

if not os.path.exists(videoPathFolder):
    os.makedirs(videoPathFolder)
if not os.path.exists(audioPathFolder):
    os.makedirs(audioPathFolder)

vid = cv2.VideoCapture(0)
w, h = int(vid.get(3)), int(vid.get(4)) # Get width and height

ret, frame = vid.read()
frame = frame[:,:,1]
prevFrame = np.copy(frame)

nDetections = 0

pgmChrono = time.time() + maxTime

def condition():
    global timeLimit, pgmChrono, nDetections, maxDetection, detectionLimit
    cond = False
    if (detectionLimit):
        cond |= nDetections < maxDetection
    elif (timeLimit):
        cond |= time.time() < pgmChrono
    else :
        cond = True
    return cond

def recordVideo(tps, dt, enabledAudio=True):
    """
    Begins record of video of duration tps, and with dt as a timestep
    """
    global nDetections
    df = 0
    now = datetime.now()
    out = cv2.VideoWriter(os.path.join(videoPathFolder, "{}_{}.mp4".format(now.strftime("%d-%m-%Y_%H-%M-%S"), nDetections)), cv2.VideoWriter_fourcc(*'mp4v'), 1000/dt, (w,h))

    if (enabledAudio):
        aud = pyaudio.PyAudio()
        stream = aud.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        audio = []

    while(df*dt/1000 < tps):
        ret, frame2 = vid.read()
        if (enabledAudio) :
            data = stream.read(4096)
            audio.append(data)
        out.write(frame2)
        df+=1
        time.sleep(dt/1000)
    if (enabledAudio):
        stream.stop_stream()
        stream.close()
        aud.terminate()
        sound_file = wave.open(os.path.join(audioPathFolder, "{}_{}.wav".format(now.strftime("%d-%m-%Y_%H-%M-%S"), nDetections)),"wb")
        sound_file.setnchannels(1)
        sound_file.setsampwidth(aud.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b''.join(audio))
        sound_file.close()

while(condition()):
    ret, frame = vid.read()
    frame = np.asarray(frame[:,:,1], np.int16)
    
    diff = np.asarray(255*(np.abs(frame-prevFrame) > 100), np.uint8)

    if (np.sum(diff) >= 10):
        # If 10 pixels or more have completely changed, record a video of 60 seconds, at 10 fps
        print("detection")
        recordVideo(2, 100, enableAudio)
        nDetections +=1
        ret, prevFrame = vid.read()
        prevFrame = prevFrame[:,:,1]
    else:
        prevFrame = np.copy(frame)
    time.sleep(0.1)
vid.release()
