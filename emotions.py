import cv2
from fer import FER  # ✅ Correct import

# Initialize the FER emotion detector
emotion_detector = FER(mtcnn=True)  # You can change to mtcnn=False if it crashes

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Webcam started. Press 'q' to quit.")

# Emojis for emotions
emoji_dict = {
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'surprise': '😮',
    'neutral': '😐',
    'fear': '😱',
    'disgust': '🤢'
}

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Detect emotions in the frame
    results = emotion_detector.detect_emotions(frame)

    for result in results:
        (x, y, w, h) = result['box']
        emotions = result['emotions']
        top_emotion = max(emotions, key=emotions.get)
        emoji = emoji_dict.get(top_emotion, '🙂')

        # Draw bounding box and label
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{emoji} {top_emotion}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # Display the result
    cv2.imshow("Emotion Detection - Press 'q' to quit", frame)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting...")
        break

# Release camera and close window
cap.release()
cv2.destroyAllWindows()
