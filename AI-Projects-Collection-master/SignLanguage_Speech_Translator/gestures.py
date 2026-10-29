import numpy as np

class GestureDetector:
    def __init__(self):
        # MediaPipe Hand Landmark Indices
        self.WRIST = 0
        self.THUMB_CMC = 1
        self.THUMB_MCP = 2
        self.THUMB_IP = 3
        self.THUMB_TIP = 4
        self.INDEX_MCP = 5
        self.INDEX_PIP = 6
        self.INDEX_DIP = 7
        self.INDEX_TIP = 8
        self.MIDDLE_MCP = 9
        self.MIDDLE_PIP = 10
        self.MIDDLE_DIP = 11
        self.MIDDLE_TIP = 12
        self.RING_MCP = 13
        self.RING_PIP = 14
        self.RING_DIP = 15
        self.RING_TIP = 16
        self.PINKY_MCP = 17
        self.PINKY_PIP = 18
        self.PINKY_DIP = 19
        self.PINKY_TIP = 20

    def get_finger_states(self, landmarks):
        """Returns a dict of finger states (True for open, False for closed)"""
        states = {
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinky": False
        }
        
        # Standard fingers
        states["index"] = landmarks[self.INDEX_TIP].y < landmarks[self.INDEX_PIP].y
        states["middle"] = landmarks[self.MIDDLE_TIP].y < landmarks[self.MIDDLE_PIP].y
        states["ring"] = landmarks[self.RING_TIP].y < landmarks[self.RING_PIP].y
        states["pinky"] = landmarks[self.PINKY_TIP].y < landmarks[self.PINKY_PIP].y
        
        # Thumb: Tip vs IP joint
        thumb_dist = np.linalg.norm([landmarks[self.THUMB_TIP].x - landmarks[self.WRIST].x, 
                                     landmarks[self.THUMB_TIP].y - landmarks[self.WRIST].y])
        thumb_base_dist = np.linalg.norm([landmarks[self.THUMB_IP].x - landmarks[self.WRIST].x, 
                                          landmarks[self.THUMB_IP].y - landmarks[self.WRIST].y])
        states["thumb"] = thumb_dist > thumb_base_dist

        return states

    def detect_gesture(self, landmarks):
        if not landmarks:
            return None, 0.0
            
        states = self.get_finger_states(landmarks)
        finger_values = list(states.values())
        num_open = sum(finger_values)
        
        # Hand rotation vector
        hand_vector = np.array([landmarks[self.INDEX_MCP].x - landmarks[self.WRIST].x, 
                              landmarks[self.INDEX_MCP].y - landmarks[self.WRIST].y])
        angle = np.degrees(np.arctan2(hand_vector[1], hand_vector[0]))
        
        # VIP PRIORITY: 21. Jokowi Fist (Fist upward)
        is_jokowi = self.detect_jokowi_fist(landmarks)
        if is_jokowi:
            return "Hidup Jokowiiie!", 1.0

        # 1. Open hand / 5 Fingers
        if all(finger_values):
            if -110 < angle < -70: # Vertical
                return "Halo, assalamualaikum", 0.95
            elif (0 < angle < 45 or -45 < angle < 0): # Tilted
                return "Bye-bye, assalamualaikum", 0.90
            else:
                return "Nice to meet you", 0.85
                
        # 3. Hand touching chest (Simple: detect near center)
        wrist_pos = landmarks[self.WRIST]
        if 0.4 < wrist_pos.x < 0.6 and 0.6 < wrist_pos.y < 0.9:
            if num_open <= 1:
                return "Aku", 0.80

        # 4. Firza (OK Sign) - Custom Logic
        dist_thumb_index = np.linalg.norm([landmarks[self.THUMB_TIP].x - landmarks[self.INDEX_TIP].x, 
                                           landmarks[self.THUMB_TIP].y - landmarks[self.INDEX_TIP].y])
        if dist_thumb_index < 0.05 and states["middle"] and states["ring"] and states["pinky"]:
            return "Firza", 0.90

        # NEW GESTURES
        
        # 13. Listen (Hand to ear) - High on head side
        if wrist_pos.x < 0.3 or wrist_pos.x > 0.7:
            if wrist_pos.y < 0.4:
                return "Listen", 0.80
                
        # 14. Look (Hand to eye)
        if 0.3 < wrist_pos.x < 0.7 and wrist_pos.y < 0.3:
            return "Look", 0.80
            
        # 15. Eat (Hand to mouth)
        if 0.4 < wrist_pos.x < 0.6 and 0.4 < wrist_pos.y < 0.6:
            if num_open <= 2:
                return "Eat", 0.75
                
        # 16. Fist (No)
        if num_open == 0:
            return "No", 0.95
            
        # 18. Four fingers
        if states["index"] and states["middle"] and states["ring"] and states["pinky"] and not states["thumb"]:
            return "Four", 0.90
            
        # 19. Thumb down (Bad)
        if states["thumb"] and not any([states["index"], states["middle"], states["ring"], states["pinky"]]):
            if landmarks[self.THUMB_TIP].y > landmarks[self.THUMB_MCP].y:
                return "Bad", 0.85
            else:
                return "Good", 0.85 # 6. Good
                
        # 20. Palm down (Stop)
        if all(finger_values) and angle > 45: 
             return "Stop", 0.80

        # 17. Yes (Forward circle - simplified to index circle or nod gesture if handled outside)
        # For now, let's use Index pointing up but shaking? Or just index up.
        if states["index"] and num_open == 1:
            return "Yes", 0.75
            
        # Additional placeholders to reach 20 if needed
        if states["index"] and states["middle"] and num_open == 2:
            return "Peace", 0.90 # 8. Peace
            
        if num_open == 3 and not states["pinky"] and not states["thumb"]:
            return "Three", 0.85 # 9. Three

        return None, 0.0

    def detect_combo(self, gestures):
        """Detect combinations of gestures from multiple hands"""
        if len(gestures) < 2:
            return None
            
        g1, g2 = gestures[0], gestures[1]
        
        if (g1 == "Halo, assalamualaikum" and g2 == "Good") or (g1 == "Good" and g2 == "Halo, assalamualaikum"):
            return "Great to see you, assalamualaikum!"
            
        return None

    def detect_jokowi_fist(self, landmarks):
        """
        Fist: ALL fingers CLOSED (tips 4,8,12,16,20 < threshold to PIP 2,6,10,14,18)
        Hand UP: wrist(0)-middle_mcp(9) angle < -45° (pointing upwards)
        """
        # 1. Check if fist (all fingers closed)
        # Using a strict check for tips vs PIP joints
        is_fist = (landmarks[self.INDEX_TIP].y > landmarks[self.INDEX_PIP].y and
                   landmarks[self.MIDDLE_TIP].y > landmarks[self.MIDDLE_PIP].y and
                   landmarks[self.RING_TIP].y > landmarks[self.RING_PIP].y and
                   landmarks[self.PINKY_TIP].y > landmarks[self.PINKY_PIP].y)
        
        # Thumb check: Tip closer to wrist than CMC/MCP
        thumb_tip_dist = np.linalg.norm([landmarks[self.THUMB_TIP].x - landmarks[self.WRIST].x, 
                                         landmarks[self.THUMB_TIP].y - landmarks[self.WRIST].y])
        thumb_mcp_dist = np.linalg.norm([landmarks[self.THUMB_MCP].x - landmarks[self.WRIST].x, 
                                         landmarks[self.THUMB_MCP].y - landmarks[self.WRIST].y])
        is_fist = is_fist and (thumb_tip_dist < thumb_mcp_dist * 1.5) # Approximate fist thumb

        if not is_fist: return False

        # 2. Check Direction (Pointing Upward)
        # Angle from wrist(0) to middle_mcp(9)
        vec = np.array([landmarks[self.MIDDLE_MCP].x - landmarks[self.WRIST].x, 
                        landmarks[self.MIDDLE_MCP].y - landmarks[self.WRIST].y])
        hand_angle = np.degrees(np.arctan2(vec[1], vec[0]))
        
        # -90 is straight up. Angle < -45 is mostly upward.
        return hand_angle < -45

