import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui 
import numpy as np
import time
import os
import requests
from utils import calculate_ear, normalize_to_screen, MouseSmoother

# Initialize PyAutoGUI
pyautogui.FAILSAFE = True

# Screen Dimensions
SCREEN_W, SCREEN_H = pyautogui.size()

# Constants
EAR_THRESHOLD = 0.25
FPS_SMOOTHING = 0.9
MODEL_PATH = "face_landmarker.task"
MOVE_GAIN = 2.0  # Increased sensitivity
CENTER_THRESHOLD = 0.05 # Deadzone prevention if needed

# Download model if not exists
def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading Face Landmarker model...")
        url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        r = requests.get(url)
        with open(MODEL_PATH, "wb") as f:
            f.write(r.content)
        print("Model downloaded.")

# Landmark Indices (Mapping for Tasks API)
# The Tasks API returns 478 landmarks. 
# Left eye: 362, 385, 387, 263, 373, 380
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
# Right eye: 33, 160, 158, 133, 153, 144
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
# Right Pupil (Iris center approx): 468
PUPIL_R_INDEX = 468

def main():
    download_model()
    
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    smoother = MouseSmoother(buffer_size=5)
    prev_time = 0
    fps = 0
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        detection_result = detector.detect(mp_image)

        if detection_result.face_landmarks:
            face_landmarks = detection_result.face_landmarks[0]
            
            # 1. Blink Detection (Left Eye)
            left_eye_pts = np.array([
                [face_landmarks[i].x, face_landmarks[i].y] 
                for i in LEFT_EYE_INDICES
            ])
            ear = calculate_ear(left_eye_pts)
            
            if ear < EAR_THRESHOLD:
                pyautogui.click()
                cv2.putText(frame, "CLICK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 2. Cursor Positioning
            pupil = face_landmarks[PUPIL_R_INDEX]
            
            # Sensitivity Adjustment: Center the coordinates around 0.5 and multiply by GAIN
            # This makes small eye movements correspond to larger screen movements
            adj_x = 0.5 + (pupil.x - 0.5) * MOVE_GAIN
            adj_y = 0.5 + (pupil.y - 0.5) * MOVE_GAIN
            
            target_x, target_y = normalize_to_screen((adj_x, adj_y), SCREEN_W, SCREEN_H)
            smooth_x, smooth_y = smoother.smooth(target_x, target_y)
            
            # Final screen coordinates
            sx, sy = int(smooth_x), int(smooth_y)
            
            # Optional: Print debug every 30 frames
            if int(time.time() * 30) % 30 == 0:
                print(f"Pupil: ({pupil.x:.3f}, {pupil.y:.3f}) -> Screen: ({sx}, {sy})")
                
            pyautogui.moveTo(sx, sy, _pause=False)
            
            # 3. Visualization
            px, py = int(pupil.x * w), int(pupil.y * h)
            cv2.circle(frame, (px, py), 5, (0, 255, 0), -1)
            
            for i in LEFT_EYE_INDICES + RIGHT_EYE_INDICES:
                pt = face_landmarks[i]
                cv2.circle(frame, (int(pt.x * w), int(pt.y * h)), 1, (255, 255, 255), -1)
            
            cv2.putText(frame, f"EAR: {ear:.2f}", (w-150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        else:
            cv2.rectangle(frame, (50, h//2 - 30), (w-50, h//2 + 30), (0, 0, 255), -1)
            cv2.putText(frame, "WARNING: NO FACE DETECTED", (70, h//2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        curr_time = time.time()
        fps = (fps * FPS_SMOOTHING) + ((1 / (curr_time - prev_time)) * (1 - FPS_SMOOTHING)) if prev_time != 0 else 0
        prev_time = curr_time
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow('AI Mouse Visualization by Eyes', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: break
        elif key == ord('s'):
            cv2.imwrite(f"screenshot_{int(time.time())}.png", frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
