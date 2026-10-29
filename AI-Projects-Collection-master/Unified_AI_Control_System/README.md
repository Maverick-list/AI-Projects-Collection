# Unified AI Control System 🚀

A powerful, integrated AI control system that combines **Eye Tracking**, **Hand Gesture Control**, **Sign Language Translation**, and **Virtual Keyboard** into one seamless application.

## ✨ Features

### 1. 👁️ Eye Tracking Mode
- **Cursor Control**: Move mouse cursor with eye movements
- **Click**: Blink to click
- **High Precision**: Adjustable sensitivity and smoothing

### 2. ✋ Hand Gesture Mode
- **Move Cursor**: Index finger up to control mouse
- **Click**: Pinch gesture (thumb + index finger)
- **Right Click**: Special pinch variation
- **Scroll**: Two fingers up, move hand up/down
- **Volume Control**: Thumb + index distance controls volume
- **Switch Desktops**: Three fingers, swipe left/right at screen edges

### 3. 🤟 Sign Language Mode
- **Gesture Recognition**: Detects common sign language gestures
- **Text-to-Speech**: Converts gestures to spoken words
- **History Tracking**: Shows recent translations
- **Multi-language**: English and Indonesian support

### 4. ⌨️ Virtual Keyboard Mode
- **Hand Typing**: Type using hand gestures
- **Visual Feedback**: On-screen keyboard display
- **Pinch to Type**: Hover and pinch to press keys
- **Text Buffer**: See what you've typed in real-time

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Webcam
- macOS, Windows, or Linux

### Setup

1. **Clone or navigate to the project**:
   ```bash
   cd /path/to/Unified_AI_Control_System
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Grant permissions** (macOS):
   - Accessibility: System Preferences → Security & Privacy → Privacy → Accessibility
   - Camera: Allow camera access when prompted
  - Microphone: For sign language speech output

## 🚀 Usage

### Starting the Application

```bash
python main.py
```

The application will:
1. Download required MediaPipe models (if not present)
2. Initialize selected modules
3. Start with Hand Gesture mode active (default)
4. Display unified control window

### Keyboard Controls

| Key | Action |
|-----|--------|
| **1** | Toggle Eye Tracking mode |
| **2** | Toggle Hand Gesture mode |
| **3** | Toggle Sign Language mode |
| **4** | Toggle Virtual Keyboard mode |
| **M** | Show/hide mode selection menu |
| **A** | Toggle hand gesture active/inactive (safety) |
| **Q** | Quit application |

### Mode Selection

- Press **M** to open the mode selection menu
- Multiple modes can be active simultaneously
- Active modes are highlighted in green
- Switch modes on-the-fly without restarting

## 📋 Gestures Reference

### Hand Gesture Mode

| Gesture | Fingers | Action |
|---------|---------|--------|
| **Move** | Index up | Control cursor |
| **Click** | Thumb + Index pinch | Left click |
| **Scroll** | Index + Middle up | Scroll (move hand up/down) |
| **Volume Up** | Thumb + Index wide apart | Increase volume |
| **Volume Down** | Thumb + Index close together | Decrease volume |
| **Switch Desktop** | Index + Middle + Thumb | Swipe at screen edges |

### Virtual Keyboard

- **Hover**: Extend index finger over key
- **Type**: Pinch (index + middle fingers close)
- **Space**: SP button
- **Backspace**: ← button
- **Shift**: ⇧ button (toggles case)

## ⚙️ Configuration

Edit `config.py` to customize:

### Camera Settings
```python
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 30
```

### Enable/Disable Modules at Startup
```python
ENABLE_EYE_TRACKING = True
ENABLE_HAND_GESTURE = True
ENABLE_SIGN_LANGUAGE = True
ENABLE_VIRTUAL_KEYBOARD = True
```

### Gesture Sensitivity
```python
PINCH_THRESHOLD = 40  # Lower = more sensitive
EYE_MOVE_GAIN = 2.0   # Higher = faster eye movement
HAND_SMOOTHING_FACTOR = 0.7  # Higher = smoother (more lag)
```

## 🏗️ Architecture

```
Unified_AI_Control_System/
├── main.py                 # Main orchestrator
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── shared/                # Shared infrastructure
│   ├── camera_manager.py  # Singleton camera
│   ├── model_manager.py   # MediaPipe models
│   └── utils.py          # Common utilities
├── modules/               # Control modules
│   ├── eye_tracking.py
│   ├── hand_gesture.py
│   ├── sign_language.py
│   └── virtual_keyboard.py
└── models/                # MediaPipe models (auto-downloaded)
    ├── hand_landmarker.task
    └── face_landmarker.task
```

### Key Design Features

- **Singleton Camera**: Single camera instance shared across all modules
- **Lazy Loading**: Models loaded only when needed
- **Modular Architecture**: Easy to add/remove modules
- **Event System**: Modules communicate via event dictionaries
- **Performance Optimized**: Maintains 20+ FPS with multiple modes

## 🐛 Troubleshooting

### Camera Not Found
- Ensure webcam is connected and not used by another application
- Check camera permissions in system settings

### Low FPS / Performance Issues
- Disable unused modes (press 1-4 to toggle)
- Reduce camera resolution in `config.py`
- Run fewer modes simultaneously

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`
- Ensure you're in the project directory

### Hand/Eye Detection Not Working
- Ensure good lighting conditions
- Position yourself clearly in front of camera
- Adjust detection confidence in module files

### PyAutoGUI Permission Errors (macOS)
- Grant Accessibility permissions to Terminal/IDE
- System Preferences → Security & Privacy → Privacy → Accessibility

## 📊 Performance Tips

1. **Best Performance**: Use one mode at a time
2. **Multi-Mode**: Eye + Hand works well together
3. **Avoid**: Running all 4 modes simultaneously (CPU intensive)
4. **Lighting**: Ensure good, even lighting for best detection
5. **Camera**: 720p or higher recommended for accuracy

## 🔧 Advanced Usage

### Running Specific Modules Only

Edit `config.py`:
```python
ENABLE_EYE_TRACKING = False
ENABLE_HAND_GESTURE = True
ENABLE_SIGN_LANGUAGE = False
ENABLE_VIRTUAL_KEYBOARD = False
```

### Adding Custom Gestures

1. Edit gesture detection in respective module files
2. Add gesture names to `gesture_recognition.py`
3. Map actions in module's `process_frame()` method

### Changing Keyboard Layout

Edit `VirtualKeyboardModule.keys_upper` and `keys_lower` in `modules/virtual_keyboard.py`

## 📝 Credits

This project integrates and enhances:
- AI Mouse Eye Tracking
- Hand Gesture Control
- SignLanguage Speech Translator  
- Virtual Keyboard

Powered by:
- [MediaPipe](https://mediapipe.dev/) - Google's ML solutions
- [OpenCV](https://opencv.org/) - Computer vision library
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - GUI automation
- [pynput](https://pynput.readthedocs.io/) - Input control

## 📜 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

**Made with ❤️ for accessible and innovative human-computer interaction**
