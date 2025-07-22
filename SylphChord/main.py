import math
import mediapipe as mp
import cv2
import subprocess

# === Initialize MediaPipe hands and akso the drawing utilities ===
mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils
hands = mpHands.Hands(min_detection_confidence = 0.7)

# === Initializes the camera/webcam ===
wCam = cv2.VideoCapture(0)

def setVolume(percent):
    subprocess.run(["amixer", "sset", "Master", f"{percent}%"])

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

            tiList = hand_landmarks.landmark
            h, w, i = frame.shape

            x1, y1 = int(tiList[mpHands.HandLandmark.INDEX_FINGER_TIP].x * w), int(tiList[mpHands.HandLandmark.INDEX_FINGER_TIP].y * h)
            x2, y2 = int(tiList[mpHands.HandLandmark.THUMB_TIP].x * w), int(tiList[mpHands.HandLandmark.THUMB_TIP].y * h)

            cv2.circle(frame, (x1, y1), 10, (0, 255, 255), -1)
            cv2.circle(frame, (x2, y2), 10, (0, 255, 255), -1)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            distance = math.hypot(x2 - x1, y2 - y1) # <- Calculates the distance between the thumb and index finger tips

            minDistance = 20
            maxDistance = 150
            volPercent = int((distance - minDistance) / (maxDistance - minDistance) * 100)
            volPercent = max(0, min(100, volPercent))

            cv2.putText(frame, f"Volume: {volPercent}%", (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            setVolume(volPercent)

    cv2.imshow("SylphChord", frame) # <- Shows the frame

    if cv2.waitKey(1) & 0xFF == 27: # <- Breaks the loop incase ESC is pressed
        break

wCam.release() # <- Releases the webcam
cv2.destroyAllWindows() # <- Closes the window