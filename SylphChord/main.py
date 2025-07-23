import math
import mediapipe as mp
import cv2
import subprocess

# === Initialize MediaPipe hands and akso the drawing utilities ===
mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils
hands = mpHands.Hands(min_detection_confidence = 0.7)
frameCount = 0
adjusting = False
startAngle = 0
startVolume = 0
currentVolume = 50
sensitivity = 1.0

# === Initializes the camera/webcam ===
wCam = cv2.VideoCapture(0)

def setVolume(percent):
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"])

def isOpenGrab(landmarks, h):
    grabScore = 0
    finger = [
        mpHands.HandLandmark.INDEX_FINGER_TIP,
        mpHands.HandLandmark.MIDDLE_FINGER_TIP,
        mpHands.HandLandmark.RING_FINGER_TIP,
        mpHands.HandLandmark.PINKY_TIP
        ]
    bases = [
        mpHands.HandLandmark.INDEX_FINGER_MCP,
        mpHands.HandLandmark.MIDDLE_FINGER_MCP,
        mpHands.HandLandmark.RING_FINGER_MCP,
        mpHands.HandLandmark.PINKY_MCP
    ]

    for tip, base in zip(finger, bases):
        yTip = landmarks[tip].y * h
        yBase = landmarks[base].y * h
        verticalGap = abs(yTip - yBase)

        if 30 < verticalGap < 120:
            grabScore += 1
    
    return grabScore >= 3 # <- Only considers it a grab if more than 3 fingers are curved

while wCam.isOpened(): # <- Loops while the webcam is open
    # Reads the webcame frame
    ret, frame = wCam.read()
    if not ret:
        print("Ignoring the empty camera frame.")
        break

    frame = cv2.flip(frame, 1) # <- Flips the frame
    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # <- Converts the frame to RGB
    result = hands.process(rgbFrame) # <- Processes the frame

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mpDrawing.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS) # <- Draws the landmarks and connections

            fingerList = hand_landmarks.landmark
            h, w, i = frame.shape

            x1, y1 = int(fingerList[mpHands.HandLandmark.INDEX_FINGER_TIP].x * w), int(fingerList[mpHands.HandLandmark.INDEX_FINGER_TIP].y * h)
            x2, y2 = int(fingerList[mpHands.HandLandmark.THUMB_TIP].x * w), int(fingerList[mpHands.HandLandmark.THUMB_TIP].y * h)

            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            distance = math.hypot(x2 - x1, y2 - y1) # <- Calculates the distance between the thumb and index finger tips
            isGrabbing = isOpenGrab(fingerList, h)

            if isGrabbing:
                if not adjusting:
                    adjusting = True
                    startAngle = angle
                    startVolume = currentVolume
                else:
                    delta = angle - startAngle
                    newVolume = int(startVolume + delta * sensitivity)
                    newVolume = max(0, min(100, newVolume))
                    currentVolume = newVolume
                    setVolume(currentVolume)

                    cv2.rectangle(frame, (50, 100), (85, 400), (0, 0, 0), 2) # <- Outline for the volume bar
                    volBarHeight = int((100 - currentVolume) * 3)
                    cv2.rectangle(frame, (51, 100 + volBarHeight), (84, 400), (0, 255, 0), -1)
                    cv2.putText(frame, f"Volume: {currentVolume}%", (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            else:
                adjusting = False

            frameCount += 1
            if frameCount % 10 == 0: # <- Updates the volume every 10 frames, It's to throttle the amixer command
                setVolume(currentVolume)
            
            setVolume(currentVolume)

    cv2.imshow("SylphChord", frame) # <- Shows the frame

    if cv2.waitKey(1) & 0xFF == 27: # <- Breaks the loop incase ESC is pressed
        break

wCam.release()
cv2.destroyAllWindows()