"""
Shared utility functions
"""

import numpy as np
import pyautogui


def calculate_distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points"""
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_ear(eye_points):
    """
    Calculate Eye Aspect Ratio for blink detection
    eye_points: numpy array of shape (6, 2) with eye landmark coordinates
    """
    # Vertical distances
    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])
    
    # Horizontal distance
    C = np.linalg.norm(eye_points[0] - eye_points[3])
    
    # EAR formula
    ear = (A + B) / (2.0 * C)
    return ear


def normalize_to_screen(normalized_coords, screen_w, screen_h):
    """
    Convert normalized coordinates (0-1) to screen coordinates
    """
    x, y = normalized_coords
    sx = int(np.clip(x * screen_w, 0, screen_w - 1))
    sy = int(np.clip(y * screen_h, 0, screen_h - 1))
    return sx, sy


class MouseSmoother:
    """Moving average smoother for mouse coordinates"""
    
    def __init__(self, buffer_size=5):
        self.buffer_size = buffer_size
        self.x_buffer = []
        self.y_buffer = []
    
    def smooth(self, x, y):
        """Smooth coordinates using moving average"""
        self.x_buffer.append(x)
        self.y_buffer.append(y)
        
        # Keep buffer at max size
        if len(self.x_buffer) > self.buffer_size:
            self.x_buffer.pop(0)
            self.y_buffer.pop(0)
        
        # Calculate average
        smooth_x = sum(self.x_buffer) / len(self.x_buffer)
        smooth_y = sum(self.y_buffer) / len(self.y_buffer)
        
        return smooth_x, smooth_y
    
    def reset(self):
        """Reset buffer"""
        self.x_buffer = []
        self.y_buffer = []


class ExponentialSmoother:
    """Exponential smoothing for more responsive control"""
    
    def __init__(self, alpha=0.7):
        self.alpha = alpha  # Smoothing factor (0-1, higher = less smoothing)
        self.prev_x = None
        self.prev_y = None
    
    def smooth(self, x, y):
        """Smooth coordinates using exponential smoothing"""
        if self.prev_x is None:
            self.prev_x = x
            self.prev_y = y
            return x, y
        
        smooth_x = self.alpha * x + (1 - self.alpha) * self.prev_x
        smooth_y = self.alpha * y + (1 - self.alpha) * self.prev_y
        
        self.prev_x = smooth_x
        self.prev_y = smooth_y
        
        return smooth_x, smooth_y
    
    def reset(self):
        """Reset smoother"""
        self.prev_x = None
        self.prev_y = None


def get_screen_size():
    """Get screen dimensions"""
    return pyautogui.size()


def is_point_in_rect(point, rect):
    """
    Check if point is inside rectangle
    point: (x, y)
    rect: (x, y, width, height)
    """
    px, py = point
    rx, ry, rw, rh = rect
    return rx <= px <= rx + rw and ry <= py <= ry + rh
