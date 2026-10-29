import cv2
import os
import config

class FaceRecognitionModule:
    """Module for Face Recognition using Haar Cascades"""
    
    def __init__(self):
        self.face_cascade = None
        
    def initialize(self):
        """Initialize the face recognition cascade classifier"""
        model_path = os.path.join(os.path.dirname(__file__), '..', config.FACE_CASCADE_PATH)
        
        if not os.path.exists(model_path):
            print(f"ERROR: Face cascade model not found at {model_path}")
            return False
            
        self.face_cascade = cv2.CascadeClassifier(model_path)
        print("Face Recognition module initialized successfully")
        return True
        
    def process_frame(self, frame):
        """Process frame for face recognition"""
        if self.face_cascade is None:
            return frame, {}
            
        # Convert to grayscale for Haar cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), config.COLOR_FACE_RECOGNITION, 2)
            cv2.putText(frame, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, config.COLOR_FACE_RECOGNITION, 2)
            
        events = {'faces_detected': len(faces)}
        return frame, events
        
    def cleanup(self):
        """Cleanup resources"""
        self.face_cascade = None
        
    def toggle_active(self):
        """Toggle any active internal states if necessary"""
        pass
