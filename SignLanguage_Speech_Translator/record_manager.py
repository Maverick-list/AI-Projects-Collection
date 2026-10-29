import cv2
import time
import os

class RecordManager:
    def __init__(self, output_dir="recordings"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.is_recording = False
        self.out = None
        self.start_time = 0
        self.subtitles = []
        
    def start_recording(self, w, h, fps=20):
        filename = f"gesture_session_{int(time.time())}.mp4"
        path = os.path.join(self.output_dir, filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(path, fourcc, fps, (w, h))
        self.is_recording = True
        self.start_time = time.time()
        self.subtitles = []
        print(f"Recording started: {filename}")
        return path

    def stop_recording(self):
        if self.out:
            self.out.release()
            self.is_recording = False
            # Save subtitles (SRT format simplified)
            self._save_subtitles()
            print("Recording stopped.")

    def add_frame(self, frame):
        if self.is_recording and self.out:
            self.out.write(frame)

    def add_subtitle(self, text):
        if self.is_recording:
            elapsed = time.time() - self.start_time
            self.subtitles.append((elapsed, text))

    def _save_subtitles(self):
        if not self.subtitles: return
        sub_path = os.path.join(self.output_dir, f"session_{int(self.start_time)}.srt")
        with open(sub_path, "w") as f:
            for i, (ts, text) in enumerate(self.subtitles):
                f.write(f"{i+1}\n00:00:{int(ts):02d},000 --> 00:00:{int(ts)+1:02d},000\n{text}\n\n")

class GestureLearner:
    def __init__(self, filepath="new_gestures.json"):
        self.filepath = filepath
        self.custom_gestures = {}
        
    def save_gesture(self, name, landmarks):
        # Store simplified landmark data
        self.custom_gestures[name] = [[l.x, l.y, l.z] for l in landmarks]
        import json
        with open(self.filepath, "w") as f:
            json.dump(self.custom_gestures, f)
        print(f"Gesture '{name}' learned.")
