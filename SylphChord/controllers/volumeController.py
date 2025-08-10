import subprocess
import math
import mediapipe as mp
from config.settings import Config

class VolumeController:
    def __init__(self):
        self.currentVolume = Config.defaultVolume
        self.adjusting = False
        self.startAngle = 0
        self.startVolume = 0
        self.prevDelta = 0.0
        self.mpHands = mp.solutions.hands

    def setVolume(self, percent):
        try:
            subprocess.run([
                "pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"
            ], check = True)
            print(f"[VOLUME] Volume has been set to: {percent}%")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to set volume: {e}")
    
    def startAdjusting(self, angle):
        self.adjusting = True
        self.startAngle = angle
        self.startVolume = self.currentVolume

    def updateVolume(self, angle):
        if not self.adjusting:
            return
        
        delta = angle - self.startAngle
        smootherDelta = (Config.smootherAlpha * delta + (1 - Config.smootherAlpha) * self.prevDelta)
        self.prevDelta = smootherDelta

        newVolume = int(self.startVolume + smootherDelta * Config.volumeSensitivity)
        self.currentVolume = max(0, min(100, newVolume))
        self.setVolume(self.currentVolume)
    
    def stopAdjusting(self):
        self.adjusting = False

    def getAngleBetweenFingers(self, landmarks, w, h):
        indexTip = self.mpHands.HandLandmark.INDEX_FINGER_TIP
        thumbTip = self.mpHands.HandLandmark.THUMB_TIP

        x1 = int(landmarks[indexTip].x * w)
        y1 = int(landmarks[indexTip].y * h)
        x2 = int(landmarks[thumbTip].x * w)
        y2 = int(landmarks[thumbTip].y * h)

        return math.degrees(math.atan2(y2 - y1, x2 - x1))