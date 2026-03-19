import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import os
import numpy as np
import requests
from gestures import GestureDetector
from speech import SpeechManager
from record_manager import RecordManager, GestureLearner
from web_exporter import WebExporter
from tutorial import TutorialManager

# Constants
MODEL_PATH = "hand_landmarker.task"
STABILITY_THRESHOLD = 15
TUTORIAL_HOLD_TIME = 3.0 # Seconds to hold for practice/tutorial
COOLDOWN_PERIOD = 3.0
WEBCAM_W, WEBCAM_H = 640, 480
SIDEBAR_W = 320
TOTAL_W = WEBCAM_W + SIDEBAR_W

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading Hand Landmarker model...")
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        r = requests.get(url)
        with open(MODEL_PATH, "wb") as f:
            f.write(r.content)
        print("Model downloaded.")

def main():
    download_model()
    
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        running_mode=vision.RunningMode.VIDEO)
    detector_mp = vision.HandLandmarker.create_from_options(options)
    
    gesture_classifier = GestureDetector()
    speech_mgr = SpeechManager()
    recorder = RecordManager()
    learner = GestureLearner()
    exporter = WebExporter()
    tutorial = TutorialManager()
    
    current_gestures = [None, None]
    consecutive_frames = [0, 0]
    history = []
    tts_speed = 1.0
    learn_mode = False
    tutorial_mode = False
    practice_mode = False
    
    # Tutorial State
    tutorial_timer = 0
    tutorial_active = False
    
    # Jokowi State
    jokowi_anim_frames = 0
    force_jokowi = False
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_H)
    
    print("Sign Language Translator Pro Started.")
    print("Welcome! Press SPACE to start Tutorial Mode.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(time.time() * 1000)
        
        detection_result = detector_mp.detect_for_video(mp_image, timestamp_ms)
        
        canvas = np.zeros((WEBCAM_H, TOTAL_W, 3), dtype=np.uint8)
        canvas[:, :WEBCAM_W] = frame
        
        detected_per_frame = []
        target_gesture = None
        if tutorial_mode or practice_mode:
            lesson = tutorial.get_current_lesson()
            if lesson: target_gesture = lesson[0]

        if detection_result.hand_landmarks:
            for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
                for landmark in hand_landmarks:
                    cx, cy = int(landmark.x * WEBCAM_W), int(landmark.y * WEBCAM_H)
                    cv2.circle(canvas, (cx, cy), 3, (0, 255, 0), -1)

                gesture, conf = gesture_classifier.detect_gesture(hand_landmarks)
                detected_per_frame.append(gesture)
                
                if i < len(current_gestures):
                    if gesture == current_gestures[i]:
                        consecutive_frames[i] += 1
                    else:
                        current_gestures[i] = gesture
                        consecutive_frames[i] = 1
                
                # Tutorial Logic
                if (tutorial_mode or practice_mode) and gesture == target_gesture:
                    if tutorial_timer == 0: tutorial_timer = time.time()
                    elapsed = time.time() - tutorial_timer
                    
                    # Visual Progress for Tutorial
                    cv2.putText(canvas, f"HOLD: {elapsed:.1f}s / {TUTORIAL_HOLD_TIME}s", (50, 450), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
                    if elapsed >= TUTORIAL_HOLD_TIME:
                        praise = "Bagus!" if tutorial.language == 'id' else "Perfect!"
                        speech_mgr.speak(praise)
                        tutorial.next_lesson()
                        tutorial_timer = 0
                elif (tutorial_mode or practice_mode):
                    tutorial_timer = 0

                # Normal Triggering (if not in tutorial or different gesture)
                if not tutorial_mode and gesture and consecutive_frames[i] >= STABILITY_THRESHOLD:
                    phrase = gesture
                    if len(detected_per_frame) == 2:
                        combo = gesture_classifier.detect_combo(detected_per_frame)
                        if combo: phrase = combo
                    
                    if not history or history[-1][0] != phrase:
                        # Special JOKOWI effect
                        if phrase == "Hidup Jokowiiie!":
                            jokowi_anim_frames = 45 # Show longer for the meme
                            # Play special meme audio instead of TTS
                            success = speech_mgr.play_jokowi_meme()
                            if not success:
                                # Overlay warning handled in animation loop
                                pass
                        else:
                            speech_mgr.speak(phrase)
                        
                        history.append((phrase, time.strftime("%H:%M:%S")))
                        if len(history) > 10: history.pop(0)
                        recorder.add_subtitle(phrase)
                    consecutive_frames[i] = 0

        # NEW: Force Jokowi Demo
        if force_jokowi:
            phrase = "Hidup Jokowiiie!"
            speech_mgr.play_jokowi_meme()
            history.append((phrase, time.strftime("%H:%M:%S")))
            jokowi_anim_frames = 45
            force_jokowi = False

        # JOKOWI ANIMATION (Red Starburst)
        if jokowi_anim_frames > 0:
            cx, cy = WEBCAM_W // 2, WEBCAM_H // 2
            # Draw a complex starburst
            for angle in range(0, 360, 10):
                rad = np.radians(angle)
                length = 150 + (jokowi_anim_frames * 5)
                ex, ey = int(cx + length * np.cos(rad)), int(cy + length * np.sin(rad))
                cv2.line(canvas, (cx, cy), (ex, ey), (0, 0, 255), 5)
            
            cv2.putText(canvas, "HIDUP JOKOWIIIE!", (cx - 250, cy), cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 255, 255), 5)
            
            # Warning if file missing
            asset_path = os.path.join("SignLanguage_Speech_Translator", "assets", "hidup_jokowiiie.mp3")
            if not os.path.exists(asset_path) and not os.path.exists(os.path.join("assets", "hidup_jokowiiie.mp3")):
                cv2.putText(canvas, "File audio Jokowi tidak ditemukan", (WEBCAM_W//2 - 150, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            jokowi_anim_frames -= 1

        # UI Overlays
        if tutorial_mode:
            cv2.rectangle(canvas, (0, 0), (WEBCAM_W, 100), (50, 0, 0), -1)
            inst = tutorial.get_instruction()
            cv2.putText(canvas, f"TUTORIAL: {inst}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            prog = f"Progress: {tutorial.current_lesson_idx + 1}/{len(tutorial.gestures)}"
            cv2.putText(canvas, prog, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
            
            # Show Template in sidebar
            asset_path = f"assets/gestures/gesture_{tutorial.current_lesson_idx + 1}.png"
            if os.path.exists(asset_path):
                template = cv2.imread(asset_path)
                canvas[WEBCAM_H-170:WEBCAM_H-20, WEBCAM_W+SIDEBAR_W-170:WEBCAM_W+SIDEBAR_W-20] = template

        if learn_mode:
            cv2.rectangle(canvas, (0, 0), (WEBCAM_W, 40), (0, 165, 255), -1)
            cv2.putText(canvas, "LEARNING MODE: Press 'n' to save", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if recorder.is_recording:
            cv2.circle(canvas, (30, 30), 10, (0, 0, 255), -1)
            cv2.putText(canvas, "REC", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            recorder.add_frame(frame)

        # Sidebar History
        cv2.putText(canvas, "HISTORY / LOG", (WEBCAM_W + 20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        for idx, (item, tm) in enumerate(reversed(history)):
            y_pos = 65 + (idx * 30)
            if y_pos > WEBCAM_H - 180: break
            cv2.putText(canvas, f"{tm}: {item[:20]}", (WEBCAM_W + 20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Bottom UI Help
        cv2.rectangle(canvas, (WEBCAM_W, WEBCAM_H - 120), (TOTAL_W, WEBCAM_H), (30, 30, 30), -1)
        info_text = [
            f"Lang: {tutorial.language.upper()} | Speed: {tts_speed}x",
            "SPACE: Tut | T: Toggle | L: Lang",
            "R: Rec | E: Exp | Q: Quit"
        ]
        for idx, txt in enumerate(info_text):
            cv2.putText(canvas, txt, (WEBCAM_W + 20, WEBCAM_H - 90 + (idx * 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        cv2.imshow('SignLanguage Speech Translator PRO', canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == ord(' '): 
            tutorial_mode = True
            tutorial_timer = 0
            if not tutorial_active:
                welcome = "Selamat datang! Mari belajar. Tekan spasi untuk mulai." if tutorial.language == 'id' else "Welcome! Let's learn. Press space to start."
                speech_mgr.speak(welcome)
                tutorial_active = True
        elif key == ord('t'): 
            tutorial_mode = not tutorial_mode
            if tutorial_mode: tutorial_timer = 0
        elif key == ord('l'): tutorial.toggle_language()
        elif key == ord('p'): practice_mode = not practice_mode
        elif key == ord('r'):
            if recorder.is_recording: recorder.stop_recording()
            else: recorder.start_recording(WEBCAM_W, WEBCAM_H)
        elif key == ord('e'): exporter.export()
        elif key == ord('j'): force_jokowi = True
        elif key == ord('s'):
            cv2.imwrite(f"dashboard_{int(time.time())}.png", canvas)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
