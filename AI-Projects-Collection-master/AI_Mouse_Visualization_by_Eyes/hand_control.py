import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import requests

class HandController:
    def __init__(self, model_path="hand_landmarker.task"):
        self.model_path = model_path
        self._download_model()
        
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # Landmark Indices (Standard MediaPipe Hand)
        self.WRIST = 0
        self.THUMB_TIP = 4
        self.INDEX_FINGER_TIP = 8
        self.MIDDLE_FINGER_TIP = 12
        self.RING_FINGER_TIP = 16
        self.PINKY_TIP = 20

    def _download_model(self):
        if not os.path.exists(self.model_path):
            print("Downloading Hand Landmarker model...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            r = requests.get(url)
            with open(self.model_path, "wb") as f:
                f.write(r.content)
            print("Model downloaded.")

    def process_frame(self, frame, timestamp_ms):
        """Detects hand landmarks for video mode."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.detector.detect_for_video(mp_image, timestamp_ms)

    def get_gesture(self, hand_landmarks):
        """
        Recognizes gestures based on normalized landmarks.
        hand_landmarks: result.hand_landmarks[0] list of landmarks
        """
        if not hand_landmarks:
            return None
            
        # Finger states (Open/Closed)
        fingers_open = []
        
        # Thumb: Tip vs IP (landmark 3) x-position (assuming right hand / mirrored)
        # For simplicity, use distance from wrist or similar to handle both hands
        thumb_tip = hand_landmarks[self.THUMB_TIP]
        thumb_ip = hand_landmarks[self.THUMB_TIP - 1]
        wrist = hand_landmarks[self.WRIST]
        
        # Thumb openness (horizontal distance from wrist relative to IP)
        fingers_open.append(abs(thumb_tip.x - wrist.x) > abs(thumb_ip.x - wrist.x))
        
        # Others (y-position vs PIP joint)
        for tip_idx in [8, 12, 16, 20]:
            tip = hand_landmarks[tip_idx]
            pip = hand_landmarks[tip_idx - 2]
            fingers_open.append(tip.y < pip.y)
            
        num_open = sum(fingers_open)
        
        # 1. Thumbs Up/Down
        if fingers_open[0] and num_open == 1:
            if thumb_tip.y < wrist.y - 0.1: # Upwards
                return "VOLUME_UP"
            elif thumb_tip.y > wrist.y + 0.1: # Downwards
                return "VOLUME_DOWN"
                
        # 2. Scroll: 2 fingers up (Index + Middle)
        if fingers_open[1] and fingers_open[2] and num_open == 2:
            return "SCROLL"
            
        # 3. Screenshot: Thumb + Pinky open (Legacy camera gesture)
        if fingers_open[0] and fingers_open[4] and num_open == 2:
            return "SCREENSHOT"
            
        # 4. Confirming: All open
        if num_open >= 4:
            return "CONFIRM"
            
        return None

    def draw_landmarks(self, frame, hand_landmarks):
        """Manual drawing since mp_drawing is often missing on macOS Silicon."""
        if not hand_landmarks:
            return
        h, w, _ = frame.shape
        # Draw connections (simplified list of standard hand connections)
        connections = [
            (0,1), (1,2), (2,3), (3,4), # Thumb
            (0,5), (5,6), (6,7), (7,8), # Index
            (9,10), (10,11), (11,12),   # Middle
            (13,14), (14,15), (15,16), # Ring
            (0,17), (17,18), (18,19), (19,20), # Pinky
            (5,9), (9,13), (13,17) # Palm
        ]
        for start, end in connections:
            p1 = hand_landmarks[start]
            p2 = hand_landmarks[end]
            cv2.line(frame, (int(p1.x*w), int(p1.y*h)), (int(p2.x*w), int(p2.y*h)), (0, 255, 0), 2)
        
        for lm in hand_landmarks:
            cv2.circle(frame, (int(lm.x*w), int(lm.y*h)), 4, (255, 0, 0), -1)
