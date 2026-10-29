import json
import os
import cv2
import numpy as np

class TutorialManager:
    def __init__(self, progress_file="user_progress.json"):
        self.progress_file = progress_file
        self.current_lesson_idx = 0
        self.language = 'id' # 'id' or 'en'
        self.gestures = [
            ("Halo, assalamualaikum", "Buka tangan (5 jari)", "Open hand (5 fingers)"),
            ("Bye-bye, assalamualaikum", "Lambaikan tangan miring", "Sideway wave"),
            ("Aku", "Tangan di dada", "Hand to chest"),
            ("Firza", "Simbol OK (Ibu jari + Telunjuk)", "OK sign (Thumb + Index)"),
            ("Nice to meet you", "Telapak ke kamera (Tegak)", "Palm to camera (Upright)"),
            ("Listen", "Tangan ke telinga", "Hand to ear"),
            ("Look", "Tangan ke mata", "Hand to eye"),
            ("Eat", "Tangan ke mulut", "Hand to mouth"),
            ("No", "Kepalan tangan", "Fist"),
            ("Four", "4 jari terbuka", "4 fingers open"),
            ("Good", "Jempol ke atas", "Thumb up"),
            ("Bad", "Jempol ke bawah", "Thumb down"),
            ("Stop", "Telapak ke arah bawah", "Palm facing down"),
            ("Yes", "Telunjuk ke atas", "Index finger up"),
            ("Peace", "2 jari (V)", "Peace sign (V)"),
            ("Three", "3 jari terbuka", "3 fingers open"),
            ("Great to see you, assalamualaikum!", "Halo + Thumbs up", "Hello + Thumbs up (Combo)"),
            ("Hidup Jokowiiie!", "Tangan mengepal ke atas", "Fist upwards")
        ]
        self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                self.current_lesson_idx = data.get("last_lesson", 0)
        else:
            self.current_lesson_idx = 0

    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump({"last_lesson": self.current_lesson_idx}, f)

    def get_current_lesson(self):
        if self.current_lesson_idx < len(self.gestures):
            return self.gestures[self.current_lesson_idx]
        return None

    def next_lesson(self):
        if self.current_lesson_idx < len(self.gestures) - 1:
            self.current_lesson_idx += 1
            self.save_progress()
            return True
        return False

    def toggle_language(self):
        self.language = 'en' if self.language == 'id' else 'id'
        return self.language

    def get_instruction(self):
        lesson = self.get_current_lesson()
        if not lesson: return ""
        idx = 1 if self.language == 'id' else 2
        return f"{lesson[0]}: {lesson[idx]}"

def generate_assets(output_dir="assets/gestures"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate simple placeholder templates (colored rectangles with labels)
    for i in range(1, 21):
        img = np.zeros((150, 150, 3), dtype=np.uint8)
        cv2.rectangle(img, (10, 10), (140, 140), (255, 165, 0), 2)
        cv2.putText(img, f"G{i}", (45, 90), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)
        cv2.imwrite(os.path.join(output_dir, f"gesture_{i}.png"), img)
    print("Programmatic assets generated.")

if __name__ == "__main__":
    generate_assets()
