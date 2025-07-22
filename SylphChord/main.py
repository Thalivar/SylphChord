import math
import mediapipe as mp
import cv2

# === Initialize MediaPipe hands and akso the drawing utilities ===
mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils

# === Initializes the camera/webcam ===
wCam = cv2.VideoCapture(0)

with mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7) as hands:
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

                indexTip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
                h, w, i = frame.shape
                cx, cy = int(indexTip.x * w), int(indexTip.y * h) # <- Gets the coordinates of the index finger tip
                cv2.circle(frame, (cx, cy), 10, (0, 0, 255), -1)

        cv2.imshow("SylphChord", frame) # <- Shows the frame

        if cv2.waitKey(1) & 0xFF == 27: # <- Breaks the loop incase ESC is pressed
            break

wCam.release() # <- Releases the webcam
cv2.destroyAllWindows() # <- Closes the window