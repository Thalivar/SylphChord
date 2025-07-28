import math
import mediapipe as mp
import cv2
import subprocess
import json
import os

mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils
hands = mpHands.Hands(min_detection_confidence = 0.7)
frameCount = 0
adjusting = False
startAngle = 0
startVolume = 0
currentVolume = 50
sensitivity = 1.0
prevDelta = 0.0
smootherAlpha = 0.3
playPauseTriggered = False
nextTriggered = False
prevTriggered = False
playPauseCooldown = 0
nextCooldown = 0
prevCooldown = 0
wCam = cv2.VideoCapture(0)

def loadZones():
    basePath = os.path.dirname(os.path.abspath(__file__))
    zonesPath = os.path.join(basePath, "zones.json")
    with open(zonesPath, "r") as f:
        return json.load(f)
zones = loadZones()

def isInZone(x, y, zones):
    x1, y1 = zones["topLeft"]
    x2, y2 = zones["bottomRight"]
    return x1 <= x <= x2 and y1 <= y <= y2

def setVolume(percent):
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"])
    print(f"[VOLUME] Volume has been set to : {percent}%")

def playPause():
    subprocess.run(["playerctl", "-p", "ncspot", "play-pause"])
    print("[MEDIA] Play/Pause has been triggered")

def nextSong():
    subprocess.run(["playerctl", "-p", "ncspot", "next"])
    print("[MEDIA] Next song has been triggered")

def prevSong():
    subprocess.run(["playerctl", "-p", "ncspot", "previous"])
    print("[MEDIA] Prev song has been triggered")

def isTwoFingersUp(landmarks, h, w):
    count = []
    tips = [
        mpHands.HandLandmark.INDEX_FINGER_TIP,
        mpHands.HandLandmark.MIDDLE_FINGER_TIP
    ]
    pips = [
        mpHands.HandLandmark.INDEX_FINGER_PIP,
        mpHands.HandLandmark.MIDDLE_FINGER_PIP
    ]

    for tip, pip in zip(tips, pips):
        if landmarks[tip].y * h < landmarks[pip].y * h:
            count.append(tip)

    if len(count) != 2:
        return []
    
    x1, y1 = int(landmarks[tips[0]].x * w), int(landmarks[tips[0]].y * h)
    x2, y2 = int(landmarks[tips[1]].x * w), int(landmarks[tips[1]].y * h)
    distance = math.hypot(x2 - x1, y2 - y1)

    if distance < 40:
        return [mpHands.HandLandmark.INDEX_FINGER_TIP, mpHands.HandLandmark.MIDDLE_FINGER_TIP]
    
    return []

def isOpenGrab(landmarks, h):
    grabFingers = []
    finger = [
        mpHands.HandLandmark.INDEX_FINGER_TIP,
        mpHands.HandLandmark.MIDDLE_FINGER_TIP,
        mpHands.HandLandmark.RING_FINGER_TIP,
        mpHands.HandLandmark.PINKY_TIP,
        mpHands.HandLandmark.THUMB_TIP
        ]
    bases = [
        mpHands.HandLandmark.INDEX_FINGER_MCP,
        mpHands.HandLandmark.MIDDLE_FINGER_MCP,
        mpHands.HandLandmark.RING_FINGER_MCP,
        mpHands.HandLandmark.PINKY_MCP,
        mpHands.HandLandmark.THUMB_MCP
    ]

    for tip, base in zip(finger, bases):
        yTip = landmarks[tip].y * h
        yBase = landmarks[base].y * h
        verticalGap = abs(yTip - yBase)

        if 30 < verticalGap < 120:
            grabFingers.append(tip)
    
    return grabFingers

