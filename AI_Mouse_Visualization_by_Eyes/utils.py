import numpy as np

def calculate_ear(eye_landmarks):
    """
    Calculate the Eye Aspect Ratio (EAR) for blink detection.
    landmarks: a list of 6 points (top-left, top-right, bot-right, bot-left, mid-left, mid-right)
    Usually indexes for standard facial landmarks, but for FaceMesh we can pick representative ones.
    For this implementation, we take:
    P2, P6 (upper/lower), P3, P5 (upper/lower), P1, P4 (corners)
    """
    # Vertical distances
    v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    
    # Horizontal distance
    h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    
    ear = (v1 + v2) / (2.0 * h)
    return ear

def normalize_to_screen(point, screen_w, screen_h):
    """
    Normalizes a point (x, y) from 0-1 space to screen pixel coordinates.
    """
    x = np.clip(point[0], 0.01, 0.99) * screen_w
    y = np.clip(point[1], 0.01, 0.99) * screen_h
    return int(x), int(y)

class MouseSmoother:
    def __init__(self, buffer_size=5):
        self.buffer_size = buffer_size
        self.x_buffer = []
        self.y_buffer = []
        
    def smooth(self, x, y):
        self.x_buffer.append(x)
        self.y_buffer.append(y)
        
        if len(self.x_buffer) > self.buffer_size:
            self.x_buffer.pop(0)
            self.y_buffer.pop(0)
            
        return sum(self.x_buffer) / len(self.x_buffer), sum(self.y_buffer) / len(self.y_buffer)
