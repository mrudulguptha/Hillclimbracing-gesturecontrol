# Simple Paint App using OpenCV (no deep learning, just fun drawing)

import cv2
import numpy as np

# Canvas size and initial state
canvas = np.ones((600, 800, 3), dtype=np.uint8) * 255
drawing = False
ix, iy = -1, -1
color = (0, 0, 255)  # Red color
thickness = 5

# Mouse callback function
def draw(event, x, y, flags, param):
    global ix, iy, drawing, canvas

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.line(canvas, (ix, iy), (x, y), color, thickness)
            ix, iy = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.line(canvas, (ix, iy), (x, y), color, thickness)

cv2.namedWindow("Paint")
cv2.setMouseCallback("Paint", draw)

print("Press 'c' to clear, 's' to save, 'q' to quit.")

while True:
    cv2.imshow("Paint", canvas)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas[:] = 255  # Clear the canvas
    elif key == ord('s'):
        cv2.imwrite("my_painting.jpg", canvas)
        print("Saved as my_painting.jpg")

cv2.destroyAllWindows()
