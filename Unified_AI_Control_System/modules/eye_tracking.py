"""
Eye Tracking Control Module
Controls cursor with eye movements and blink detection
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
from shared.utils import calculate_ear, normalize_to_screen, MouseSmoother
from shared.model_manager import ModelManager
import config


class EyeTrackingModule:
    """Eye tracking control for cursor movement and clicking"""
    
    def __init__(self):
        self.name = "Eye Tracking"
        self.enabled = False
        self.model_manager = ModelManager()
        self.detector = None
        self.smoother = MouseSmoother(buffer_size=config.EYE_SMOOTHING_BUFFER)
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Eye landmark indices
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.PUPIL_R_INDEX = 468
        
        # Blink state
        self.blink_cooldown = 0
        self.last_blink_time = 0
        
    def initialize(self):
        """Initialize the eye tracking detector"""
        try:
            self.detector = self.model_manager.get_face_detector(num_faces=1)
            self.enabled = True
            print(f"[{self.name}] Initialized successfully")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to initialize: {e}")
            return False
    
    def process_frame(self, frame):
        """
        Process frame for eye tracking
        Returns: (processed_frame, events_dict)
        """
        if not self.enabled or self.detector is None:
            return frame, {}
        
        events = {
            'cursor_moved': False,
            'clicked': False,
            'ear': 0.0
        }
        
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        try:
            detection_result = self.detector.detect(mp_image)
            
            if detection_result.face_landmarks:
                face_landmarks = detection_result.face_landmarks[0]
                
                # 1. Blink Detection (Left Eye)
                left_eye_pts = np.array([
                    [face_landmarks[i].x, face_landmarks[i].y] 
                    for i in self.LEFT_EYE_INDICES
                ])
                ear = calculate_ear(left_eye_pts)
                events['ear'] = ear
                
                # Blink detection with cooldown
                current_time = time.time()
                if ear < config.EAR_THRESHOLD and (current_time - self.last_blink_time) > 0.5:
                    pyautogui.click()
                    events['clicked'] = True
                    self.last_blink_time = current_time
                    cv2.putText(frame, "CLICK", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # 2. Cursor Positioning (Right Pupil)
                pupil = face_landmarks[self.PUPIL_R_INDEX]
                
                # Sensitivity adjustment
                adj_x = 0.5 + (pupil.x - 0.5) * config.EYE_MOVE_GAIN
                adj_y = 0.5 + (pupil.y - 0.5) * config.EYE_MOVE_GAIN
                
                target_x, target_y = normalize_to_screen((adj_x, adj_y), 
                                                          self.screen_w, self.screen_h)
                smooth_x, smooth_y = self.smoother.smooth(target_x, target_y)
                
                sx, sy = int(smooth_x), int(smooth_y)
                pyautogui.moveTo(sx, sy, _pause=False)
                events['cursor_moved'] = True
                
                # 3. Visualization
                px, py = int(pupil.x * w), int(pupil.y * h)
                cv2.circle(frame, (px, py), 5, (0, 255, 0), -1)
                
                # Draw  eye landmarks
                for i in self.LEFT_EYE_INDICES + self.RIGHT_EYE_INDICES:
                    pt = face_landmarks[i]
                    cv2.circle(frame, (int(pt.x * w), int(pt.y * h)), 1, (255, 255, 255), -1)
                
                # Show EAR value
                cv2.putText(frame, f"EAR: {ear:.2f}", (w-150, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            else:
                # No face detected warning
                cv2.rectangle(frame, (50, h//2 - 30), (w-50, h//2 + 30), (0, 0, 255), 2)
                cv2.putText(frame, "NO FACE DETECTED", (70, h//2 + 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        except Exception as e:
            print(f"[{self.name}] Processing error: {e}")
        
        return frame, events
    
    def toggle(self):
        """Toggle module on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def cleanup(self):
        """Cleanup resources"""
        self.smoother.reset()
        print(f"[{self.name}] Cleaned up")
