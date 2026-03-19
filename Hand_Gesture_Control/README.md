# Hand Gesture Control System

Control your Mac using hand gestures! This application uses MediaPipe to track your hand and PyAutoGUI to control the mouse and keyboard.

## 🛠️ Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You might need to grant Accessibility permissions to your Terminal/IDE for PyAutoGUI to control the mouse.*

2.  **Model File**:
    Ensure `hand_landmarker.task` is in the project directory. (It has been copied for you).

## 🚀 Usage

Run the application:
```bash
python main.py
```

## ✋ Gestures

| Gesture | Action | Description |
| :--- | :--- | :--- |
| **Index Up** | **Move Cursor** | Only index finger extended. Pointer follows finger tip. |
| **Pinch (Index+Thumb)** | **Left Click** | Bring Index and Thumb tips close together. |
| **Index + Middle Up** | **Scroll** | Move hand up/down to scroll. |
| **Thumb + Index Open** | **Volume** | Distance between Thumb and Index controls volume. |
| **3 Fingers Up** | **Switch Window** | Move hand Left/Right to switch spaces/windows. |

## ⌨️ Controls

- **`a`**: Toggle Active/Inactive mode (Prevent accidental clicks).
- **`q`**: Quit the application.

## ⚙️ Configuration

Edit `config.py` to adjust:
- `SMOOTHING_FACTOR`: Higher = smoother but more lag.
- `FRAME_MARGIN`: Area of camera mapped to screen.
- `gestures` thresholds.
