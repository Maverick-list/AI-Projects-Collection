import math
import time
import numpy as np
from collections import deque
import config

class MovingAverageSmoother:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.x_buffer = deque(maxlen=window_size)
        self.y_buffer = deque(maxlen=window_size)

    def get_smoothed_coords(self, x, y):
        self.x_buffer.append(x)
        self.y_buffer.append(y)
        
        avg_x = sum(self.x_buffer) / len(self.x_buffer)
        avg_y = sum(self.y_buffer) / len(self.y_buffer)
        
        return int(avg_x), int(avg_y)

def apply_deadzone(dx, dy, threshold):
    """
    Applies a deadzone to movement deltas.
    If movement is smaller than threshold, return 0,0.
    """
    if abs(dx) < threshold: dx = 0
    if abs(dy) < threshold: dy = 0
    return dx, dy

def map_range(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
