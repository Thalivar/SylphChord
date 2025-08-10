import mediapipe as mp
import cv2
from config.settings import Config

class HandDetector:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.mpDrawing = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands(
            min_detection_confidence = Config.minDetectionConfidence
        )

    def detect(self, frame):
        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgbFrame)
    
    def drawLandmarks(self, frame, hand_landmarks):
        self.mpDrawing.draw_landmarks(
            frame, hand_landmarks, self.mpHands.HAND_CONNECTIONS
        )