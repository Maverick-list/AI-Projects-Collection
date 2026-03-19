import cv2
import mediapipe as mp
import time
import os
import numpy as np
import pyautogui
from system_actions_mac import move_cursor, click, scroll, set_volume_relative, take_screenshot, open_app
from eye_control import EyeController
from hand_control import HandController
from voice_control import VoiceController

# Constants
WEBCAM_W, WEBCAM_H = 640, 480
SCREEN_W, SCREEN_H = pyautogui.size()
GESTURE_COOLDOWN = 1.0 # Seconds between gesture actions

def main():
    # 1. Initialize Modules
    eye_ctrl = EyeController()
    hand_ctrl = HandController()
    voice_ctrl = VoiceController()
    
    # Start Voice Listening in background
    voice_ctrl.start_background_listening()
    
    # 2. Setup Webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_H)
    
    prev_time = 0
    fps = 0
    last_gesture_time = 0
    
    print("Combined AI Assistant Started!")
    print("Eye Control: Active")
    print("Voice Listener: Active (Say 'Hi my assistant' -> 'Open the app')")
    print("Press 'q' or ESC to quit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame = cv2.flip(frame, 1)
        
        # 3. Eye Control Pipeline
        timestamp_ms = int(time.time() * 1000)
        eye_result = eye_ctrl.process_frame(frame, timestamp_ms) # Now takes timestamp
        sx, sy, is_blink = eye_ctrl.get_eye_state(eye_result, SCREEN_W, SCREEN_H)
        
        if sx is not None:
            # We don't move cursor if hand is active to prevent conflicts? 
            # Or just move normally.
            move_cursor(sx, sy)
            if is_blink:
                click()
                cv2.putText(frame, "CLICK!", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

        # 4. Hand Control Pipeline
        hand_result = hand_ctrl.process_frame(frame, timestamp_ms)
        if hand_result.hand_landmarks:
            for hand_landmarks in hand_result.hand_landmarks:
                hand_ctrl.draw_landmarks(frame, hand_landmarks)
                gesture = hand_ctrl.get_gesture(hand_landmarks)
                
                if gesture and (time.time() - last_gesture_time > GESTURE_COOLDOWN):
                    print(f"Detected Gesture: {gesture}")
                    
                    if gesture == "VOLUME_UP":
                        set_volume_relative(10)
                    elif gesture == "VOLUME_DOWN":
                        set_volume_relative(-10)
                    elif gesture == "SCROLL":
                        # Simplistic: scroll based on hand position or fixed? 
                        # Let's say index finger higher than middle = scroll up
                        wrist = hand_landmarks.landmark[0]
                        if wrist.y < 0.5: scroll('up')
                        else: scroll('down')
                    elif gesture == "SCREENSHOT":
                        take_screenshot()
                    elif gesture == "CONFIRM":
                        # Check Voice State
                        if voice_ctrl.command_ready:
                            print("Voice Trigger + Gesture CONFIRMED! Launching Safari...")
                            open_app("Safari")
                            voice_ctrl.reset_state()
                        else:
                            cv2.putText(frame, "WAITING FOR VOICE COMMAND", (100, 300), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    last_gesture_time = time.time()
                    cv2.putText(frame, f"ACT: {gesture}", (WEBCAM_W - 200, 50), 
                                cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)

        # 5. UI and Status
        if voice_ctrl.wake_detected:
            status_color = (0, 255, 0) if voice_ctrl.command_ready else (0, 255, 255)
            msg = "VOICE: Command Ready" if voice_ctrl.command_ready else "VOICE: Listening for Command..."
            cv2.putText(frame, msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        # FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time
        cv2.putText(frame, f"FPS: {int(fps)}", (10, WEBCAM_H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow('Combined AI Assistant (Eye + Hand + Voice)', frame)
        
        if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
            break

    voice_ctrl.stop_listening = True
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
