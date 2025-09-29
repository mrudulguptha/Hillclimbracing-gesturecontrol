import cv2
import mediapipe as mp
import pyautogui
import comtypes.client
import pygetwindow as gw
import time
import sys

# === PowerPoint Setup ===
try:
    PowerPoint = comtypes.client.CreateObject("PowerPoint.Application")
    PowerPoint.Visible = 1  # Visible PowerPoint
    presentation = PowerPoint.Presentations.Open(r"C:\Users\mrudu\OneDrive\Documents\English_presentation[1]  -  Read-Only.pptx")
except Exception as e:
    print("❌ Error opening PowerPoint:", e)
    sys.exit(1)

presentation.SlideShowSettings.Run()
time.sleep(2)  # Allow slideshow window to appear

# SlideShow view
slide_show = presentation.SlideShowWindow.View

# === Window Management ===
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
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

# Cooldown to prevent repeated triggers
last_action_time = 0
cooldown = 1.0  # seconds

def fingers_up(hand_landmarks):
    """Detect which fingers are up (1=up, 0=down)."""
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb (consider x-axis, left vs right hand)
    if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other 4 fingers (y-axis)
    for id in range(1, 5):
        if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

camera_hidden = True  # 🔥 Always keep OpenCV window hidden

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    gesture = "UNKNOWN"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            fingers = fingers_up(hand_landmarks)
            current_time = time.time()

            if current_time - last_action_time > cooldown:
                # Open palm (all fingers up): Next Slide
                if fingers == [1,1,1,1,1]:
                    gesture = "OPEN PALM → Next Slide"
                    slide_show.Next()
                    last_action_time = current_time

                # Fist (all fingers down): Previous Slide
                elif fingers == [0,0,0,0,0]:
                    gesture = "FIST → Previous Slide"
                    slide_show.Previous()
                    last_action_time = current_time

                # Thumb + index up (peace sign): Hide camera (no-op now)
                elif fingers == [1,1,0,0,0]:
                    gesture = "THUMB+INDEX UP → Hide Camera"
                    camera_hidden = True
                    try:
                        ppt_win.activate()
                    except Exception:
                        pass
                    last_action_time = current_time

                # Two fingers up (index and middle): Exit slideshow
                elif fingers == [0,1,1,0,0]:
                    gesture = "TWO FINGERS → Exit Slideshow"
                    slide_show.Exit()
                    last_action_time = current_time

    # 🔥 No cv2.imshow here → no black window ever shown

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC to exit
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
try:
    presentation.Close()
    PowerPoint.Quit()
except:
    pass