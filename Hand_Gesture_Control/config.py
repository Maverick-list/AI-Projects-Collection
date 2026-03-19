
# Screen settings
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Camera settings
CAM_WIDTH = 640
CAM_HEIGHT = 480
FPS = 30

# Smoothing factors
SMOOTHING_WINDOW = 7      # Number of frames for moving average (Higher = smoother/more lag)
CURSOR_SPEED_GAIN = 1.0   # Sensitivity multiplier
DEADZONE = 5.0            # Pixels movement to ignore (jitter reduction)

# Cursor sensitivity
# Region of interest for hand movement (0-1)
FRAME_MARGIN_X = 120
FRAME_MARGIN_Y = 100

# Gesture Thresholds
PINCH_THRESHOLD = 35  # Pixel distance for pinch click
SCROLL_THRESHOLD = 40 # Pixel distance for scroll activation

# Volume Gesture Ranges (Distance between Thumb and Index)
# Range logic: < MIN = Down, > MAX = Up
VOL_DIST_MIN = 30
VOL_DIST_MAX = 140

# Colors (BGR)
COLOR_MOUSE = (255, 0, 0)
COLOR_CLICK = (0, 255, 0)
COLOR_SCROLL = (0, 0, 255)
COLOR_SWITCH = (255, 255, 0)
COLOR_VOL = (0, 165, 255)
