import subprocess
import math
import time
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
        self.lastVolumeSet = 0

    def setVolume(self, percent):
        if time.time() - self.lastVolumeSet < 0.1:
            return
        
        percent = max(0, min(100, percent))
        
        try:
            subprocess.run([
                "pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"
            ], check = True)
            print(f"[VOLUME] Volume has been set to: {percent}%")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to set volume: {e}")
        except FileNotFoundError:
            print(f"[ERROR] 'pactl' not found: {e}")
    
    def startAdjusting(self, angle):
        self.adjusting = True
        self.startAngle = angle
        self.startVolume = self.currentVolume
        self.prevDelta = 0.0

    def updateVolume(self, angle):
        if not self.adjusting:
            return
        
        delta = angle - self.startAngle
        smootherDelta = (Config.smootherAlpha * delta + (1 - Config.smootherAlpha) * self.prevDelta)
        self.prevDelta = smootherDelta

        newVolume = int(self.startVolume + smootherDelta * Config.volumeSensitivity)
        newVolume = max(0, min(100, newVolume))
        self.currentVolume = max(0, min(100, newVolume))

        if abs(newVolume - self.currentVolume) > 2:
            self.currentVolume = newVolume
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