import math
import cv2
import mediapipe as mp
from config.settings import Config

class GestureProcessor:
    def __init__(self):
        self.mpHands = mp.solutions.hands

    def isOneFingerUp(self, landmarks, h, w):
        indexTip = self.mpHands.HandLandmark.INDEX_FINGER_TIP
        indexPip = self.mpHands.HandLandmark.INDEX_FINGER_PIP
        indexPIP = self.mpHands.HandLandmark.INDEX_FINGER_PIP
        middleTip = self.mpHands.HandLandmark.MIDDLE_FINGER_TIP
        middlePip = self.mpHands.HandLandmark.MIDDLE_FINGER_PIP
        ringTip = self.mpHands.HandLandmark.RING_FINGER_TIP
        ringPip = self.mpHands.HandLandmark.RING_FINGER_PIP
        pinkyTip = self.mpHands.HandLandmark.PINKY_TIP
        pinkyPip = self.mpHands.HandLandmark.PINKY_PIP
        indexExtended = landmarks[indexTip].y * h < landmarks[indexPip].y * h
        indexExtension = abs(landmarks[indexTip].y - landmarks[indexPIP].y) * h
        middleFolded = landmarks[middleTip].y * h > landmarks[middlePip].y * h
        ringFolded = landmarks[ringTip].y * h > landmarks[ringPip].y * h
        pinkyFolded = landmarks[pinkyTip].y * h > landmarks[pinkyPip].y * h

        if (indexExtended and middleFolded and ringFolded and pinkyFolded and indexExtension > Config.fingerExtensionThreshold):
            x = int(landmarks[indexTip].x * w)
            y = int(landmarks[indexTip].y * h)
            return (x, y)

        return None

    def isGrabbing(self, landmarks, h):
        fingerTips = [
            self.mpHands.HandLandmark.INDEX_FINGER_TIP,
            self.mpHands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mpHands.HandLandmark.RING_FINGER_TIP,
            self.mpHands.HandLandmark.PINKY_TIP
        ]
        fingerPips = [
            self.mpHands.HandLandmark.INDEX_FINGER_PIP,
            self.mpHands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mpHands.HandLandmark.RING_FINGER_PIP,
            self.mpHands.HandLandmark.PINKY_PIP
        ]

        thumbTip = self.mpHands.HandLandmark.THUMB_TIP
        thumbIp = self.mpHands.HandLandmark.THUMB_IP

        foldedFingers = 0
        for tip, pip in zip(fingerTips, fingerPips):
            if landmarks[tip].y > landmarks[pip].y:
                foldedFingers += 1

        if landmarks[thumbTip].y > landmarks[thumbIp].x:
            foldedFingers += 1

        isGrabbing = foldedFingers >= 4

        return [], isGrabbing
