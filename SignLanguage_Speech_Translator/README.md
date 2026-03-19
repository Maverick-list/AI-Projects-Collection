# SignLanguage Speech Translator PRO

An advanced AI application that translates 20 different hand gestures into spoken Indonesian/Islamic phrases. It includes recording capabilities, gesture learning, and a split-screen dashboard.

## 🌟 New Features
- **20 Gestures**: Includes "Listen", "Look", "Eat", "Yes/No", "Four", "Bad", "Stop", and more.
- **Interactive Tutorial**: Step-by-step masterclass for all 20 gestures with voice calibration.
- **Split-Screen UI**: Real-time webcam feed on the left, history and stats on the right.
- **Recording Mode**: Record your sessions into MP4 videos with auto-generated subtitle timestamps.
- **Gesture Learning**: Teach the AI new custom gestures on the fly.
- **Speech History**: View a log of the last 10 detected gestures with timestamps.
- **Multi-Hand Support**: Detect and translate gestures from both hands simultaneously.
- **Web Export**: Generate an HTML gallery of all your recorded sessions.

## ⌨️ Controls & Hotkeys
- **`q`**: Quit the application.
- **`r`**: Toggle **Recording** (Start/Stop).
- **`l`**: Toggle **Learning Mode**.
- **`n`**: While in Learning Mode, save current hand position as a new gesture.
- **`e`**: **Export** all recordings to an HTML report.
- **`+` / `-`**: Increase/Decrease Speech Speed (0.8x to 2.0x).
- **`v`**: Toggle Mute/Unmute.
- **`s`**: Take a high-res screenshot of the entire dashboard.

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. **Generate Assets** (First Time Only):
   ```bash
   python3 tutorial.py
   ```
   This will create the necessary gesture images in `assets/gestures`.

## 🚀 Usage

Run the main application:
```bash
python3 main.py
```

## 📂 Project Structure
- `main.py`: Interactive dashboard and core loop.
- `gestures.py`: Gesture classification logic for 20+ signs.
- `speech.py`: TTS engine with gTTS and Pygame.
- `record_manager.py`: Handles video recording and SRT generation.
- `web_exporter.py`: Generates the HTML session report.

## 💡 Calibration Tips
- **Meme Audio**: The project now includes a special meme audio for the Jokowi gesture at `assets/hidup_jokowiiie.mp3`. 
- **Trigger Legend**: Show a **fist upwards** gesture to trigger the "Hidup Jokowiiie!" meme animation and sound.
- **Stability Bar**: Watch the green bar fill up; keep your hand steady for about 0.5s to trigger speech.
- **Multi-Hand**: Try doing "Hello" with one hand and "Good" (Thumb up) with the other for combo phrases!
- **Lighting**: Frontal lighting is critical for accurate landmark detection.
