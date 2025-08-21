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
        self.dominantHand = Config.dominantHandPreference

    def detect(self, frame):
        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgbFrame)
    
    def drawLandmarks(self, frame, handLandmarks):
        if hasattr(self, "showLandmarks") and self.showLandmarks:
            self.mpDrawing.draw_landmarks(
                frame, handLandmarks, self.mpHands.HAND_CONNECTIONS
            )

    def classifyHands(self, results):
        if not results.multi_hand_landmarks:
            return []
        
        classifiedHands = []
        for i, handLandmarks in enumerate(results.multi_hand_landmarks):
            handInfo = {
                "landmarks": handLandmarks,
                "side": "right" if i == 0 else "left",
                "confidence": 1.0
            }
            classifiedHands.append(handInfo)
        return classifiedHands