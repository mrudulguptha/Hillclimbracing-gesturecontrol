import cv2
import numpy as np

# Define upper and lower bounds for the color to detect (e.g., blue color)
lower_color = np.array([100, 150, 0])
upper_color = np.array([140, 255, 255])

# Canvas for drawing
canvas = None
prev_x, prev_y = None, None

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    if canvas is None:
        canvas = np.zeros_like(frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 1000:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if prev_x is not None and prev_y is not None:
                    # Sky blue color
                    cv2.line(canvas, (prev_x, prev_y), center, (235, 206, 135), 5)
                prev_x, prev_y = center
        else:
            prev_x, prev_y = None, None
    else:
        prev_x, prev_y = None, None

    combined = cv2.add(frame, canvas)
    cv2.imshow("Virtual Painter", combined)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        canvas = np.zeros_like(frame)  # Clear
    elif key == ord('s'):
        cv2.imwrite("drawing.png", canvas)  # Save
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
