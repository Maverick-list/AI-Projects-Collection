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
        
        # Index, Middle, Ring, Pinky: Check Tip vs PIP coordinate (usually Y)
        # Assuming vertical hand (inverted Y in image space)
        states["index"] = landmarks[self.INDEX_TIP].y < landmarks[self.INDEX_PIP].y
        states["middle"] = landmarks[self.MIDDLE_TIP].y < landmarks[self.MIDDLE_PIP].y
        states["ring"] = landmarks[self.RING_TIP].y < landmarks[self.RING_PIP].y
        states["pinky"] = landmarks[self.PINKY_TIP].y < landmarks[self.PINKY_PIP].y
        
        # Thumb: Check Tip vs IP joint coordinate (usually X depending on orientation)
        # Simple heuristic: distance from wrist
        thumb_dist = np.linalg.norm([landmarks[self.THUMB_TIP].x - landmarks[self.WRIST].x, 
                                     landmarks[self.THUMB_TIP].y - landmarks[self.WRIST].y])
        thumb_base_dist = np.linalg.norm([landmarks[self.THUMB_IP].x - landmarks[self.WRIST].x, 
                                          landmarks[self.THUMB_IP].y - landmarks[self.WRIST].y])
        states["thumb"] = thumb_dist > thumb_base_dist

        return states

    def detect_gesture(self, landmarks):
        if not landmarks:
            return None
            
        states = self.get_finger_states(landmarks)
        
        # 1. Open hand (5 fingers extended)
        if all(states.values()):
            return "Halo, assalamualaikum"
            
        # 2. Goodbye hand (palm facing camera, hand rotated/ Goodbye motion)
        # Heuristic: Check for open hand + horizontal orientation or specific rotation
        # For simplicity, we can use "All open" but distinct from open hand by checking rotation
        # If the hand is rotated roughly 90 degrees (wrist to index mcp vector)
        hand_vector = np.array([landmarks[self.INDEX_MCP].x - landmarks[self.WRIST].x, 
                              landmarks[self.INDEX_MCP].y - landmarks[self.WRIST].y])
        angle = np.degrees(np.arctan2(hand_vector[1], hand_vector[0]))
        
        # 3. Hand touching chest (hand vertical near center)
        # In MediaPipe, we check normalized coordinates. Center is 0.5, 0.5.
        wrist_pos = landmarks[self.WRIST]
        if 0.4 < wrist_pos.x < 0.6 and 0.6 < wrist_pos.y < 0.9:
            # Check if fingers are closed or relaxed (not a full open hand)
            if not states["index"] and not states["middle"] and not states["ring"] and not states["pinky"]:
                return "Aku"

        # 4. Index finger + thumb open (Firza/OK sign)
        # Thumb tip and index tip are close, other fingers extended
        dist_thumb_index = np.linalg.norm([landmarks[self.THUMB_TIP].x - landmarks[self.INDEX_TIP].x, 
                                           landmarks[self.THUMB_TIP].y - landmarks[self.INDEX_TIP].y])
        if dist_thumb_index < 0.05 and states["middle"] and states["ring"] and states["pinky"]:
            return "Firza"

        # 5. All fingers to camera (Palm facing cam)
        # Similar to Open hand but we can use it for "Nice to meet you"
        # We'll differentiate based on context or a slight variation in logic
        # For this requirement, let's look for all fingers straight but maybe distinct orientation
        # If angle is very specifically vertical
        if -110 < angle < -70 and all(states.values()):
            return "Nice to meet you"
            
        # Redefine Goodbye if specifically tilted
        if (0 < angle < 45 or -45 < angle < 0) and all(states.values()):
            return "Bye-bye, assalamualaikum"

        return None
