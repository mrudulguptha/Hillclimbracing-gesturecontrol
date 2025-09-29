import cv2

print("OpenCV version:", cv2.__version__)

# Load the Haar cascade file for face detection
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
print("Cascade path:", cascade_path)
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    print("Error: Could not load Haar cascade xml file.")
    exit()

# Start video capture from webcam
cap = cv2.VideoCapture(0)

# Check if the webcam opens correctly
if not cap.isOpened():
    print("Error: Could not open webcam. Check if it's connected and not used by another application.")
    exit()

print("Webcam opened successfully. Press 'q' to quit.")

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to read frame from webcam.")
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame with rectangles
    cv2.imshow('Face Detection - Press q to quit', frame)

    # Wait for key press - if 'q' is pressed, break the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting...")
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()