
import pyautogui
import platform
import subprocess
import time
from utils import MovingAverageSmoother, apply_deadzone, map_range
import config

class InputController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.smoother = MovingAverageSmoother(window_size=config.SMOOTHING_WINDOW)
        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT
        self.os_type = platform.system()
        
        self.prev_x_mapped = 0
        self.prev_y_mapped = 0
        
        self.last_vol_time = 0

    def move_mouse(self, x, y):
        # x, y are raw coordinates from the camera frame
        
        # 1. Map to Screen Coordinates
        # Direct mapping (Hand Right -> Screen Right)
        x_mapped = map_range(x, config.FRAME_MARGIN_X, config.CAM_WIDTH - config.FRAME_MARGIN_X, 
                             0, self.screen_width)
        y_mapped = map_range(y, config.FRAME_MARGIN_Y, config.CAM_HEIGHT - config.FRAME_MARGIN_Y, 
                             0, self.screen_height)
        
        # Clamp
        x_mapped = max(0, min(self.screen_width, x_mapped))
        y_mapped = max(0, min(self.screen_height, y_mapped))
        
        # 2. Deadzone Check
        dx = x_mapped - self.prev_x_mapped
        dy = y_mapped - self.prev_y_mapped
        
        dx, dy = apply_deadzone(dx, dy, config.DEADZONE)
        
        if dx == 0 and dy == 0:
            return # No significant movement
            
        target_x = self.prev_x_mapped + dx
        target_y = self.prev_y_mapped + dy
        
        self.prev_x_mapped = target_x
        self.prev_y_mapped = target_y

        # 3. Smooth
        smooth_x, smooth_y = self.smoother.get_smoothed_coords(target_x, target_y)
        
        # 4. Move
        # Note: pyautogui duration=0 is instant. We rely on our loop rate for smooth updates.
        pyautogui.moveTo(smooth_x, smooth_y)

    def click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.click(button='right')

    def scroll(self, dy):
        # dy is normalized or pixel change. Pyautogui scroll is platform dependent.
        # For Mac, scroll is sensitive.
        pyautogui.scroll(int(dy * 5)) 

    def volume_up(self):
        if time.time() - self.last_vol_time < 0.2: return
        
        if self.os_type == 'Darwin':
            # AppleScript: set volume output volume (output volume of (get volume settings) + 5)
            # This is slow if we do "get volume settings".
            # Faster: "set volume output volume ((output volume of (get volume settings)) + 5)"
            # Better: use key codes for system volume keys? 
            # Key 1000? No.
            # Best reliable way is osascript small increment.
            cmd = "set volume output volume ((output volume of (get volume settings)) + 5)"
            subprocess.Popen(["osascript", "-e", cmd])
        self.last_vol_time = time.time()

    def volume_down(self):
        if time.time() - self.last_vol_time < 0.2: return

        if self.os_type == 'Darwin':
            cmd = "set volume output volume ((output volume of (get volume settings)) - 5)"
            subprocess.Popen(["osascript", "-e", cmd])
        self.last_vol_time = time.time()

    def switch_window(self, direction='right'):
        # Mac: Ctrl + Left/Right Arrow for spaces
        # Using 'command' alias might be wrong for Control key on Mac if mapped differently,
        # usually 'ctrl' is correct for standard Mission Control.
        if direction == 'right':
            pyautogui.hotkey('ctrl', 'right')
        elif direction == 'left':
            pyautogui.hotkey('ctrl', 'left')
