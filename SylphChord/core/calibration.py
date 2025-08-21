import cv2
import json
import numpy as np
from config.settings import Config

class GestureCalibrator:
    def __init__(self):
        self.calibrationData = {}
        self.currentGesture = None
        self.samples = []

    def startCalibration(self, gestureName):
        self.currentGesture = gestureName
        self.samples = []
        print(f"[CALIBRATION] Starting calibration for: {gestureName}")
    
    def addSample(self, landmarks):
        if self.currentGesture:
            self.samples.append(landmarks)
    
    def finishCalibration(self):
        if len(self.samples) >= 10:
            self.calibrationData[self.currentGesture] = {
                "threshold": self.calculateThreshold(),
                "reference": self.calculateReference()
            }
            self.saveCalibration()
            return True
        return False
    
    def calculateThreshold(self):
        return Config.calibrationThreshold
    
    def calculateReference(self):
        return self.samples[0] if self.samples else None
    
    def saveCalibration(self):
        with open("config/calibration.json", "w") as f:
            json.dump(self.calibrationData, f, indent = 2)