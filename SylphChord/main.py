import cv2
from core.camera import CameraManager
from core.handDetector import HandDetector
from core.gestureProcessor import GestureProcessor
from controllers.volumeController import VolumeController
from controllers.mediaController import MediaController
from utils.zoneManager import ZoneManager
from config.settings import Config

class SylphChord:
    def __init__(self):
        self.camera = CameraManager()
        self.handDetector = HandDetector()
        self.gestureProcessor = GestureProcessor()
        self.volumeController = VolumeController()
        self.mediaController = MediaController()
        self.zoneManager = ZoneManager()
    
    def drawUI(self, frame):
        cv2.rectangle(frame, (50, 100), (85, 400), (0, 0, 0), 2)
        volumeBarHeight = int((100 - self.volumeController.currentVolume) * 3)
        cv2.rectangle(frame, (51, 100 + volumeBarHeight), (84, 400), (0, 255, 0), -1)
        cv2.putText(frame, f"Volume: {self.volumeController.currentVolume}%",
                    (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        self.zoneManager.drawZones(frame)
    
    def processGestures(self, handLandmarks, frame):
        h, w, _ = frame.shape
        landmarks = handLandmarks.landmark

        grabbingFingers, isGrabbing = self.gestureProcessor.isGrabbing(landmarks, h)
        fingersUp = self.gestureProcessor.isTwoFingersUp(landmarks, h, w)
        twoFingersUp = len(fingersUp) == 2

        for tipIDX in grabbingFingers:
            cx = int(landmarks[tipIDX].x * w)
            cy = int(landmarks[tipIDX].y * h)
            cv2.circle(frame, (cx, cy), 12, (230, 130, 255), -1)
        
        for tipIDX in fingersUp:
            cx = int(landmarks[tipIDX].x * w)
            cy = int(landmarks[tipIDX].y * h)
            cv2.circle(frame, (cx, cy), 12, (200, 150, 200), -1)
        
        if twoFingersUp:
            indexTip = self.gestureProcessor.mpHands.HandLandmark.INDEX_FINGER_TIP
            x = int(landmarks[indexTip].x * w)
            y = int(landmarks[indexTip].y * h)

            if self.zoneManager.isInZone(x, y, "play"):
                self.mediaController.playPause()
            elif self.zoneManager.isInZone(x, y, "next"):
                self.mediaController.nextSong()
            elif self.zoneManager.isInZone(x, y, "prev"):
                self.mediaController.prevSong()
        
        if isGrabbing:
            angle = self.volumeController.getAngleBetweenFingers(landmarks, w, h)
            if not self.volumeController.adjusting:
                self.volumeController.startAdjusting(angle)
            else:
                self.volumeController.updateVolume(angle)
        else:
            self.volumeController.stopAdjusting
    
    def run(self):
        print(f"[INFO] Starting SylphChord...")
        try:
            while self.camera.isOpened():
                frame = self.camera.readFrame()
                if frame is None:
                    print("[WARNING] Your camera is not on.")
                    continue

                results = self.handDetector.detect(frame)
                if results.multi_hand_landmarks:
                    for handLandmarks in results.multi_hand_landmarks:
                        self.handDetector.drawLandmarks(frame, handLandmarks)
                        self.processGestures(handLandmarks, frame)
                
                self.mediaController.updateCooldowns()
                if self.camera.frameCount % Config.volumeUpdateInterval == 0:
                    self.volumeController.setVolume(self.volumeController.currentVolume)
                
                self.drawUI(frame)
                cv2.imshow("Sylphchord", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    print("[INFO] ESC pressed, shutting down SylphChord...")
                    self.volumeController.setVolume(45)
                    break

        except KeyboardInterrupt:
            print("[INFO] Keyboard interrupt received, shutting down...")
        finally:
            self.camera.release()
            print("[INFO] SylphChord has been stopped.")

if __name__ == "__main__":
    app = SylphChord()
    app.run()