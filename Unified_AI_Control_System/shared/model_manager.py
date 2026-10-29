"""
MediaPipe Model Manager
Handles lazy loading and caching of MediaPipe models
"""

import os
import requests
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class ModelManager:
    """Singleton manager for MediaPipe models"""
    
    _instance = None
    _hand_detector = None
    _face_detector = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.hand_model_path = "models/hand_landmarker.task"
        self.face_model_path = "models/face_landmarker.task"
        self._ensure_models_exist()
    
    def _ensure_models_exist(self):
        """Download models if they don't exist"""
        os.makedirs("models", exist_ok=True)
        
        # Download hand model if needed
        if not os.path.exists(self.hand_model_path):
            print("Downloading hand landmarker model...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            self._download_file(url, self.hand_model_path)
        
        # Download face model if needed
        if not os.path.exists(self.face_model_path):
            print("Downloading face landmarker model...")
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            self._download_file(url, self.face_model_path)
    
    def _download_file(self, url, filepath):
        """Download a file from URL"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded: {filepath}")
            return True
        except Exception as e:
            print(f"Error downloading {filepath}: {e}")
            return False
    
    def get_hand_detector(self, num_hands=2, min_detection_confidence=0.7):
        """
        Get or create hand landmarker detector
        Uses caching to avoid recreating detector
        """
        if ModelManager._hand_detector is None:
            base_options = python.BaseOptions(model_asset_path=self.hand_model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=num_hands,
                min_hand_detection_confidence=min_detection_confidence,
                min_hand_presence_confidence=min_detection_confidence,
                min_tracking_confidence=min_detection_confidence
            )
            ModelManager._hand_detector = vision.HandLandmarker.create_from_options(options)
            print("Hand detector initialized")
        
        return ModelManager._hand_detector
    
    def get_face_detector(self, num_faces=1):
        """
        Get or create face landmarker detector
        Uses caching to avoid recreating detector
        """
        if ModelManager._face_detector is None:
            base_options = python.BaseOptions(model_asset_path=self.face_model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=True,
                output_facial_transformation_matrixes=True,
                num_faces=num_faces
            )
            ModelManager._face_detector = vision.FaceLandmarker.create_from_options(options)
            print("Face detector initialized")
        
        return ModelManager._face_detector
    
    @staticmethod
    def reset():
        """Reset cached detectors (useful for reconfiguration)"""
        ModelManager._hand_detector = None
        ModelManager._face_detector = None
