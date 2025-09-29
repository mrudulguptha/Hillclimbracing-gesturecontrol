import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

print("👉 Controls for Hill Climb Racing:")
print("✋ Open Palm  = Accelerate (Right Arrow)")
print("✊ Fist       = Brake/Reverse (Left Arrow)")
print("Press ESC to exit")

def count_fingers(hand_landmarks, frame_w, frame_h):
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    count = 0
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 2].x:
        count += 1
    return count

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = count_fingers(hand_landmarks, w, h)
            if fingers >= 4:
                pyautogui.keyDown("right")
                pyautogui.keyUp("left")
                cv2.putText(frame, "Accelerate", (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)
            elif fingers == 0:
                pyautogui.keyDown("left")
                pyautogui.keyUp("right")
                cv2.putText(frame, "Brake/Reverse", (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2)
            else:
                pyautogui.keyUp("left")
                pyautogui.keyUp("right")

    small_frame = cv2.resize(frame, (850, 450))
    cv2.imshow("Gesture Camera", small_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
