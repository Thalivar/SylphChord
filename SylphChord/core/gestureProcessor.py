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
        middleTip = self.mpHands.HandLandmark.MIDDLE_FINGER_TIP
        middlePip = self.mpHands.HandLandmark.MIDDLE_FINGER_PIP
        ringTip = self.mpHands.HandLandmark.RING_FINGER_TIP
        ringPip = self.mpHands.HandLandmark.RING_FINGER_PIP
        pinkyTip = self.mpHands.HandLandmark.PINKY_TIP
        pinkyPip = self.mpHands.HandLandmark.PINKY_PIP
        thumbTip = self.mpHands.HandLandmark.THUMB_TIP
        thumbMcp = self.mpHands.HandLandmark.THUMB_MCP

        indexExtended = landmarks[indexTip].y < landmarks[indexPip].y
        indexExtension = abs(landmarks[indexTip].y - landmarks[indexPip].y) * h
        middleFolded = landmarks[middleTip].y > landmarks[middlePip].y
        ringFolded = landmarks[ringTip].y > landmarks[ringPip].y
        pinkyFolded = landmarks[pinkyTip].y > landmarks[pinkyPip].y

        thumbDistance = abs(landmarks[thumbTip].x - landmarks[thumbMcp].x)
        thumbFolded = thumbDistance < Config.fingerDistanceThreshold

        if (indexExtended and middleFolded and ringFolded and pinkyFolded and indexExtension > Config.fingerExtensionThreshold and thumbFolded):
            x = int(landmarks[indexTip].x * w)
            y = int(landmarks[indexTip].y * h)
            return (x, y)

        return None

    def isGrabbing(self, landmarks, w, h):
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
        extendedFingers = []

        for i, (tip, pip) in enumerate(zip(fingerTips, fingerPips)):
            if landmarks[tip].y > landmarks[pip].y:
                foldedFingers += 1
            else:
                extendedFingers.append(tip)
        
        thumbDistance = abs(landmarks[thumbTip].x - landmarks[thumbIp].x) * w
        thumbFolded = thumbDistance < Config.fingerDistanceThreshold
        if thumbFolded:
            foldedFingers += 1
        
        isGrabbing = foldedFingers >= 5
        return extendedFingers, isGrabbing
    
    def getFingerPositions(self, landmarks, w, h, normalized: bool = False):
        fingerTips = [
            self.mpHands.HandLandmark.THUMB_TIP,
            self.mpHands.HandLandmark.INDEX_FINGER_TIP,
            self.mpHands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mpHands.HandLandmark.RING_FINGER_TIP,
            self.mpHands.HandLandmark.PINKY_TIP
        ]

        if normalized:
            return [(landmarks[tip].x, landmarks[tip].y) for tip in fingerTips]
        return [(int(landmarks[tip].x * w), int(landmarks[tip].y * h)) for tip in fingerTips]
