"""
A module that handles screen capture and image processing for the bot.
"""

import cv2
import mss
import numpy as np
import threading
import time
import os
import platform
from src.common import config, utils

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = cv2.imread('assets/minimap_tl_template.png', 0)
MM_BR_TEMPLATE = cv2.imread('assets/minimap_br_template.png', 0)
MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])

# The player's symbol on the minimap
PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape

# The other players' symbols on the minimap
OTHER_TEMPLATE = cv2.imread('assets/other_template.png', 0)

# Minimap border constants
MINIMAP_TOP_BORDER = 2
MINIMAP_BOTTOM_BORDER = 2


class Capture:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    def __init__(self):
        """Initializes this Capture object's main thread."""

        config.capture = self

        self.frame = None
        self.minimap = {}
        self.minimap_ratio = 1
        self.minimap_sample = None
        self.sct = None
        self.window = {
            'left': 0,
            'top': 0,
            'width': 1366,
            'height': 768
        }

        self.ready = False
        self.calibrated = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """Starts this Capture's thread."""

        print('\n[~] Started video capture')
        self.thread.start()

    def _load_saved_window_config(self):
        """Load saved window configuration from file."""
        try:
            import json
            import os
            
            config_file = "window_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    # Validate the config
                    if all(key in config_data for key in ['left', 'top', 'width', 'height']):
                        return config_data
        except Exception as e:
            print(f"[WARN] Failed to load saved window config: {e}")
        return None
    
    def _load_manual_minimap_config(self):
        """Load manual minimap configuration from file."""
        try:
            import json
            import os
            
            config_file = "minimap_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    # Validate the config
                    if all(key in config_data for key in ['mm_left', 'mm_top', 'mm_right', 'mm_bottom']):
                        return config_data
        except Exception as e:
            print(f"[WARN] Failed to load manual minimap config: {e}")
        return None

    def _find_maple_window(self):
        """Cross-platform window finding."""
        # Check for saved window configuration FIRST (from automation tools)
        saved_config = self._load_saved_window_config()
        if saved_config:
            print(f"[INFO] Using saved window config: {saved_config}")
            return (
                saved_config['left'],
                saved_config['top'],
                saved_config['left'] + saved_config['width'],
                saved_config['top'] + saved_config['height']
            )
        
        # Check if manual window position is enabled (fallback)
        if hasattr(config, 'settings') and hasattr(config.settings, 'use_manual_window_position') and config.settings.use_manual_window_position:
            print(f"[INFO] Using manual window position: ({config.settings.maple_window_left}, {config.settings.maple_window_top}, {config.settings.maple_window_width}, {config.settings.maple_window_height})")
            return (
                config.settings.maple_window_left,
                config.settings.maple_window_top,
                config.settings.maple_window_left + config.settings.maple_window_width,
                config.settings.maple_window_top + config.settings.maple_window_height
            )
        
        # Try template-based detection (works on all platforms)
        window_rect = self._find_maple_window_by_template()
        if window_rect:
            return window_rect
        
        # Platform-specific fallback
        if platform.system() == "Windows":
            try:
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                handle = user32.FindWindowW(None, 'MapleStory')
                if handle:
                    rect = wintypes.RECT()
                    user32.GetWindowRect(handle, ctypes.pointer(rect))
                    rect = (rect.left, rect.top, rect.right, rect.bottom)
                    rect = tuple(max(0, x) for x in rect)
                    return rect
            except Exception as e:
                print(f"[WARN] Windows API detection failed: {e}")
        
        # Default fallback
        print("[INFO] Using default window coordinates")
        return (0, 0, 1366, 768)

    def _find_maple_window_by_template(self):
        """Find MapleStory window using template matching."""
        try:
            with mss.mss() as sct:
                # Take a full screen screenshot
                screenshot = sct.grab(sct.monitors[1])  # Primary monitor
                img = np.array(screenshot)
                
                # Convert BGRA to BGR if needed
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Convert to grayscale for template matching
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Look for MapleStory window using template matching
                # This is a simplified approach - you might need to create a window template
                return None  # For now, return None to use fallback
                
        except Exception as e:
            print(f"[WARN] Template-based window detection failed: {e}")
            return None

    def screenshot(self):
        """Takes a screenshot of the MapleStory window."""

        try:
            with mss.mss() as sct:
                # Create a region dict for mss
                region = {
                    'left': self.window['left'],
                    'top': self.window['top'],
                    'width': self.window['width'],
                    'height': self.window['height']
                }
                
                # Take screenshot
                sct_img = sct.grab(region)
                img = np.array(sct_img)
                
                # Convert BGRA to BGR if needed
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Convert to grayscale for template matching
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                return gray
                
        except Exception as e:
            print(f"[WARN] Screenshot failed: {e}")
            return None

    def _calibrate_minimap(self):
        """Calibrate the minimap by finding its corners using template matching."""
        
        try:
            # Try to use manual minimap configuration first
            manual_mm_config = self._load_manual_minimap_config()
            if manual_mm_config:
                print(f"[INFO] Using manual minimap config: {manual_mm_config}")
                # Convert absolute screen coordinates to relative window coordinates
                mm_tl = (
                    manual_mm_config['mm_left'] - self.window['left'], 
                    manual_mm_config['mm_top'] - self.window['top']
                )
                mm_br = (
                    manual_mm_config['mm_right'] - self.window['left'], 
                    manual_mm_config['mm_bottom'] - self.window['top']
                )
                
                # Validate coordinates are within window bounds
                if (0 <= mm_tl[0] < self.window['width'] and 
                    0 <= mm_tl[1] < self.window['height'] and
                    0 <= mm_br[0] <= self.window['width'] and 
                    0 <= mm_br[1] <= self.window['height'] and
                    mm_br[0] > mm_tl[0] and mm_br[1] > mm_tl[1]):
                    
                    self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    self.calibrated = True
                    print(f"[INFO] Minimap calibrated using manual config: TL={mm_tl}, BR={mm_br}, ratio={self.minimap_ratio:.2f}")
                    return True
                else:
                    print(f"[WARN] Manual minimap coordinates are outside window bounds: TL={mm_tl}, BR={mm_br}, window={self.window}")
                    manual_mm_config = None  # Fall back to template detection
            
            # Fall back to template-based detection
            if not manual_mm_config:
                # Find the top-left corner of the minimap
                tl_match = utils.single_match(self.frame, MM_TL_TEMPLATE)
                if not tl_match:
                    print("[WARN] Could not find minimap top-left corner")
                    return False
                
                # Find the bottom-right corner of the minimap
                br_match = utils.single_match(self.frame, MM_BR_TEMPLATE)
                if not br_match:
                    print("[WARN] Could not find minimap bottom-right corner")
                    return False
                
                # Calculate minimap boundaries with borders
                mm_tl = (
                    tl_match[0] + MINIMAP_BOTTOM_BORDER,
                    tl_match[1] + MINIMAP_TOP_BORDER
                )
                mm_br = (
                    max(mm_tl[0] + PT_WIDTH, br_match[0] - MINIMAP_BOTTOM_BORDER),
                    max(mm_tl[1] + PT_HEIGHT, br_match[1] - MINIMAP_BOTTOM_BORDER)
                )
                
                # Validate minimap dimensions
                minimap_width = mm_br[0] - mm_tl[0]
                minimap_height = mm_br[1] - mm_tl[1]
                
                if minimap_width > 0 and minimap_height > 0:
                    self.minimap_ratio = minimap_width / minimap_height
                    self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    self.calibrated = True
                    print(f"[INFO] Minimap calibrated using templates: TL={mm_tl}, BR={mm_br}, ratio={self.minimap_ratio:.2f}")
                    return True
                else:
                    print(f"[WARN] Invalid minimap dimensions: width={minimap_width}, height={minimap_height}")
                    return False
                    
        except Exception as e:
            print(f"[WARN] Minimap calibration failed: {e}")
            return False

    def _detect_player(self, minimap):
        """Detect the player's position on the minimap."""
        
        try:
            # Find player using simple multi_match with high threshold
            player = utils.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
            if player:
                config.player_pos = utils.convert_to_relative(player[0], minimap)
                return True
            else:
                print("[WARN] Could not detect player position")
                return False
                
        except Exception as e:
            print(f"[WARN] Player detection failed: {e}")
            return False

    def _detect_others(self, minimap):
        """Detect other players on the minimap."""
        
        try:
            if OTHER_TEMPLATE is not None:
                others = utils.multi_match(minimap, OTHER_TEMPLATE, threshold=0.8)
                config.others_pos = [utils.convert_to_relative(pos, minimap) for pos in others]
            else:
                config.others_pos = []
                
        except Exception as e:
            print(f"[WARN] Others detection failed: {e}")
            config.others_pos = []

    def _main(self):
        """Constantly monitors the player's position and in-game events."""

        while True:
            # Find MapleStory window
            rect = self._find_maple_window()
            
            self.window['left'] = rect[0]
            self.window['top'] = rect[1]
            self.window['width'] = max(rect[2] - rect[0], MMT_WIDTH)
            self.window['height'] = max(rect[3] - rect[1], MMT_HEIGHT)

            print(f"[INFO] Window coordinates: {self.window}")

            # Take screenshot
            with mss.mss() as self.sct:
                self.frame = self.screenshot()
            if self.frame is None:
                continue
                
            # Calibrate minimap if not already calibrated
            if not self.calibrated:
                if not self._calibrate_minimap():
                    print("[WARN] Minimap calibration failed, retrying...")
                    time.sleep(1)
                    continue
                    
            # Extract minimap region
            if self.minimap_sample is not None:
                minimap = self.minimap_sample.copy()
                
                # Detect player position
                if self._detect_player(minimap):
                    # Detect other players
                    self._detect_others(minimap)
                    
                    # Update minimap data
                    self.minimap = {
                        'minimap': minimap,
                        'player_pos': config.player_pos,
                        'others_pos': config.others_pos,
                        'rune_active': False,
                        'rune_pos': None,
                        'path': []
                    }
                    
                    self.ready = True
                else:
                    print("[WARN] Player detection failed")
                    self.ready = False
            else:
                print("[WARN] No minimap sample available")
                self.ready = False
                
            time.sleep(0.1)  # 10 FPS update rate
