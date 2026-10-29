"""
Singleton Camera Manager
Provides a single camera instance shared across all modules
"""

import cv2
import threading
import time


class CameraManager:
    """Thread-safe singleton camera manager"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, width=640, height=480, fps=30):
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
            
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.running = False
        self._initialized = True
        
    def start(self):
        """Initialize and start camera capture"""
        if self.cap is not None:
            return True
            
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("ERROR: Could not open camera!")
            return False
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        self.running = True
        print(f"Camera started: {self.width}x{self.height} @ {self.fps}fps")
        return True
    
    def read_frame(self):
        """
        Read a frame from the camera
        Returns: (success, frame) tuple
        """
        if not self.cap or not self.running:
            return False, None
            
        with self.frame_lock:
            success, frame = self.cap.read()
            if success:
                self.current_frame = frame.copy()
                return True, frame
            return False, None
    
    def get_frame(self):
        """
        Get the most recent frame (cached)
        Useful for multiple modules accessing same frame
        Returns: frame or None
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def release(self):
        """Release camera resources"""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
            print("Camera released")
    
    def is_running(self):
        """Check if camera is running"""
        return self.running and self.cap is not None and self.cap.isOpened()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.release()
