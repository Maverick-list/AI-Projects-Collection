
import time
import cv2

class TutorialStep:
    def __init__(self, name, instruction, target_gestures, duration=2.0):
        self.name = name
        self.instruction = instruction
        self.target_gestures = target_gestures # List of acceptable gesture names
        self.duration = duration
        self.success_start_time = 0
        self.is_completed = False

    def check(self, current_gesture):
        if self.is_completed:
            return True
        
        if current_gesture in self.target_gestures:
            if self.success_start_time == 0:
                self.success_start_time = time.time()
            elif time.time() - self.success_start_time >= self.duration:
                self.is_completed = True
                return True
        else:
            self.success_start_time = 0 # Reset if gesture breaks
        
        return False

    def get_progress(self):
        if self.success_start_time == 0:
            return 0.0
        elapsed = time.time() - self.success_start_time
        return min(elapsed / self.duration, 1.0)

class TutorialManager:
    def __init__(self):
        self.steps = [
            TutorialStep("WELCOME", "Press 't' to Start/Exit. Hold 'Index Up' to begin.", ["MOVE"], duration=1.0),
            TutorialStep("MOVE CURSOR", "Hold Index Finger UP. Move hand around.", ["MOVE"], duration=3.0),
            TutorialStep("LEFT CLICK", "Pinch Thumb + Index (Touch tips).", ["CLICK"], duration=2.0),
            TutorialStep("RIGHT CLICK", "Pinch Thumb + Middle (Touch tips).", ["RCLICK"], duration=2.0),
            TutorialStep("SCROLL", "Hold Index + Middle UP. Move Hand Up/Down.", ["SCROLL"], duration=3.0),
            TutorialStep("VOLUME", "Spread Thumb + Index Wide (Up) or Close (Down).", ["VOL_UP", "VOL_DOWN"], duration=3.0),
            TutorialStep("SWITCH DESKTOP", "3 Fingers (Index+Middle+Thumb) OPEN. Hold steady.", ["SWITCH_MODE", "NEXT DESKTOP", "PREV DESKTOP"], duration=3.0),
            TutorialStep("COMPLETED", "You are ready! Press 't' to exit tutorial.", [], duration=999)
        ]
        self.current_step_index = 0

    def update(self, current_gesture):
        if self.current_step_index >= len(self.steps):
            return
        
        step = self.steps[self.current_step_index]
        if step.check(current_gesture):
            # Move to next step after brief pause/visual feedback? 
            # Logic handles completion. We can auto-advance.
            if step.name != "COMPLETED":
                 self.current_step_index += 1
                 # Reset next step's timer just in case
                 if self.current_step_index < len(self.steps):
                     self.steps[self.current_step_index].success_start_time = 0
    
    def get_current_instruction(self):
        step = self.steps[self.current_step_index]
        return step.name, step.instruction, step.get_progress()

    def reset(self):
        self.current_step_index = 0
        for step in self.steps:
            step.is_completed = False
            step.success_start_time = 0

    def draw_overlay(self, img):
        if self.current_step_index >= len(self.steps): return img
        
        step = self.steps[self.current_step_index]
        h, w, c = img.shape
        
        # Overlay Box
        cv2.rectangle(img, (50, h - 200), (w - 50, h - 50), (0, 0, 0), cv2.FILLED)
        cv2.rectangle(img, (50, h - 200), (w - 50, h - 50), (255, 255, 255), 2)
        
        # Text
        cv2.putText(img, f"TUTORIAL: {step.name}", (70, h - 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(img, step.instruction, (70, h - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Progress Bar
        progress = step.get_progress()
        bar_width = int((w - 140) * progress)
        cv2.rectangle(img, (70, h - 80), (70 + bar_width, h - 60), (0, 255, 0), cv2.FILLED)
        cv2.rectangle(img, (70, h - 80), (w - 70, h - 60), (255, 255, 255), 2)
        
        return img
