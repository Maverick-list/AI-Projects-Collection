"""
Hand Gesture Control Module
Controls cursor with hand gestures, supports clicking, scrolling, volume control
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from shared.model_manager import ModelManager
from shared.utils import ExponentialSmoother
from modules.hand_tracking import HandTracker
from modules.gesture_recognition import GestureRecognizer
from modules.input_controller import InputController
import config


class HandGestureModule:
    """Hand gesture control for various system actions"""
    
    def __init__(self):
        self.name = "Hand Gesture"
        self.enabled = False
        self.model_manager = ModelManager()
        
        # Initialize components
        self.tracker = None
        self.gesture_recognizer = None
        self.controller = None
        
        # State
        self.is_active = True
        self.current_mode_text = "NONE"
        self.switch_cooldown = 0
        
    def initialize(self):
        """Initialize the hand gesture system"""
        try:
            # Ensure hand detector is loaded
            self.model_manager.get_hand_detector(num_hands=1)
            
            # Initialize components
            self.tracker = HandTracker()
            self.gesture_recognizer = GestureRecognizer()
            self.controller = InputController()
            
            self.enabled = True
            print(f"[{self.name}] Initialized successfully")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to initialize: {e}")
            return False
    
    def process_frame(self, frame):
        """
        Process frame for hand gesture recognition
        Returns: (processed_frame, events_dict)
        """
        if not self.enabled or not self.is_active:
            # Show inactive status
            cv2.putText(frame, "HAND GESTURE: INACTIVE", (20, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame, {'active': False}
        
        events = {
            'active': True,
            'gesture': 'NONE',
            'action': None
        }
        
        try:
            # Detect hands
            frame = self.tracker.find_hands(frame)
            lm_list = self.tracker.find_position(frame)
            fingers_up = self.tracker.fingers_up(lm_list)
            
            gesture_name = "NONE"
            val = None
            color = (255, 255, 255)
            
            if lm_list:
                # Recognize gesture
                gesture_name, val = self.gesture_recognizer.recognize(lm_list, fingers_up)
                events['gesture'] = gesture_name
                
                # Execute actions based on gesture
                if gesture_name == "MOVE":
                    self.controller.move_mouse(val[1], val[2])
                    color = config.COLOR_MOUSE
                    self.current_mode_text = "CURSOR"
                    events['action'] = 'move'
                
                elif gesture_name == "CLICK":
                    self.controller.move_mouse(val[1], val[2])
                    self.controller.click()
                    color = config.COLOR_CLICK
                    self.current_mode_text = "CLICK"
                    events['action'] = 'click'
                
                elif gesture_name == "RCLICK":
                    self.controller.move_mouse(val[1], val[2])
                    self.controller.right_click()
                    color = config.COLOR_CLICK
                    self.current_mode_text = "RIGHT CLICK"
                    events['action'] = 'right_click'
                
                elif gesture_name == "SCROLL":
                    if val[2] < config.CAM_HEIGHT / 2 - config.SCROLL_ZONE_HEIGHT:
                        self.controller.scroll(10)
                        self.current_mode_text = "SCROLL UP"
                    elif val[2] > config.CAM_HEIGHT / 2 + config.SCROLL_ZONE_HEIGHT:
                        self.controller.scroll(-10)
                        self.current_mode_text = "SCROLL DOWN"
                    color = config.COLOR_SCROLL
                    events['action'] = 'scroll'
                
                elif gesture_name == "SWITCH_MODE":
                    if time.time() - self.switch_cooldown > 1.0:
                        if val[1] > config.CAM_WIDTH - config.SWITCH_EDGE_WIDTH:
                            self.controller.switch_window('right')
                            self.switch_cooldown = time.time()
                            self.current_mode_text = "NEXT DESKTOP"
                        elif val[1] < config.SWITCH_EDGE_WIDTH:
                            self.controller.switch_window('left')
                            self.switch_cooldown = time.time()
                            self.current_mode_text = "PREV DESKTOP"
                        else:
                            self.current_mode_text = "SWITCH READY"
                    else:
                        self.current_mode_text = "SWITCH COOLDOWN"
                    color = config.COLOR_SWITCH
                    events['action'] = 'switch'
                
                elif gesture_name == "VOL_UP":
                    self.controller.volume_up()
                    self.current_mode_text = "VOL UP"
                    color = config.COLOR_VOL
                    events['action'] = 'volume_up'
                
                elif gesture_name == "VOL_DOWN":
                    self.controller.volume_down()
                    self.current_mode_text = "VOL DOWN"
                    color = config.COLOR_VOL
                    events['action'] = 'volume_down'
                
                else:
                    self.current_mode_text = "NEUTRAL"
            
            # Draw ROI box
            cv2.rectangle(frame, 
                         (config.HAND_FRAME_MARGIN_X, config.HAND_FRAME_MARGIN_Y),
                         (config.CAM_WIDTH - config.HAND_FRAME_MARGIN_X, 
                          config.CAM_HEIGHT - config.HAND_FRAME_MARGIN_Y),
                         (255, 0, 255), 2)
            
            # Show status
            cv2.putText(frame, f"Mode: {self.current_mode_text}", (20, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        except Exception as e:
            print(f"[{self.name}] Processing error: {e}")
        
        return frame, events
    
    def toggle(self):
        """Toggle module on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def toggle_active(self):
        """Toggle active state (prevents accidental clicks)"""
        self.is_active = not self.is_active
        return self.is_active
    
    def cleanup(self):
        """Cleanup resources"""
        print(f"[{self.name}] Cleaned up")
