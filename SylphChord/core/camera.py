import cv2
from config.settings import Config

class CameraManager:
    def __init__(self):
        self.cap = cv2.VideoCapture(Config.cameraIndex)
        self.frameCount = 0
    
    def readFrame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (Config.frameWidth, Config.frameHeight))
        self.frameCount += 1
        return frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
    
    def isOpened(self):
        return self.cap.isOpened()