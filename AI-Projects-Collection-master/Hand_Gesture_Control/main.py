
import cv2
import time
import numpy as np
import config
from hand_tracking import HandTracker
from gesture_recognition import GestureRecognizer
from input_controller import InputController
from tutorial_system import TutorialManager

def main():
    # 1. Initialize Modules
    tracker = HandTracker()
    gesture_recognizer = GestureRecognizer()
    controller = InputController()
    tutorial_manager = TutorialManager() # New Tutorial Module

    # 2. Setup Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found!")
        return
        
    cap.set(3, config.CAM_WIDTH)
    cap.set(4, config.CAM_HEIGHT)
    
    # State flags
    is_active = True
    is_tutorial_mode = False
    prev_time = 0
    
    # Cooldown states
    switch_cooldown = 0
    switch_gesture_start_time = 0
    
    # Mode tracking
    current_mode_text = "NONE"

    print("Hand Gesture Control - UPGRADED")
    print("Gestures:")
    print(" - Move: Index Up")
    print(" - Click: Pinched (Thumb+Index)")
    print(" - Scroll: Index+Middle Up")
    print(" - Switch Desktop: Index+Middle+Thumb Open (Swipe Left/Right)")
    print(" - Volume: Thumb+Index Distance (Wide=Up, Narrow=Down)")
    print("Press 'q' to quit, 'a' to toggle Active/Inactive")

    while True:
        success, img = cap.read()
        if not success:
            break

        # Flip for mirror view
        img = cv2.flip(img, 1) # 1 = horizontal flip
        
        # 3. Detect Hands
        img = tracker.find_hands(img)
        lm_list = tracker.find_position(img)
        fingers_up = tracker.fingers_up(lm_list) # [Thumb, Index, Middle, Ring, Pinky]

        gesture_name = "NONE"
        val = None
        color = (255, 255, 255) # Default color

        if is_active and lm_list:
            # Recognize Gesture
            gesture_name, val = gesture_recognizer.recognize(lm_list, fingers_up)
            
            # --- ACTION HANDLER ---
            # Only execute actions if NOT in tutorial mode
            if not is_tutorial_mode:
                if gesture_name == "MOVE":
                    # val is (x, y) of index tip
                    controller.move_mouse(val[1], val[2])
                    color = config.COLOR_MOUSE
                    current_mode_text = "CURSOR"

                elif gesture_name == "CLICK":
                     # val is coords
                     controller.move_mouse(val[1], val[2]) # Keep moving while pinching
                     controller.click()
                     color = config.COLOR_CLICK
                     current_mode_text = "CLICK"
                     
                elif gesture_name == "RCLICK":
                     controller.move_mouse(val[1], val[2])
                     controller.right_click()
                     color = config.COLOR_CLICK
                     current_mode_text = "RIGHT CLICK"

                elif gesture_name == "SCROLL":
                    # val is (x, y)
                    if val[2] < config.CAM_HEIGHT / 2 - 50:
                        controller.scroll(10) # UP
                        current_mode_text = "SCROLL UP"
                    elif val[2] > config.CAM_HEIGHT / 2 + 50:
                        controller.scroll(-10) # DOWN
                        current_mode_text = "SCROLL DOWN"
                    
                    color = config.COLOR_SCROLL
                
                elif gesture_name == "SWITCH_MODE":
                    if time.time() - switch_cooldown > 1.0: # 1s cooldown
                        if val[1] > config.CAM_WIDTH - 150: # Right Edge
                            controller.switch_window('right')
                            switch_cooldown = time.time()
                            current_mode_text = "NEXT DESKTOP"
                        elif val[1] < 150: # Left Edge
                            controller.switch_window('left')
                            switch_cooldown = time.time()
                            current_mode_text = "PREV DESKTOP"
                        else:
                            current_mode_text = "SWITCH READY"
                    else:
                        current_mode_text = "SWITCH COOLDOWN"
                    
                    color = config.COLOR_SWITCH

                elif gesture_name == "VOL_UP":
                    # val is distance, but we just trigger UP command
                    controller.volume_up()
                    current_mode_text = "VOL UP"
                    color = config.COLOR_VOL

                elif gesture_name == "VOL_DOWN":
                    controller.volume_down()
                    current_mode_text = "VOL DOWN"
                    color = config.COLOR_VOL

                else:
                    current_mode_text = "NEUTRAL"
            else:
                 current_mode_text = "TUTORIAL MODE"
        
        else:
             current_mode_text = "INACTIVE (Press 'a')"

        # --- TUTORIAL MODE OVERRIDE ---
        if is_tutorial_mode:
             # In tutorial, we DON'T execute actions (unless it's part of the test?)
             # Let's disable mouse control actions to avoid chaos
             # But we need to update the tutorial manager
             # We pass the gesture_name detected 
             
             # Map internal names to Manager expected names if needed
             # Manager expects: MOVE, CLICK, RCLICK, SCROLL, VOL_UP, VOL_DOWN, SWITCH_MODE
             # gesture_name matches these.
             # Special case for SWITCH desktop: gesture is 'SWITCH_MODE', 
             # but action is 'NEXT/PREV'. Manager accepts 'SWITCH_MODE' or text.
             
             tutorial_manager.update(gesture_name)
             if current_mode_text in ["NEXT DESKTOP", "PREV DESKTOP"]:
                 tutorial_manager.update(current_mode_text) # Allow these too

             img = tutorial_manager.draw_overlay(img)
             
             # Show safe mode indicator
             cv2.putText(img, "** SAFEMODE (NO CLICKS) **", (300, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)

        # 4. Draw HUD
        # ROI Box
        cv2.rectangle(img, (config.FRAME_MARGIN_X, config.FRAME_MARGIN_Y), 
                      (config.CAM_WIDTH - config.FRAME_MARGIN_X, config.CAM_HEIGHT - config.FRAME_MARGIN_Y),
                      (255, 0, 255), 2)
        
        # FPS
        cTime = time.time()
        fps = 1 / (cTime - prev_time) if (cTime - prev_time) > 0 else 0
        prev_time = cTime
        
        cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(img, f"Mode: {current_mode_text}", (20, 90), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

        cv2.imshow("Hand Gesture Control", img)
        
        # Key Handling
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord('a'):
            is_active = not is_active
        if key == ord('t'):
            is_tutorial_mode = not is_tutorial_mode
            if is_tutorial_mode:
                tutorial_manager.reset()
                is_active = True # Force active for tutorial

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# --- SUMMARY OF UPGRADE ---
# 1. Cursor Smoothing: Implemented MovingAverageSmoother (window=7) + Deadzone (5px).
# 2. Window Switching: 
#    - Gesture: Index + Middle + Thumb OPEN (Ring+Pinky Closed).
#    - Trigger: Move hand to Left edge (<150px) or Right edge (>Width-150px).
#    - Keys: ctrl+left, ctrl+right (MacOS Spaces).
# 3. Volume:
#    - Gesture: Thumb+Index Distance. Wide (>140px) = Up, Narrow (<30px) = Down.
#    - Action: AppleScript `set volume` relative change (+/- 5).
