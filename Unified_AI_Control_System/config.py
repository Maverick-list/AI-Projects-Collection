"""
Global Configuration for Unified AI Control System
"""

# ============== CAMERA SETTINGS ==============
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 30

# ============== MODE SETTINGS ==============
# Enable/disable modes at startup (can be changed during runtime)
ENABLE_EYE_TRACKING = True
ENABLE_HAND_GESTURE = True
ENABLE_SIGN_LANGUAGE = True
ENABLE_FACE_RECOGNITION = True
ENABLE_VIRTUAL_KEYBOARD = False

# ============== KEYBOARD SHORTCUTS ==============
# Mode switching keys
KEY_EYE_TRACKING = '1'
KEY_HAND_GESTURE = '2'
KEY_SIGN_LANGUAGE = '3'
KEY_VIRTUAL_KEYBOARD = '4'
KEY_FACE_RECOGNITION = '5'
KEY_MENU = 'm'
KEY_QUIT = 'q'
KEY_TOGGLE_ACTIVE = 'a'

# ============== MODEL PATHS ==============
HAND_MODEL_PATH = "models/hand_landmarker.task"
FACE_MODEL_PATH = "models/face_landmarker.task"
FACE_CASCADE_PATH = "models/haarcascade_frontalface_default.xml"

# ============== HAND GESTURE SETTINGS ==============
HAND_SMOOTHING_FACTOR = 0.7
HAND_FRAME_MARGIN_X = 100
HAND_FRAME_MARGIN_Y = 100

# Gesture detection thresholds
PINCH_THRESHOLD = 40  # pixels
SCROLL_ZONE_HEIGHT = 50  # pixels from center
SWITCH_EDGE_WIDTH = 150  # pixels from edge
VOLUME_THRESHOLD_HIGH = 140  # pixels
VOLUME_THRESHOLD_LOW = 30  # pixels

# Colors for visualization (BGR)
COLOR_MOUSE = (147, 20, 255)  # Purple
COLOR_CLICK = (0, 255, 0)  # Green
COLOR_SCROLL = (255, 255, 0)  # Cyan
COLOR_SWITCH = (0, 165, 255)  # Orange
COLOR_VOL = (0, 255, 255)  # Yellow
COLOR_FACE_RECOGNITION = (255, 0, 0)  # Blue

# ============== EYE TRACKING SETTINGS ==============
EAR_THRESHOLD = 0.25  # Eye Aspect Ratio for blink detection
EYE_SMOOTHING_BUFFER = 5  # frames
EYE_MOVE_GAIN = 2.0  # Cursor sensitivity multiplier

# ============== SIGN LANGUAGE SETTINGS ==============
SIGN_STABILITY_THRESHOLD = 15  # frames
SIGN_COOLDOWN_PERIOD = 3.0  # seconds
SIGN_DEFAULT_LANGUAGE = 'en'  # 'en' or 'id'
SIGN_TTS_SPEED = 1.0

# ============== VIRTUAL KEYBOARD SETTINGS ==============
VKBD_BUTTON_SIZE = [70, 70]  # [width, height]
VKBD_SPACING = 80  # pixels between buttons
VKBD_OFFSET = 10  # pixels from edge
VKBD_CLICK_THRESHOLD = 50  # pixels for pinch detection
VKBD_DELAY_FRAMES = 10  # frames between clicks

# ============== PERFORMANCE SETTINGS ==============
FPS_SMOOTHING = 0.9  # Exponential smoothing for FPS display
MAX_FPS = 30  # Target FPS cap

# ============== UI SETTINGS ==============
UI_FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
UI_FONT_SCALE = 0.6
UI_FONT_THICKNESS = 2
UI_PADDING = 20
UI_STATUS_BAR_HEIGHT = 80

# Window layout modes: 'split', 'tabbed', 'overlay'
UI_LAYOUT_MODE = 'split'
