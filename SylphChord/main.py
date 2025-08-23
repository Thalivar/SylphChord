import cv2
import time
from core.camera import CameraManager
from core.handDetector import HandDetector
from core.gestureProcessor import GestureProcessor
from controllers.volumeController import VolumeController
from controllers.mediaController import MediaController
from utils.zoneManager import ZoneManager
from config.settings import Config
from core.gestureStateManager import GestureStateManager, GestureMode
from utils.uiManager import UIManager

class SylphChord:
    def __init__(self):
        self.camera = CameraManager()
        self.handDetector = HandDetector()
        self.gestureProcessor = GestureProcessor()
        self.volumeController = VolumeController()
        self.mediaController = MediaController()
        self.zoneManager = ZoneManager()
        self.gestureStateManager = GestureStateManager()
        self.uiManager = UIManager()
        self.fpsHistory = []
        self.lastTime = time.time()
        self.pendingNotification = None
    
    def drawUI(self, frame, fps = 0):
        self.uiManager.drawVolumeBar(frame, self.volumeController.currentVolume)
        self.zoneManager.drawZones(frame)
        self.uiManager.drawGestureModeIndicator(frame, self.gestureStateManager.currentMode)
        self.uiManager.drawFPSCounter(frame, fps)

        if hasattr(self, "pendingNotification") and self.pendingNotification:
            self.uiManager.showNotification(frame, self.pendingNotification)
            self.pendingNotification = None
        else:
            self.uiManager.showNotification(frame, "", 0)
        
        if getattr(self.uiManager, "showControlsHelp", False):
            self.uiManager.drawControlsHelp(frame)

    def calculateFPS(self):
        currentTime = time.time()
        if hasattr(self, "lastTime"):
            fps = 1.0 / (currentTime - self.lastTime)
            self.fpsHistory.append(fps)
            
            if len(self.fpsHistory) > 30:
                self.fpsHistory.pop(0)
        
        self.lastTime = currentTime
        return sum(self.fpsHistory) / len(self.fpsHistory) if self.fpsHistory else 0
    
    def handleKeyboardInput(self):
        key = cv2.waitKey(1) & 0xFF
        char = chr(key).lower() if 0 <= key < 128 else ""

        if char == "r":
            self.gestureStateManager.setMode(GestureMode.idle)
            self.pendingNotification = "Gesture State Reset"
        elif char == "m":
            modeInfo = self.gestureStateManager.getModeInfo()
            self.pendingNotification = f"Mode: {modeInfo['mode'].value}"
        elif char == "h":
            self.uiManager.showControlsHelp = not getattr(self.uiManager, "showControlsHelp", False)
        elif key == 27:
            return True

        return False

    def handleVolumeControl(self, landmarks, w, h):
        angle = self.volumeController.getAngleBetweenFingers(landmarks, w, h)
        if not self.volumeController.adjusting:
            self.volumeController.startAdjusting(angle)
        else:
            self.volumeController.updateVolume(angle)
    
    def handleMediaControl(self, landmarks, w, h):
        indexTip = landmarks[8]
        x, y = int(indexTip.x * w), int(indexTip.y * h)

        actions = (
            ("play", "Play/Pause", self.mediaController.playPause),
            ("next", "Next song", self.mediaController.nextSong),
            ("prev", "Previous song", self.mediaController.prevSong)
        )

        for zone, label, fn in actions:
            if self.zoneManager.isInZone(x, y, zone):
                try:
                    fn()
                    self.pendingNotification = f"{label} triggered"
                except Exception as e:
                    self.pendingNotification = f"Failed to trigger {label}"
                    print(f"[ERROR] {label} action failed: {e}")
                break  

    def processGestures(self, handLandmarks, frame):
        h, w, c = frame.shape
        fingerTip = self.gestureProcessor.isOneFingerUp(handLandmarks.landmark, h, w)
        extendedFingers, isGrabbing = self.gestureProcessor.isGrabbing(handLandmarks.landmark, w, h)

        isMediaZone = False
        if fingerTip:
            x, y = fingerTip
            mediaZone = next((z for z in ("play", "next", "prev") if self.zoneManager.isInZone(x, y, z)), None)
            isMediaZone = mediaZone is not None
            
        currentMode = self.gestureStateManager.processGesturePriority(isGrabbing, bool(fingerTip), isMediaZone)

        if currentMode.value == "volume" and isGrabbing:
            self.handleVolumeControl(handLandmarks.landmark, w, h)
        elif currentMode.value == "media" and fingerTip:
            self.handleMediaControl(handLandmarks.landmark, w, h)
        elif currentMode.value != "volume":
            self.volumeController.stopAdjusting()

        if isGrabbing and not fingerTip:
            fingerPositions = self.gestureProcessor.getFingerPositions(handLandmarks.landmark, w, h)
            self.uiManager.drawGrabIndicators(frame, fingerPositions, currentMode)
        elif fingerTip and not isGrabbing:
            fingerPositions = [fingerTip]
            self.uiManager.drawFingerIndicators(frame, fingerPositions, currentMode)
        else:
            if hasattr(self.uiManager, "clearIndicators"):
                self.uiManager.clearIndicators(frame)
    
    def run(self):
        print(f"[INFO] Starting SylphChord...")
        print(f"[CONTROLS] R: Reset Gesture State, H: Toggle Help, M: Show Mode, ESC: Exit")

        try:
            while self.camera.isOpened():
                frame = self.camera.readFrame()
                if frame is None:
                    print("[WARNING] Your camera is not on.")
                    continue
                
                fps = self.calculateFPS()
                results = self.handDetector.detect(frame)
                if results.multi_hand_landmarks:
                    for handLandmarks in results.multi_hand_landmarks:
                        self.processGestures(handLandmarks, frame)
                
                else:
                    self.volumeController.stopAdjusting()
                
                self.drawUI(frame, fps)
                cv2.imshow("SylphChord", frame)

                if self.handleKeyboardInput():
                    print("[INFO] ESC pressed, shutting down SylphChord...")
                    self.volumeController.setVolume(45)
                    break

        except KeyboardInterrupt:
            print("[INFO] Keyboard interrupt received, shutting down...")
        finally:
            self.camera.release()
            print("[INFO] SylphChord has been stopped.")

class PerformanceMonitor:
    def __init__(self):
        self.frameTimes = []
        self.gestureProcessTimes = []

    def startFrameTimer(self):
        self.frameStart = time.time()
    
    def endFrameTimer(self):
        if hasattr(self, "frameStart"):
            frameTime = time.time() - self.frameStart
            self.frameTimes.append(frameTime)
            if len(self.frameTimes) > 30:
                self.frameTimes.pop(0)
    
    def getAverageFrameTime(self):
        return sum(self.frameTimes) / len(self.frameTimes) if self.frameTimes else 0
    
    def shouldSkipFrame(self):
        avgTime = self.getAverageFrameTime()
        return avgTime > (1.0 / Config.minFpsThreshold) and Config.enableFrameSkipping

if __name__ == "__main__":
    app = SylphChord()
    app.run()