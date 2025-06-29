"""A module for tracking useful in-game information."""

import time
import cv2
import threading
import platform
import mss
import numpy as np
from src.common import config, utils

# Platform-specific imports
if platform.system() == "Windows":
    import ctypes
    import mss.windows
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    mss.windows.CAPTUREBLT = 0
else:
    # Non-Windows platforms
    user32 = None
    wintypes = None

# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9

# Offset in pixels to adjust for windowed mode
WINDOWED_OFFSET_TOP = 36
WINDOWED_OFFSET_LEFT = 10

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = cv2.imread('assets/minimap_tl_template.png', 0)
MM_BR_TEMPLATE = cv2.imread('assets/minimap_br_template.png', 0)

MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])

# The player's symbol on the minimap
PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape


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

    def _find_maple_window(self):
        """Cross-platform window finding."""
        # Check if manual window position is enabled
        if hasattr(config, 'settings') and hasattr(config.settings, 'use_manual_window_position') and config.settings.use_manual_window_position:
            print(f"[INFO] Using manual window position: ({config.settings.maple_window_left}, {config.settings.maple_window_top}, {config.settings.maple_window_width}, {config.settings.maple_window_height})")
            return (
                config.settings.maple_window_left,
                config.settings.maple_window_top,
                config.settings.maple_window_left + config.settings.maple_window_width,
                config.settings.maple_window_top + config.settings.maple_window_height
            )
        
        # Check for saved window configuration
        saved_config = self._load_saved_window_config()
        if saved_config:
            print(f"[INFO] Using saved window config: {saved_config}")
            return (
                saved_config['left'],
                saved_config['top'],
                saved_config['left'] + saved_config['width'],
                saved_config['top'] + saved_config['height']
            )
        
        # Try template-based detection first (works on all platforms)
        window_rect = self._find_maple_window_by_template()
        if window_rect:
            return window_rect
        
        if platform.system() == "Windows" and user32:
            try:
                handle = user32.FindWindowW(None, 'MapleStory')
                if handle:
                    rect = wintypes.RECT()
                    user32.GetWindowRect(handle, ctypes.pointer(rect))
                    rect = (rect.left, rect.top, rect.right, rect.bottom)
                    rect = tuple(max(0, x) for x in rect)
                    return rect
            except Exception as e:
                print(f"[WARN] Windows window finding failed: {e}")
        
        # Fallback: use entire screen
        print(f"[INFO] Using full screen capture for {platform.system()}")
        return (0, 0, 1366, 768)
    
    def _find_maple_window_by_template(self):
        """Find MapleStory window by looking for distinctive UI elements."""
        try:
            with mss.mss() as sct:
                # Capture entire screen
                screenshot = sct.grab(sct.monitors[1])  # Primary monitor
                frame = np.array(screenshot)
                
                # Convert from BGRA to BGR if needed
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                
                # Look for minimap corner templates
                tl_matches = utils.multi_match(frame, MM_TL_TEMPLATE, threshold=0.8)
                br_matches = utils.multi_match(frame, MM_BR_TEMPLATE, threshold=0.8)
                
                if tl_matches and br_matches:
                    # Find the best pair of corners
                    best_window = None
                    best_score = 0
                    
                    for tl in tl_matches:
                        for br in br_matches:
                            # Calculate window dimensions
                            left = max(0, tl[0] - 50)  # Add some margin
                            top = max(0, tl[1] - 50)
                            right = min(frame.shape[1], br[0] + 50)
                            bottom = min(frame.shape[0], br[1] + 50)
                            
                            width = right - left
                            height = bottom - top
                            
                            # Validate reasonable window size
                            if 800 <= width <= 2000 and 600 <= height <= 1200:
                                # Calculate score based on how well corners align
                                corner_distance = utils.distance(tl, br)
                                if corner_distance > best_score:
                                    best_score = corner_distance
                                    best_window = (left, top, right, bottom)
                    
                    if best_window:
                        print(f"[INFO] Found MapleStory window by template: {best_window}")
                        return best_window
                
                print("[INFO] Template-based window detection failed, using fallback")
                return None
                
        except Exception as e:
            print(f"[WARN] Template-based window detection failed: {e}")
            return None

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

    def _main(self):
        """Constantly monitors the player's position and in-game events."""

        while True:
            # Calibrate screen capture
            rect = self._find_maple_window()
            
            self.window['left'] = rect[0]
            self.window['top'] = rect[1]
            self.window['width'] = max(rect[2] - rect[0], MMT_WIDTH)
            self.window['height'] = max(rect[3] - rect[1], MMT_HEIGHT)

            print(f"[INFO] Window coordinates: {self.window}")

            # Calibrate by finding the top-left and bottom-right corners of the minimap
            with mss.mss() as self.sct:
                self.frame = self.screenshot()
            if self.frame is None:
                continue
                
            try:
                # Try to use manual minimap configuration first
                manual_mm_config = self._load_manual_minimap_config()
                if manual_mm_config:
                    print(f"[INFO] Using manual minimap config: {manual_mm_config}")
                    mm_tl = (manual_mm_config['mm_left'], manual_mm_config['mm_top'])
                    mm_br = (manual_mm_config['mm_right'], manual_mm_config['mm_bottom'])
                    self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    self.calibrated = True
                else:
                    # Fall back to template-based detection
                    tl, _ = utils.single_match(self.frame, MM_TL_TEMPLATE)
                    _, br = utils.single_match(self.frame, MM_BR_TEMPLATE)
                    mm_tl = (
                        tl[0] + MINIMAP_BOTTOM_BORDER,
                        tl[1] + MINIMAP_TOP_BORDER
                    )
                    mm_br = (
                        max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
                        max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
                    )
                    self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    self.calibrated = True
            except Exception as e:
                print(f"[WARN] Minimap calibration failed: {e}")
                self.calibrated = False
                time.sleep(1)
                continue

            with mss.mss() as self.sct:
                while True:
                    if not self.calibrated:
                        break

                    # Check if window moved (Windows only)
                    if platform.system() == "Windows" and user32:
                        try:
                            handle2 = user32.FindWindowW(None, 'MapleStory')
                            rect2 = wintypes.RECT()
                            user32.GetWindowRect(handle2, ctypes.pointer(rect2))
                            rect2 = (rect2.left, rect2.top, rect2.right, rect2.bottom)
                            if rect2 != rect:
                                time.sleep(1)
                                break
                        except:
                            pass

                    # Take screenshot
                    self.frame = self.screenshot()
                    if self.frame is None:
                        continue

                    # Crop the frame to only show the minimap
                    try:
                        minimap = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]

                        # Determine the player's position
                        player = utils.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
                        if player:
                            config.player_pos = utils.convert_to_relative(player[0], minimap)

                        # Package display information to be polled by GUI
                        self.minimap = {
                            'minimap': minimap,
                            'rune_active': config.bot.rune_active,
                            'rune_pos': config.bot.rune_pos,
                            'path': config.path,
                            'player_pos': config.player_pos
                        }
                    except Exception as e:
                        print(f"[WARN] Minimap processing failed: {e}")

                    if not self.ready:
                        self.ready = True
                    time.sleep(0.001)

    def screenshot(self, delay=1):
        try:
            with mss.mss() as sct:
                # Capture the entire screen (monitor 0 is all monitors combined)
                # This works better for ultrawide monitors
                screenshot = sct.grab(sct.monitors[0])
                frame = np.array(screenshot)
                
                # Convert from BGRA to BGR if needed
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                
                # Crop to just the MapleStory window using absolute coordinates
                window_frame = frame[self.window['top']:self.window['top'] + self.window['height'], 
                                   self.window['left']:self.window['left'] + self.window['width']]
                
                return window_frame
        except mss.exception.ScreenShotError:
            print(f'\n[!] Error while taking screenshot, retrying in {delay} second'
                  + ('s' if delay != 1 else ''))
            time.sleep(delay)
            return None
        except Exception as e:
            print(f'\n[!] Screenshot error: {e}')
            time.sleep(delay)
            return None
