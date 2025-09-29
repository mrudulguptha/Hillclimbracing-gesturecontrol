import cv2
import mediapipe as mp
import pyautogui
import comtypes.client
import pygetwindow as gw
import time
import sys
import face_recognition
import numpy as np
import os

# === PowerPoint Setup ===
try:
    PowerPoint = comtypes.client.CreateObject("PowerPoint.Application")
    PowerPoint.Visible = 1
    presentation = PowerPoint.Presentations.Open(
        r"C:\Users\mrudu\OneDrive\Documents\English_presentation[1]  -  Read-Only.pptx"
    )
except Exception as e:
    print("❌ Error opening PowerPoint:", e)
    sys.exit(1)

presentation.SlideShowSettings.Run()
time.sleep(2)
slide_show = presentation.SlideShowWindow.View

ppt_windows = [w for w in gw.getAllTitles() if "PowerPoint Slide Show" in w]
if ppt_windows:
    try:
        ppt_win = gw.getWindowsWithTitle(ppt_windows[0])[0]
        ppt_win.activate()
        ppt_win.maximize()
    except Exception as e:
        print("⚠ Could not maximize PowerPoint window:", e)

# === Mediapipe Setup ===
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7
)

# === Face Recognition Setup ===
owner_images = []
owner_encodings = []
for file in os.listdir("owner_face"):
    img_path = os.path.join("owner_face", file)
    img = face_recognition.load_image_file(img_path)
    encoding = face_recognition.face_encodings(img)[0]
    owner_images.append(img)
    owner_encodings.append(encoding)

cap = cv2.VideoCapture(0)
last_action_time = 0
cooldown = 1.0  # seconds

def fingers_up(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for id in range(1, 5):
        if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # --- Face Recognition ---
    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    owner_detected = False
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(owner_encodings, face_encoding)
        if True in matches:
            owner_detected = True
            break

    if owner_detected:
        # --- Hand Gesture Recognition ---
        result = hands_detector.process(rgb_frame)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                fingers = fingers_up(hand_landmarks)
                current_time = time.time()
                if current_time - last_action_time > cooldown:
                    if fingers == [1,1,1,1,1]:
                        slide_show.Next()
                        last_action_time = current_time
                    elif fingers == [0,0,0,0,0]:
                        slide_show.Previous()
                        last_action_time = current_time
                    elif fingers == [0,1,1,0,0]:
                        slide_show.Exit()
                        last_action_time = current_time
    else:
        print("🚫 Unauthorized user. Gesture disabled.")

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
try:
    presentation.Close()
    PowerPoint.Quit()
except:
    pass
