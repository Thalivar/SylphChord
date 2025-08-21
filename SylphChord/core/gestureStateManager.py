from enum import Enum
import time
from config.settings import Config

class GestureMode(Enum):
    idle = "idle"
    volume = "volume"
    media = "media"
    gestureLock = "locked"

class GestureStateManager:
    def __init__(self):
        self.currentMode = GestureMode.idle
        self.modeStartTime = time.time()
        self.lastModeSwitch = 0

    def canSwitchMode(self):
        return (time.time() - self.lastModeSwitch) > Config.gestureModeSwitchCooldown

    def setMode(self, newMode):
        if not self.canSwitchMode() and newMode != self.currentMode:
            return False
        
        if newMode != self.currentMode:
            self.currentMode = newMode
            self.modeStartTime = time.time()
            self.lastModeSwitch = time.time()
            print(f"[GESTURE] Mode has switched to: {newMode.value}")
            return True
        return False
    
    def isInGestureLock(self):
        return (self.currentMode == GestureMode.gestureLock or (time.time() - self.modeStartTime) < Config.gestureLockDuration)

    def processGesturePriority(self, isGrabbing, isPointing, inMediaZone):
        if self.isInGestureLock():
            return self.currentMode
        
        if isGrabbing:
            self.setMode(GestureMode.volume)
        elif isPointing and inMediaZone:
            self.setMode(GestureMode.media)
        else:
            if (time.time() - self.modeStartTime) > 0.5:
                self.setMode(GestureMode.idle)
        
        return self.currentMode

    def getModeInfo(self):
        return {
            "mode": self.currentMode,
            "duration": time.time() - self.modeStartTime,
            "canSwitch": self.canSwitchMode()
        }