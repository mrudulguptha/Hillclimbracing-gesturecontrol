import cv2

def cartoonify_webcam():
    cap = cv2.VideoCapture(0)  # Use default webcam

    if not cap.isOpened():
        print("Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Resize for better performance
        frame = cv2.resize(frame, (640, 480))

        # Convert to grayscale and apply median blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)

        # Edge detection
        edges = cv2.adaptiveThreshold(gray_blur, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)

        # Apply bilateral filter to smooth color regions
        color = cv2.bilateralFilter(frame, 9, 250, 250)

        # Combine edges and smoothed image
        cartoon = cv2.bitwise_and(color, color, mask=edges)

        # Show output
        cv2.imshow("Cartoonified Webcam", cartoon)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Run it
cartoonify_webcam()
