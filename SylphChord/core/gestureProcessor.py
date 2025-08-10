import math
import cv2
import mediapipe as mp
from config.settings import Config

class GestureProcessor:
    def __init__(self):
        self.mpHands = mp.solutions.hands

    def isTwoFingersUp(self, landmarks, h, w):
        tips = [
            self.mpHands.HandLandmark.INDEX_FINGER_TIP,
            self.mpHands.HandLandmark.MIDDLE_FINGER_TIP
        ]
        pips = [
            self.mpHands.HandLandmark.INDEX_FINGER_PIP,
            self.mpHands.HandLandmark.MIDDLE_FINGER_PIP
        ]

        extendedFingers = []
        for tip, pip in zip(tips, pips):
            if landmarks[tip].y * h < landmarks[pip].y * h:
                extendedFingers.append(tip)
        
        if len(extendedFingers) != 2:
            return []
        
        x1 = int(landmarks[tips[0]].x * w)
        y1 = int(landmarks[tips[0]].y * h)
        x2 = int(landmarks[tips[1]].x * w)
        y2 = int(landmarks[tips[1]].y * h)

        distance = math.hypot(x2 - x1, y2 - y1)
        return extendedFingers if distance < Config.fingerDistanceThreshold else []
    
    def isGrabbing(self, landmarks, h):
        fingerTips = [
            self.mpHands.HandLandmark.INDEX_FINGER_TIP,
            self.mpHands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mpHands.HandLandmark.RING_FINGER_TIP,
            self.mpHands.HandLandmark.PINKY_TIP,
            self.mpHands.HandLandmark.THUMB_TIP
        ]
        fingerBases = [
            self.mpHands.HandLandmark.INDEX_FINGER_MCP,
            self.mpHands.HandLandmark.MIDDLE_FINGER_MCP,
            self.mpHands.HandLandmark.RING_FINGER_MCP,
            self.mpHands.HandLandmark.PINKY_MCP,
            self.mpHands.HandLandmark.THUMB_MCP
        ]

        extendedFingers = []
        for tip, base in zip(fingerTips, fingerBases):
            yTip = landmarks[tip].y * h
            yBase = landmarks[base].y * h
            verticalGap = abs(yTip - yBase)

            if Config.grabMinGap < verticalGap < Config.grabMaxGap:
                extendedFingers.append(tip)
            
        return extendedFingers, len(extendedFingers) >= Config.grabMinFingers