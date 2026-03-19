import subprocess
import os
import time
import pyautogui

def move_cursor(x, y):
    """Moves cursor using PyAutoGUI."""
    pyautogui.moveTo(x, y, _pause=False)

def click():
    """Simulates a left click."""
    pyautogui.click()

def scroll(direction):
    """
    Simulates scrolling on macOS.
    direction: 'up' or 'down'
    """
    amount = 10 if direction == 'up' else -10
    pyautogui.scroll(amount)

def set_volume_relative(delta):
    """
    On macOS, adjust volume using AppleScript.
    delta: integer (positive for up, negative for down)
    """
    script = f'set volume output volume ((output volume of (get volume settings)) + {delta})'
    subprocess.run(['osascript', '-e', script])

def take_screenshot():
    """Uses macOS screencapture command."""
    timestamp = int(time.time())
    file_path = os.path.expanduser(f"~/Desktop/screenshot_{timestamp}.png")
    subprocess.run(['screencapture', file_path])
    print(f"Screenshot saved to: {file_path}")
    return file_path

def open_app(app_name):
    """Opens a macOS application using 'open -a'."""
    try:
        subprocess.run(['open', '-a', app_name], check=True)
        print(f"Opened app: {app_name}")
    except subprocess.CalledProcessError:
        print(f"Error: Could not open {app_name}. Make sure the name is correct.")

if __name__ == "__main__":
    # Test functions
    print("Testing macOS system actions...")
    # set_volume_relative(5)
    # take_screenshot()
    # open_app("Notes")
