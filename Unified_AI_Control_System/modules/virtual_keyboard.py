"""
Virtual Keyboard Module
Hand gesture-controlled virtual keyboard for typing
"""

import cv2
import mediapipe as mp
import numpy as np
import math
from pynput.keyboard import Controller
from shared.model_manager import ModelManager
from shared.utils import calculate_distance
import config


class Button:
    """Virtual keyboard button"""
    def __init__(self, pos, text, size=[70, 70]):
        self.pos = pos
        self.size = size
        self.text = text


class VirtualKeyboardModule:
    """Virtual keyboard controlled by hand gestures"""
    
    def __init__(self):
        self.name = "Virtual Keyboard"
        self.enabled = False
        self.model_manager = ModelManager()
        self.detector = None
        self.keyboard = Controller()
        
        # Keyboard layouts
        self.keys_upper = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "←"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "SP"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "⇧"]
        ]
        
        self.keys_lower = [
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "←"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "SP"],
            ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "⇧"]
        ]
        
        # Create button lists
        self.button_list_upper = self._create_button_list(self.keys_upper)
        self.button_list_lower = self._create_button_list(self.keys_lower)
        
        # State
        self.text_buffer = ""
        self.app_mode = 0  # 0 = upper, 1 = lower
        self.delay_counter = 0
        
    def _create_button_list(self, layout):
        """Create button objects from layout"""
        buttons = []
        for i in range(len(layout)):
            for j, key_text in enumerate(layout[i]):
                x = config.VKBD_SPACING * j + config.VKBD_OFFSET
                y = config.VKBD_SPACING * i + config.VKBD_OFFSET
                buttons.append(Button([x, y], key_text, config.VKBD_BUTTON_SIZE))
        return buttons
    
    def _draw_all_buttons(self, img, button_list):
        """Draw all keyboard buttons"""
        for button in button_list:
            x, y = button.pos
            w, h = button.size
            cv2.rectangle(img, (x, y), (x + w, y + h), (96, 96, 96), cv2.FILLED)
            cv2.putText(img, button.text, (x + 10, y + 40),
                       cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        return img
    
    def initialize(self):
        """Initialize virtual keyboard"""
        try:
            self.detector = self.model_manager.get_hand_detector(num_hands=1)
            self.enabled = True
            print(f"[{self.name}] Initialized successfully")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to initialize: {e}")
            return False
    
    def process_frame(self, frame):
        """
        Process frame for virtual keyboard input
        Returns: (processed_frame, events_dict)
        """
        if not self.enabled or self.detector is None:
            return frame, {'active': False}
        
        events = {
            'active': True,
            'key_pressed': None,
            'text': self.text_buffer
        }
        
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        try:
            detection_result = self.detector.detect(mp_image)
            
            # Draw keyboard
            active_buttons = self.button_list_upper if self.app_mode == 0 else self.button_list_lower
            frame = self._draw_all_buttons(frame, active_buttons)
            
            landmarks = []
            
            if detection_result.hand_landmarks:
                for hand_landmarks in detection_result.hand_landmarks:
                    for idx, lm in enumerate(hand_landmarks):
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        landmarks.append([idx, cx, cy])
            
            if landmarks and len(landmarks) >= 21:
                # Get finger positions
                x8, y8 = landmarks[8][1], landmarks[8][2]    # Index tip
                x6, y6 = landmarks[6][1], landmarks[6][2]    # Index PIP
                x12, y12 = landmarks[12][1], landmarks[12][2]  # Middle tip
                
                # Visual feedback
                cv2.circle(frame, (x8, y8), 20, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (x12, y12), 20, (255, 0, 255), cv2.FILLED)
                
                # Check if index finger is extended
                if y6 > y8:
                    for button in active_buttons:
                        bx, by = button.pos
                        bw, bh = button.size
                        
                        # Check if finger is over button
                        if bx < x8 < bx + bw and by < y8 < by + bh:
                            # Hover effect
                            cv2.rectangle(frame, (bx - 5, by - 5), (bx + bw + 5, by + bh + 5),
                                        (160, 160, 160), cv2.FILLED)
                            cv2.putText(frame, button.text, (bx + 20, by + 65),
                                      cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            
                            # Check for pinch gesture (click)
                            click_dist = calculate_distance(x8, y8, x12, y12)
                            
                            if click_dist < config.VKBD_CLICK_THRESHOLD and self.delay_counter == 0:
                                k = button.text
                                
                                # Visual click feedback
                                cv2.rectangle(frame, (bx - 5, by - 5), (bx + bw + 5, by + bh + 5),
                                            (255, 255, 255), cv2.FILLED)
                                cv2.putText(frame, k, (bx + 20, by + 65),
                                          cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)
                                
                                # Handle button actions
                                if k == "SP":
                                    self.text_buffer += " "
                                    self.keyboard.press(' ')
                                    self.keyboard.release(' ')
                                elif k == "←":
                                    if self.text_buffer:
                                        self.text_buffer = self.text_buffer[:-1]
                                        self.keyboard.press('\b')
                                        self.keyboard.release('\b')
                                elif k == "⇧":
                                    # Toggle case
                                    self.app_mode = 1 if self.app_mode == 0 else 0
                                else:
                                    # Type character
                                    self.text_buffer += k
                                    self.keyboard.press(k)
                                    self.keyboard.release(k)
                                
                                events['key_pressed'] = k
                                self.delay_counter = 1
            
            # Handle delay counter
            if self.delay_counter != 0:
                self.delay_counter += 1
                if self.delay_counter > config.VKBD_DELAY_FRAMES:
                    self.delay_counter = 0
            
            # Draw text buffer
            buffer_y = h - 120
            cv2.rectangle(frame, (20, buffer_y), (w - 20, buffer_y + 100), 
                         (255, 255, 255), cv2.FILLED)
            
            # Truncate text if too long
            display_text = self.text_buffer[-40:] if len(self.text_buffer) > 40 else self.text_buffer
            cv2.putText(frame, display_text, (30, buffer_y + 70),
                       cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
        
        except Exception as e:
            print(f"[{self.name}] Processing error: {e}")
        
        return frame, events
    
    def clear_buffer(self):
        """Clear text buffer"""
        self.text_buffer = ""
    
    def toggle(self):
        """Toggle module on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def cleanup(self):
        """Cleanup resources"""
        self.text_buffer = ""
        print(f"[{self.name}] Cleaned up")
