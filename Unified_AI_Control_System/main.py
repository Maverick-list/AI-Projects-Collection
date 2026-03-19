"""
Unified AI Control System
Main application that orchestrates all control modules
"""

import cv2
import time
import numpy as np
from shared.camera_manager import CameraManager
from shared.model_manager import ModelManager
from modules.eye_tracking import EyeTrackingModule
from modules.hand_gesture import HandGestureModule
from modules.sign_language import SignLanguageModule
from modules.virtual_keyboard import VirtualKeyboardModule
import config


class UnifiedAIControlSystem:
    """Main application orchestrator"""
    
    def __init__(self):
        self.camera = CameraManager(config.CAM_WIDTH, config.CAM_HEIGHT, config.CAM_FPS)
        self.model_manager = ModelManager()
        
        # Initialize modules
        self.modules = {}
        self.active_modules = []
        
        # Performance tracking
        self.fps = 0
        self.prev_time = 0
        
        # UI state
        self.show_menu = False
        
    def initialize(self):
        """Initialize system and modules"""
        print("=" * 60)
        print("UNIFIED AI CONTROL SYSTEM")
        print("=" * 60)
        
        # Start camera
        if not self.camera.start():
            print("ERROR: Failed to start camera!")
            return False
        
        # Initialize selected modules based on config
        print("\nInitializing modules...")
        
        if config.ENABLE_EYE_TRACKING:
            eye_module = EyeTrackingModule()
            if eye_module.initialize():
                self.modules['eye'] = eye_module
        
        if config.ENABLE_HAND_GESTURE:
            hand_module = HandGestureModule()
            if hand_module.initialize():
                self.modules['hand'] = hand_module
        
        if config.ENABLE_SIGN_LANGUAGE:
            sign_module = SignLanguageModule()
            if sign_module.initialize():
                self.modules['sign'] = sign_module
        
        if config.ENABLE_VIRTUAL_KEYBOARD:
            kbd_module = VirtualKeyboardModule()
            if kbd_module.initialize():
                self.modules['keyboard'] = kbd_module
        
        # Set initially active modules (only one by default to reduce load)
        if 'hand' in self.modules:
            self.active_modules.append('hand')
        
        print(f"\nInitialized {len(self.modules)} modules")
        print(f"Active modules: {', '.join(self.active_modules)}")
        
        return True
    
    def process_frame(self):
        """Process a single frame through active modules"""
        success, frame = self.camera.read_frame()
        if not success:
            return None
        
        # Flip for mirror view
        frame = cv2.flip(frame, 1)
        
        # Process through each active module
        all_events = {}
        
        for module_key in self.active_modules:
            if module_key in self.modules:
                module = self.modules[module_key]
                frame, events = module.process_frame(frame)
                all_events[module_key] = events
        
        # Draw UI overlay
        frame = self.draw_ui(frame, all_events)
        
        return frame
    
    def draw_ui(self, frame, events):
        """Draw unified UI overlay"""
        h, w, _ = frame.shape
        
        # Status bar background
        cv2.rectangle(frame, (0, 0), (w, config.UI_STATUS_BAR_HEIGHT), 
                     (40, 40, 40), -1)
        
        # Title
        cv2.putText(frame, "UNIFIED AI CONTROL", (10, 30), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        
        # FPS
        curr_time = time.time()
        if self.prev_time != 0:
            self.fps = config.FPS_SMOOTHING * self.fps + \
                      (1 - config.FPS_SMOOTHING) * (1 / (curr_time - self.prev_time))
        self.prev_time = curr_time
        
        cv2.putText(frame, f"FPS: {int(self.fps)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Active modules indicator
        module_status = []
        colors = {
            'eye': (147, 20, 255),    # Purple
            'hand': (0, 255, 0),      # Green
            'sign': (255, 255, 0),    # Cyan
            'keyboard': (0, 165, 255) # Orange
        }
        
        names = {
            'eye': 'EYE',
            'hand': 'HAND',
            'sign': 'SIGN',
            'keyboard': 'KBRD'
        }
        
        x_offset = w - 300
        for module_key in self.active_modules:
            if module_key in self.modules:
                color = colors.get(module_key, (255, 255, 255))
                name = names.get(module_key, module_key.upper())
                cv2.putText(frame, name, (x_offset, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                x_offset += 70
        
        # Controls help
        cv2.putText(frame, "M:Menu Q:Quit 1-4:Mode A:Toggle", (10, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Menu overlay
        if self.show_menu:
            frame = self.draw_menu(frame)
        
        return frame
    
    def draw_menu(self, frame):
        """Draw mode selection menu"""
        h, w, _ = frame.shape
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (w//4, h//4), (3*w//4, 3*h//4), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        menu_x = w//4 + 20
        menu_y = h//4 + 40
        
        cv2.putText(frame, "MODE SELECTION", (menu_x, menu_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 2)
        
        options = [
            ("1: Eye Tracking", 'eye'),
            ("2: Hand Gesture", 'hand'),
            ("3: Sign Language", 'sign'),
            ("4: Virtual Keyboard", 'keyboard'),
            ("", None),
            ("M: Close Menu", None),
            ("Q: Quit Program", None)
        ]
        
        for i, (text, key) in enumerate(options):
            y = menu_y + 50 + (i * 35)
            color = (0, 255, 0) if key and key in self.active_modules else (200, 200, 200)
            cv2.putText(frame, text, (menu_x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return frame
    
    def toggle_module(self, module_key):
        """Toggle a module on/off"""
        if module_key in self.modules:
            if module_key in self.active_modules:
                self.active_modules.remove(module_key)
                print(f"Disabled: {module_key}")
            else:
                self.active_modules.append(module_key)
                print(f"Enabled: {module_key}")
    
    def handle_key_input(self, key):
        """Handle keyboard input"""
        if key == ord(config.KEY_QUIT):
            return False  # Quit
        
        elif key == ord(config.KEY_MENU):
            self.show_menu = not self.show_menu
        
        elif key == ord(config.KEY_EYE_TRACKING):
            self.toggle_module('eye')
        
        elif key == ord(config.KEY_HAND_GESTURE):
            self.toggle_module('hand')
        
        elif key == ord(config.KEY_SIGN_LANGUAGE):
            self.toggle_module('sign')
        
        elif key == ord(config.KEY_VIRTUAL_KEYBOARD):
            self.toggle_module('keyboard')
        
        elif key == ord(config.KEY_TOGGLE_ACTIVE):
            # Toggle active state for hand gesture module
            if 'hand' in self.modules:
                self.modules['hand'].toggle_active()
        
        return True  # Continue running
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            print("Failed to initialize system!")
            return
        
        print("\n" + "=" * 60)
        print("CONTROLS:")
        print("  1-4: Toggle Eye/Hand/Sign/Keyboard modes")
        print("  M: Show/hide menu")
        print("  A: Toggle hand gesture active/inactive")
        print("  Q: Quit")
        print("=" * 60)
        print("\nStarting main loop...\n")
        
        try:
            while True:
                frame = self.process_frame()
                if frame is None:
                    break
                
                cv2.imshow('Unified AI Control System', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key != 255:  # Key pressed
                    if not self.handle_key_input(key):
                        break
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup all resources"""
        print("\nCleaning up...")
        
        for module in self.modules.values():
            module.cleanup()
        
        self.camera.release()
        cv2.destroyAllWindows()
        
        print("Goodbye!")


def main():
    """Entry point"""
    app = UnifiedAIControlSystem()
    app.run()


if __name__ == "__main__":
    main()
