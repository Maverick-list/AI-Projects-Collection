
import cv2
import mediapipe as mp
import time
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

class HandTracker:
    def __init__(self, model_path='models/hand_landmarker.task', max_hands=1):
        self.max_hands = max_hands
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO)
        
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None

    def find_hands(self, img, draw=True):
        # MediaPipe Tasks API requires MP Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Timestamp is required for VIDEO mode
        timestamp_ms = int(time.time() * 1000)
        self.results = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        # Drawing is manual in new API or needs helpers. 
        # We'll do manual drawing matching legacy style for consistency
        if draw and self.results.hand_landmarks:
             for hand_landmarks in self.results.hand_landmarks:
                h, w, c = img.shape
                # Draw connections
                # We need a list of connections. Hand connections are constant.
                # mp.solutions.hands.HAND_CONNECTIONS is standard
                # Map to points
                points = []
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    points.append((cx, cy))
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                kj k
                # Draw lines (simplified list of connections)
                connections = [
                    (0,1), (1,2), (2,3), (3,4), # Thumb
                    (0,5), (5,6), (6,7), (7,8), # Index
                    (5,9), (9,10), (10,11), (11,12), # Middle
                    (9,13), (13,14), (14,15), (15,16), # Ring
                    (13,17), (17,18), (18,19), (19,20), # Pinky
                    (0,17) # Base
                ]
                for p1, p2 in connections:
                    cv2.line(img, points[p1], points[p2], (255, 255, 255), 2)

        return img

    def find_position(self, img, hand_no=0, draw=True):
        lm_list = []
        if self.results.hand_landmarks and len(self.results.hand_landmarks) > hand_no:
            my_hand = self.results.hand_landmarks[hand_no]
            h, w, c = img.shape
            for id, lm in enumerate(my_hand):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
                # We already drew in find_hands, avoid double drawing or customize here
        return lm_list

    def fingers_up(self, lm_list):
        fingers = []
        if not lm_list:
            return fingers

        # Thumb (Simple X check for right hand)
        # Tip 4, IP 3
        if lm_list[4][1] < lm_list[3][1]: 
             fingers.append(1)
        else:
             fingers.append(0)

        # 4 Fingers
        for id in range(8, 21, 4):
            if lm_list[id][2] < lm_list[id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
