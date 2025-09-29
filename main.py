import cv2
import cvzone
import numpy as np
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from fer import FER

# Title for the display window
title = "Reality Warp"

# Initialize the camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize the segmentation model
segmentor = SelfiSegmentation()

# Initialize the FER emotion detector
emotion_detector = FER(mtcnn=True)

# Path to the virtual background image
bg_path = 'Backgrounds/virtual_bg.jpg'

# Generate a solid color image and save as virtual_bg.jpg
bg_img = np.full((720, 1280, 3), (100, 200, 250), dtype=np.uint8)  # Light blue
cv2.imwrite(bg_path, bg_img)

virtual_bg = cv2.imread(bg_path)

# Add a check to see if the image was loaded successfully
if virtual_bg is None:
    print(f"Error: Could not load the image from path: {bg_path}")
    print("Please check the file name and path.")
    exit()

# Resize the background image to match the camera resolution
virtual_bg = cv2.resize(virtual_bg, (1280, 720))

# Define a simple emoji dictionary for demonstration
emoji_dict = {
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'surprised': '😮',
    'neutral': '😐',
    # Add more emotions and corresponding emojis as needed
}

while True:
    # Read a frame from the camera
    success, frame = cap.read()
    if not success:
        break

    # Flip the frame for a more natural mirror view
    frame = cv2.flip(frame, 1)

    # Detect emotions in the frame
    results = emotion_detector.detect_emotions(frame)

    # Resize virtual_bg to match frame size (do not resize frame itself)
    virtual_bg_resized = cv2.resize(virtual_bg, (frame.shape[1], frame.shape[0]))

    for result in results:
        (x, y, w, h) = result['box']
        emotions = result['emotions']
        top_emotion = max(emotions, key=emotions.get)
        emoji = emoji_dict.get(top_emotion, '🙂')

        # Draw bounding box and label
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{emoji} {top_emotion}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # Replace background with resized image (frame is not resized)
    img_out = segmentor.removeBG(frame, virtual_bg_resized)

    # Display the result
    cv2.imshow("Emotion Detection - Press 'q' to quit", img_out)

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and destroy all windows
cap.release()
cv2.destroyAllWindows()