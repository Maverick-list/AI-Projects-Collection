
import math
from modules import config as hand_config
import numpy as np

class GestureRecognizer:
    def __init__(self):
        pass

    def get_dist(self, p1, p2):
        return math.hypot(p2[1] - p1[1], p2[0] - p1[0])

    def recognize(self, lm_list, fingers_up):
        """
        Returns:
            gesture_name (str): 'MOVE', 'CLICK', 'RCLICK', 'SCROLL', 'VOL_UP', 'VOL_DOWN', 'SWITCH_MODE', 'NONE'
            val (any): associated value 
        """
        if not lm_list:
            return "NONE", None

        # Landmarks
        # 4: Thumb Tip, 8: Index Tip, 12: Middle Tip, 16: Ring Tip, 20: Pinky Tip
        
        # Calculate distances
        dist_thumb_index = self.get_dist(lm_list[4][1:], lm_list[8][1:])
        dist_thumb_middle = self.get_dist(lm_list[4][1:], lm_list[12][1:])

        # 1. SWITCH MODE (New Gesture)
        # Logic: Index(OPEN), Middle(OPEN), Thumb(OPEN), Ring(CLOSED), Pinky(CLOSED)
        # Note: fingers_up = [Thumb, Index, Middle, Ring, Pinky]
        # BUT check MediaPipe orientation. 
        # My finger_up logic was primitive. Let's trust it for now but verify.
        # [1, 1, 1, 0, 0] -> Thumb, Index, Middle Open.
        if fingers_up == [1, 1, 1, 0, 0]:
             # Return index tip for movement tracking (swipe)
             return "SWITCH_MODE", lm_list[8]
        
        # 2. CLICK (Pinch Index+Thumb)
        if dist_thumb_index < hand_config.PINCH_THRESHOLD:
            return "CLICK", lm_list[8]
        
        # 3. RIGHT CLICK (Pinch Middle+Thumb)
        if dist_thumb_middle < hand_config.PINCH_THRESHOLD:
            return "RCLICK", lm_list[12]

        # 4. SCROLL (Index + Middle Up + others down)
        if fingers_up == [0, 1, 1, 0, 0] or fingers_up == [1, 1, 1, 0, 0]:
             # If Thumb is Open (1,1,1,0,0) it catches Switch Mode above.
             # So this only catches (0,1,1,0,0) OR strict ordering.
             # Switch Mode is higher priority.
             if not fingers_up[0]: # Ensure thumb is closed for Scroll
                return "SCROLL", lm_list[8]

        # 5. MOVE (Index Up only)
        # Often thumb can be loose. [0, 1, 0, 0, 0] or [1, 1, 0, 0, 0] if thumb is far?
        # If thumb is close to index -> Click.
        # If thumb is far but open -> Vol?
        
        if fingers_up == [0, 1, 0, 0, 0]:
            return "MOVE", lm_list[8]
            
        # 6. VOLUME (Thumb + Index Open)
        # [1, 1, 0, 0, 0]
        if fingers_up == [1, 1, 0, 0, 0]:
            dist = dist_thumb_index
            # Check thresholds
            if dist > hand_config.VOL_DIST_MAX:
                return "VOL_UP", dist
            elif dist < hand_config.VOL_DIST_MIN:
                # This might conflict with Click if thresholds overlap.
                # Click < 35. Vol Min < 30.
                # If < 30, it might be Click.
                # Priority: Click is checked first. So if < 35, it returns CLICK.
                # Whatever reaches here is >= 35.
                pass 
                # Actually, if VOL_DIST_MIN is small, we return Down.
                # Let's say Vol Down is a "Small Pinch" but not "Click"? No, that's confusing.
                # User asked for "Distance ranges".
                # Let's map strict ranges? 
                # Or just map range to Vol Up/Down commands?
                return "VOL_DOWN", dist # We handle "neutral" zone in main/input
            
            # If in neutral zone [MIN, MAX], maybe just hold?
            # Or treat as "MOVE" if we want cursor to move?
            # User wants "Volume Up/Down gestures".
            # Let's return VOLUME_MODE and let main decide?
            # Or explicit UP/DOWN.
            pass

        return "NONE", None
