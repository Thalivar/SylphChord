import cv2
import time
import numpy as np
from config.settings import Config

class UITheme:

    background = (25, 25, 35)
    primary = (100, 200 ,255)
    secondary = (150, 100, 255)
    success = (100, 255, 150)
    warning = (255, 200, 100)
    error = (255, 100, 100)
    textPrimary = (255, 255, 255)
    textSecondary = (200, 200, 200)
    accent = (255, 150, 100)

class UIManager:
    def __init__(self):
        self.showLandmarks = Config.showLandmarksByDefault
        self.uiOpacity = Config.uiOpacity
        self.notificationqueue = []
    
    def toggleLandmarks(self):
        self.showLandmarks = not self.showLandmarks
        return self.showLandmarks

    def drawVolumeBar(self, frame, volume, x = 50, y = 100, width = 20, height = 300):
        cv2.rectangle(frame, (x, y), (x + width, y + height), UITheme.background, - 1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), UITheme.primary, 2)

        fillHeight = int((volume / 100.0) * height)
        if fillHeight > 0:
            for i in range(fillHeight):
                alpha = 1 / fillHeight
                color = self.interpolateColor(UITheme.success, UITheme.warning, alpha)
                yPos = y + height - i
                cv2.line(frame, (x + 2, yPos), (x + width - 2, yPos), color, 1)
        
        text = f"{volume}%"
        textSize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        textX = x + (width - textSize[0]) // 2
        textY = y + height + 20

        cv2.putText(frame, text, (textX + 1, textY + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(frame, text, (textX, textY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, UITheme.textPrimary, 2)
    
    def drawGestureModeIndicator(self, frame, gestureMode, x = 10, y = 30):
        modeText = f"Mode: {gestureMode.value.capitalize()}"

        if gestureMode.value == "volume":
            color = UITheme.success
        elif gestureMode.value == "media":
            color = UITheme.primary
        elif gestureMode.value == "locked":
            color = UITheme.warning
        else:
            color = UITheme.textSecondary
        
        textSize = cv2.getTextSize(modeText, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        cv2.rectangle(frame, (x - 5, y - 25), (x + textSize[0] + 10, y + 5), UITheme.background, -1)
        cv2.rectangle(frame, (x - 5, y - 25), (x + textSize[0] + 10, y + 5), color, 2)

        cv2.putText(frame, modeText, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    def drawFingerIndicators(self, frame, fingerPositions, gestureMode):
        if not self.showLandmarks or not fingerPositions:
            return
    
        if gestureMode.value == "volume":
            color = UITheme.success
            radius = 15
        elif gestureMode.value == "media":
            color = UITheme.primary
            radius = 12
        else:
            color = UITheme.textSecondary
            radius = 8
        
        pulse = int(5 * abs(np.sin(time.time() * 3)))
        for pos in fingerPositions:
            cx, cy = pos
            cv2.circle(frame, (cx, cy), radius + pulse, color, 2)
            cv2.circle(frame, (cx, cy), 4, color, -1)
    
    def showNotification(self, frame, message, duration = None):
        if duration is None:
            duration = Config.notificationDuration

        currentTime = time.time()
        self.notificationqueue.append({
            "message": message,
            "startTime": currentTime,
            "duration": duration
        })

        self.notificationqueue = [n for n in self.notificationqueue if currentTime - n["startTime"] < n["duration"]]

        yOffset = 50
        for notification in self.notificationqueue:
            alpha = max(0, 1 - (currentTime - notification["startTime"]) / notification["duration"])

            text = notification["message"]
            textSize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            x = frame.shape[1] - textSize[0] - 20
            y = yOffset

            overlay = frame.copy()
            cv2.rectangle(overlay, (x - 10, y - 25), (x + textSize[0] + 10, y + 5), UITheme.background, -1)
            cv2.addWeighted(overlay, alpha * 0.8, frame, 1 - alpha * 0.8, 0, frame)

            color = tuple(int(c * alpha) for c in UITheme.textPrimary)
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            yOffset += 40
    
    def interpolateColor(self, color1, color2, alpha):
        return tuple(int(c1 * (1 - alpha) + c2 * alpha) for c1, c2 in zip(color1, color2))
    
    def drawFPSCounter(self, frame, fps):
        text = f"FPS: {fps:.1f}"
        cv2.putText(frame, text, (frame.shape[1] - 120, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, UITheme.textSecondary, 1)
    
    def drawControlsHelp(self, frame):
        helpText = [
            "Controls:",
            "L - Toggles Landmarks",
            "H - Switch The Dominant Hand",
            "R - Reset The Gesture",
            "ESC - Exit The Program"
        ]

        yStart = frame.shape[0] - (len(helpText) * 25) - 10
        for i, text in enumerate(helpText):
            y = yStart + (i * 25)
            cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, UITheme.textSecondary, 1)