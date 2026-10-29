# AI Combined Assistant (Eye + Hand + Voice) for macOS

This project is a powerful macOS assistant that combines Eye Tracking, Hand Gestures, and Voice Commands for a touchless desktop experience.

## ✨ Features
1. **Eye Tracking Control**: Move the cursor with your eyes and blink to click.
2. **Hand Gesture Control**:
   - **Thumbs Up/Down**: Increase/Decrease system volume.
   - **Two Fingers Up**: Scroll page (move hand up/down to control direction).
   - **Thumb + Pinky Out**: Take a screenshot (saved to Desktop).
   - **Open Palm**: Confirm voice commands.
3. **Voice Control**:
   - "Hi my assistant" -> Wake phrase.
   - "Open the app" -> Follow-up command.
   - Requires an **Open Palm** gesture to execute the launch (Safari by default).

## 🚀 Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Run the assistant: `python main_combined_assistant.py`
3. Grant macOS permissions when prompted:
   - **Accessibility**: For mouse and scroll control.
   - **Screen Recording**: For taking screenshots.
   - **Microphone**: For voice commands.

## 🛠️ Configuration
- **Sensitivity**: Adjust `eye_ctrl.MOVE_GAIN` in `eye_control.py`.
- **Gesture Mappings**: Modify thresholds in `hand_control.py`.
- **Voice App**: Change the app in `main_combined_assistant.py` (Default: Safari).

## 📂 Project Structure
- `main_combined_assistant.py`: Central orchestration.
- `eye_control.py`: Refined pupil tracking and blink detection.
- `hand_control.py`: Gesture recognition using MediaPipe Hands.
- `voice_control.py`: Multithreaded voice command listener.
- `system_actions_mac.py`: Native macOS integrations (AppleScript, shell).
- `utils.py`: Helper functions for smoothing and EAR.
