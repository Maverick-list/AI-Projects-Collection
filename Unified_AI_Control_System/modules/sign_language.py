"""
Sign Language Translation Module
Recognizes sign language gestures and converts to speech
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from shared.model_manager import ModelManager
from modules.gestures import GestureDetector
from modules.speech import SpeechManager
import config


class SignLanguageModule:
    """Sign language gesture recognition and speech output"""
    
    def __init__(self):
        self.name = "Sign Language"
        self.enabled = False
        self.model_manager = ModelManager()
        self.detector = None
        
        # Components
        self.gesture_classifier = None
        self.speech_mgr = None
        
        # State
        self.current_gestures = [None, None]
        self.consecutive_frames = [0, 0]
        self.history = []
        self.language = config.SIGN_DEFAULT_LANGUAGE
        
    def initialize(self):
        """Initialize sign language detector"""
        try:
            self.detector = self.model_manager.get_hand_detector(num_hands=2)
            self.gesture_classifier = GestureDetector()
            self.speech_mgr = SpeechManager()
            
            self.enabled = True
            print(f"[{self.name}] Initialized successfully")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to initialize: {e}")
            return False
    
    def process_frame(self, frame):
        """
        Process frame for sign language recognition
        Returns: (processed_frame, events_dict)
        """
        if not self.enabled or self.detector is None:
            return frame, {'active': False}
        
        events = {
            'active': True,
            'gesture': None,
            'phrase': None,
            'spoken': False
        }
        
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        try:
            detection_result = self.detector.detect(mp_image)
            
            detected_per_frame = []
            
            if detection_result.hand_landmarks:
                for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
                    # Draw landmarks
                    for landmark in hand_landmarks:
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
                    
                    # Detect gesture
                    gesture, conf = self.gesture_classifier.detect_gesture(hand_landmarks)
                    detected_per_frame.append(gesture)
                    
                    if i < len(self.current_gestures):
                        if gesture == self.current_gestures[i]:
                            self.consecutive_frames[i] += 1
                        else:
                            self.current_gestures[i] = gesture
                            self.consecutive_frames[i] = 1
                    
                    # Check if stable enough to speak
                    if gesture and self.consecutive_frames[i] >= config.SIGN_STABILITY_THRESHOLD:
                        phrase = gesture
                        
                        # Check for combo gestures
                        if len(detected_per_frame) == 2:
                            combo = self.gesture_classifier.detect_combo(detected_per_frame)
                            if combo:
                                phrase = combo
                        
                        # Speak if new phrase
                        if not self.history or self.history[-1][0] != phrase:
                            self.speech_mgr.speak(phrase)
                            self.history.append((phrase, time.strftime("%H:%M:%S")))
                            if len(self.history) > 10:
                                self.history.pop(0)
                            
                            events['phrase'] = phrase
                            events['spoken'] = True
                            
                        self.consecutive_frames[i] = 0
            
            # Draw history sidebar
            sidebar_x = w - 250
            cv2.rectangle(frame, (sidebar_x, 0), (w, h), (30, 30, 30), -1)
            cv2.putText(frame, "HISTORY", (sidebar_x + 10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            for idx, (item, tm) in enumerate(reversed(self.history)):
                y_pos = 65 + (idx * 30)
                if y_pos > h - 50:
                    break
                text = f"{tm}: {item[:15]}"
                cv2.putText(frame, text, (sidebar_x + 10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        except Exception as e:
            print(f"[{self.name}] Processing error: {e}")
        
        return frame, events
    
    def toggle_language(self):
        """Toggle between English and Indonesian"""
        self.language = 'id' if self.language == 'en' else 'en'
        return self.language
    
    def toggle(self):
        """Toggle module on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def cleanup(self):
        """Cleanup resources"""
        self.history = []
        print(f"[{self.name}] Cleaned up")