while wCam.isOpened(): # <- Loops while the webcam is open
    # Reads the webcame frame
    ret, frame = wCam.read()
    if not ret:
        print("Ignoring the empty camera frame.")
        break

    frame = cv2.flip(frame, 1) # <- Flips the frame
    frame = cv2.resize(frame, (960, 700))
    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # <- Converts the frame to RGB
    result = hands.process(rgbFrame) # <- Processes the frame
    playZone = zones["play"]
    nextZone = zones["next"]
    prevZone = zones["prev"]

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mpDrawing.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS) # <- Draws the landmarks and connections

            fingerList = hand_landmarks.landmark
            h, w, i = frame.shape

            x1, y1 = int(fingerList[mpHands.HandLandmark.INDEX_FINGER_TIP].x * w), int(fingerList[mpHands.HandLandmark.INDEX_FINGER_TIP].y * h)
            x2, y2 = int(fingerList[mpHands.HandLandmark.THUMB_TIP].x * w), int(fingerList[mpHands.HandLandmark.THUMB_TIP].y * h)

            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            distance = math.hypot(x2 - x1, y2 - y1)

            grabbingFingers = isOpenGrab(fingerList, h)
            isGrabbing = len(grabbingFingers) >= 3

            fingersUp = isTwoFingersUp(fingerList, h, w)
            twoFingersUp = len(fingersUp) == 2
            
            mpDrawing.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)
            for tip_idx in grabbingFingers:
                cx = int(fingerList[tip_idx].x * w)
                cy = int(fingerList[tip_idx].y * h)
                cv2.circle(frame, (cx, cy), 12, (230, 130, 255), -1)

            for tip_idx in fingersUp:
                cx = int(fingerList[tip_idx].x * w)
                cy = int(fingerList[tip_idx].y * h)
                cv2.circle(frame, (cx, cy), 12, (200, 150, 200), -1)
            
            if twoFingersUp:
                x, y = int(fingerList[mpHands.HandLandmark.INDEX_FINGER_TIP].x * w), int(fingerList[mpHands.HandLandmark.INDEX_FINGER_TIP].y * h)
                
                if isInZone(x, y, playZone) and not playPauseTriggered:
                    playPause()
                    playPauseTriggered = True
                    playPauseCooldown = 120
                elif isInZone(x, y, nextZone) and not nextTriggered:
                    nextSong()
                    nextTriggered = True
                    nextCooldown = 120
                elif isInZone(x, y, prevZone) and not prevTriggered:
                    prevSong()
                    prevTriggered = True
                    prevCooldown = 120
                
            
            if playPauseCooldown > 0:
                playPauseCooldown -= 1
            elif playPauseTriggered:
                playPauseTriggered = False
            if nextCooldown > 0:
                nextCooldown -= 1
            elif nextTriggered:
                nextTriggered = False
            if prevCooldown > 0:
                prevCooldown -= 1
            elif prevTriggered:
                prevTriggered = False

            if isGrabbing:
                if not adjusting:
                    adjusting = True
                    startAngle = angle
                    startVolume = currentVolume
                else:
                    delta = angle - startAngle
                    smootherDelta = smootherAlpha * delta + (1 - smootherAlpha) * prevDelta
                    prevDelta = smootherDelta

                    newVolume = int(startVolume + smootherDelta * sensitivity)
                    newVolume = max(0, min(100, newVolume))
                    currentVolume = newVolume
                    setVolume(currentVolume)

            else:
                adjusting = False

    frameCount += 1
    if frameCount % 30 == 0: # <- Updates the volume every x frames. Puruly here to have better feedback with my old camera
        setVolume(currentVolume)

    cv2.rectangle(frame, (50, 100), (85, 400), (0, 0, 0), 2) # <- Outline for the volume bar
    volBarHeight = int((100 - currentVolume) * 3)
    cv2.rectangle(frame, (51, 100 + volBarHeight), (84, 400), (0, 255, 0), -1) # <- The volume bar
    cv2.putText(frame, f"Volume: {currentVolume}%", (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    for name, zone in zones.items():
        if not isinstance(zone, dict):
            continue # Skips the temporary comment i left in the json file remove this once its gone

        x1, y1 = zone["topLeft"]
        x2, y2 = zone["bottomRight"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
        cv2.putText(frame, name.capitalize(), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow("SylphChord", frame) # <- Shows the frame

    if cv2.waitKey(1) & 0xFF == 27: # <- Breaks the loop incase ESC is pressed
        setVolume(45) # Resets the volume
        break

wCam.release()
cv2.destroyAllWindows()