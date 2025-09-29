# Final Code for the "Magic Eraser" using OpenCV and MediaPipe

import cv2
import mediapipe as mp
import numpy as np
import math

# --- Step 1: Initialize MediaPipe and Webcam ---

# Initialize MediaPipe solutions for Hands and Selfie Segmentation
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_selfie_segmentation = mp.solutions.selfie_segmentation
segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0)

# Initialize MediaPipe drawing utilities
mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam
cap = cv.VideoCapture(0)
cap.set(3, 1280) # Set width
cap.set(4, 720)  # Set height

if not cap.isOpened():
    raise IOError("Cannot open webcam")

# --- Step 2: Background Capture and State Variables ---

# This variable will store the clean background frame
background_image = None

# This mask will store all the areas the user has "erased"
erased_mask = None

# --- Step 3: The Main Application Loop ---

while True:
    # Read a frame from the webcam
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the frame horizontally for a mirror-like view
    frame = cv2.flip(frame, 1)

    # On the first frame, initialize the erased_mask with the same dimensions
    if erased_mask is None:
        erased_mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)

    # Convert the BGR image to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # --- Step 4: User Instructions and Key Handling ---
    
    # Display instructions on the screen
    cv2.putText(frame, "Press 'b' to Capture Background", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Press 'c' to Clear Eraser", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Press 'q' to Quit", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Handle key presses
    key = cv2.waitKey(5) & 0xFF
    if key == ord('b'):
        background_image = frame.copy()
        erased_mask.fill(0) # Reset mask when new background is captured
        print("Background captured!")
    elif key == ord('c'):
        erased_mask.fill(0)
        print("Eraser cleared!")
    elif key == ord('q'):
        break

    # The main logic only runs if a background has been captured
    if background_image is not None:
        # Get the segmentation mask for the person
        segmentation_results = segmentation.process(rgb_frame)
        # Create a binary mask where the person is detected
        person_mask = (segmentation_results.segmentation_mask > 0.7).astype('uint8')

        # Process the frame to find hand landmarks
        hand_results = hands.process(rgb_frame)
        
        # --- Step 5: Hand Gesture Recognition and Eraser Logic ---
        
        if hand_results.multi_hand_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            
            # Get coordinates for index finger tip and thumb tip
            h, w, _ = frame.shape
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            ix, iy = int(index_tip.x * w), int(index_tip.y * h)
            tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
            
            # Calculate distance to detect a "pinch"
            distance = math.hypot(ix - tx, iy - ty)

            eraser_radius = 30
            pinch_threshold = 40
            
            if distance < pinch_threshold:
                # If pinching, "paint" on the erased_mask
                cv2.circle(erased_mask, (ix, iy), eraser_radius, (255), -1)
                # Visual feedback: Green circle for active eraser
                cv2.circle(frame, (ix, iy), eraser_radius, (0, 255, 0), 3)
            else:
                # Visual feedback: Red circle for inactive eraser
                cv2.circle(frame, (ix, iy), eraser_radius, (0, 0, 255), 3)
            
            # Draw hand landmarks for visualization
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # --- Step 6: Combine Masks and Create Final Image ---
        
        # The final area to erase is where the person is AND where the user has erased
        final_mask_to_erase = cv2.bitwise_and(person_mask, erased_mask)

        # Convert the mask to 3 channels to use with numpy.where
        final_mask_3ch = cv2.cvtColor(final_mask_to_erase, cv2.COLOR_GRAY2BGR)

        # Where the mask is white (255), show the background. Otherwise, show the current frame.
        output_frame = np.where(final_mask_3ch == 255, background_image, frame)
        
        cv2.imshow('Magic Eraser', output_frame)
    
    else:
        # Before background is captured, just show the normal webcam feed
        cv2.imshow('Magic Eraser', frame)

# --- Step 7: Cleanup ---
cap.release()
cv2.destroyAllWindows()