import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import requests
from utils import calculate_ear, MouseSmoother, normalize_to_screen

class EyeController:
    def __init__(self, model_path="face_landmarker.task"):
        self.model_path = model_path
        self._download_model()
        
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1,
            running_mode=vision.RunningMode.VIDEO)
        self.detector = vision.FaceLandmarker.create_from_options(options)
        
        self.smoother = MouseSmoother(buffer_size=5)
        
        # Landmark Indices
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.PUPIL_R_INDEX = 468
        
        # Constants
        self.EAR_THRESHOLD = 0.25
        self.MOVE_GAIN = 2.0

    def _download_model(self):
        if not os.path.exists(self.model_path):
            print("Downloading Face Landmarker model...")
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            r = requests.get(url)
            with open(self.model_path, "wb") as f:
                f.write(r.content)
            print("Model downloaded.")

    def process_frame(self, frame, timestamp_ms):
        """Processes frame for face landmarks in video mode."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.detector.detect_for_video(mp_image, timestamp_ms)

    def get_eye_state(self, detection_result, screen_w, screen_h):
        """
        Calculates EAR for click and Screen coords for movement.
        Returns: (smooth_x, smooth_y, is_blink) or (None, None, False)
        """
        if not detection_result.face_landmarks:
            return None, None, False
            
        landmarks = detection_result.face_landmarks[0]
        
        # 1. Blink Detection
        left_eye_pts = np.array([
            [landmarks[i].x, landmarks[i].y] 
            for i in self.LEFT_EYE_INDICES
        ])
        ear = calculate_ear(left_eye_pts)
        is_blink = ear < self.EAR_THRESHOLD
        
        # 2. Pupil Position
        pupil = landmarks[self.PUPIL_R_INDEX]
        adj_x = 0.5 + (pupil.x - 0.5) * self.MOVE_GAIN
        adj_y = 0.5 + (pupil.y - 0.5) * self.MOVE_GAIN
        
        target_x, target_y = normalize_to_screen((adj_x, adj_y), screen_w, screen_h)
        smooth_x, smooth_y = self.smoother.smooth(target_x, target_y)
        
        return smooth_x, smooth_y, is_blink

    def get_pupil_coords(self, landmarks, w, h):
        """Utility for visualization."""
        if not landmarks: return None
        pupil = landmarks[self.PUPIL_R_INDEX]
        return int(pupil.x * w), int(pupil.y * h)
