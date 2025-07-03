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

# Load template files with error handling
def load_template_safe(path):
    """Load a template file with error handling."""
    if os.path.exists(path):
        template = cv2.imread(path, 0)  # Load as grayscale
        if template is not None:
            return template.astype(np.uint8)
    print(f"[WARN] Failed to load template: {path}")
    return None

# A rune's symbol on the minimap
RUNE_TEMPLATE = load_template_safe('assets/rune_template.png')

# Other players' symbols on the minimap
OTHER_TEMPLATE = load_template_safe('assets/other_template.png')

# The Elite Boss's warning sign
ELITE_TEMPLATE = load_template_safe('assets/elite_template.jpg')

# Rune CD Templates
RUNE_CD1_TEMPLATE = load_template_safe('assets/runeCD.png')
RUNE_CD2_TEMPLATE = load_template_safe('assets/runeCD2.png')

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = load_template_safe('assets/minimap_tl_template.png')
MM_BR_TEMPLATE = load_template_safe('assets/minimap_br_template.png')

# Set default dimensions if templates failed to load
if MM_TL_TEMPLATE is not None and MM_BR_TEMPLATE is not None:
    MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
    MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])
else:
    MMT_HEIGHT = 50  # Default fallback
    MMT_WIDTH = 50   # Default fallback

# The player's symbol on the minimap
PLAYER_TEMPLATE = load_template_safe('assets/player_template.png')

# Minimap border constants
MINIMAP_TOP_BORDER = 2
MINIMAP_BOTTOM_BORDER = 2


class Capture:
    """
    Captures the screen at regular intervals and processes the image to extract information.
    """

    def __init__(self):
        """
        Initializes this Capture object's main thread.
        """

        config.capture = self
        self.ready = False
        self.calibrated = False
        self.frame = None
        self.minimap_sample = None
        self.minimap_ratio = 1.333
        self.minimap = {}
        
        self.window = {
            'left': 0, 'top': 0,
            'width': 1366, 'height': 768
        }

        self.debug_mode = True
        self.sct = None

    def start(self):
        """Starts this Capture object's main thread."""
        print('\n[~] Starting capture')
        self.ready = True
        t = threading.Thread(target=self._main, daemon=True)
        t.start()

    def _load_saved_window_config(self):
        """Load saved window configuration from window_config.json"""
        try:
            import json
            config_path = 'window_config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                return config_data
        except Exception as e:
            print(f"[WARN] Could not load window config: {e}")
        return None

    def _load_manual_minimap_config(self):
        """Load manual minimap configuration from minimap_config.json"""
        try:
            import json
            config_path = 'minimap_config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                return config_data
        except Exception as e:
            print(f"[WARN] Could not load minimap config: {e}")
        return None

    def _find_maple_window(self):
        """Find MapleStory window using platform-agnostic approach."""
        
        # Try to get settings for manual window position
        try:
            from src.common import settings
            settings_obj = settings
        except:
            settings_obj = None

        if settings_obj is not None and getattr(settings_obj, 'use_manual_window_position', False):
            print(f"[INFO] Using manual window position: ({settings_obj.maple_window_left}, {settings_obj.maple_window_top}, {settings_obj.maple_window_width}, {settings_obj.maple_window_height})")
            rect = (
                settings_obj.maple_window_left,
                settings_obj.maple_window_top,
                settings_obj.maple_window_left + settings_obj.maple_window_width,
                settings_obj.maple_window_top + settings_obj.maple_window_height
            )
            self._cached_window_rect = rect
            return rect
        
        # Try template-based detection (works on all platforms)
        window_rect = self._find_maple_window_by_template()
        if window_rect:
            self._cached_window_rect = window_rect
            return window_rect
        
        # Platform-specific fallback
        system_name = platform.system()
        
        if system_name == "Windows":
            # Try to use Windows-specific window finding as fallback
            try:
                import win32gui
                import win32con
                
                def enum_windows_proc(hwnd, lParam):
                    window_text = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    if 'MapleStory' in window_text or 'MapleStory' in class_name:
                        rect = win32gui.GetWindowRect(hwnd)
                        lParam.append(rect)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_proc, windows)
                
                if windows:
                    rect = windows[0]
                    self._cached_window_rect = rect
                    return rect
            except ImportError:
                print("[INFO] Windows-specific libraries not available")
        
        # Load from saved config as fallback
        window_config = self._load_saved_window_config()
        if window_config:
            rect = (
                window_config['left'],
                window_config['top'],
                window_config['left'] + window_config['width'],
                window_config['top'] + window_config['height']
            )
            self._cached_window_rect = rect
            return rect
        
        # Default fallback
        print("[INFO] Using default window coordinates")
        rect = (0, 0, 1366, 768)
        self._cached_window_rect = rect
        return rect

    def _find_maple_window_by_template(self):
        """Template-based window detection as fallback."""
        try:
            # This would use template matching to find the MapleStory window
            # For now, return None to use other methods
            return None
        except Exception as e:
            print(f"[WARN] Template-based window detection failed: {e}")
            return None

    def screenshot(self):
        """Takes a screenshot of the MapleStory window."""

        try:
            with mss.mss() as sct:
                monitor = {
                    'left': self.window['left'],
                    'top': self.window['top'],
                    'width': self.window['width'],
                    'height': self.window['height']
                }
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                return frame
        except Exception as e:
            print(f"[WARN] Screenshot failed: {e}")
            return None

    def _calibrate_minimap(self):
        """
        Calibrate the minimap boundaries using templates or manual configuration.
        """
        
        try:
            # Try manual configuration first
            minimap_config = self._load_manual_minimap_config()
            
            if minimap_config:
                # Convert absolute screen coordinates to window-relative coordinates
                mm_left_abs = minimap_config['mm_left']
                mm_top_abs = minimap_config['mm_top']
                mm_right_abs = minimap_config['mm_right']
                mm_bottom_abs = minimap_config['mm_bottom']
                
                # Convert to window-relative coordinates
                mm_left_rel = mm_left_abs - self.window['left']
                mm_top_rel = mm_top_abs - self.window['top']
                mm_right_rel = mm_right_abs - self.window['left']
                mm_bottom_rel = mm_bottom_abs - self.window['top']
                
                mm_tl = (mm_left_rel, mm_top_rel)
                mm_br = (mm_right_rel, mm_bottom_rel)
                
                # Validate coordinates are within window bounds
                if (0 <= mm_tl[0] < self.window['width'] and 
                    0 <= mm_tl[1] < self.window['height'] and
                    0 <= mm_br[0] <= self.window['width'] and 
                    0 <= mm_br[1] <= self.window['height'] and
                    mm_br[0] > mm_tl[0] and mm_br[1] > mm_tl[1]):
                    
                    self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    if self.frame is not None:
                        # Extract minimap from color frame for display using relative coordinates
                        self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                        self.calibrated = True
                        print(f"[INFO] Minimap calibrated using manual config: TL={mm_tl}, BR={mm_br}, ratio={self.minimap_ratio:.2f}")
                        
                        # Store the relative coordinates for later use
                        self.minimap_bounds = {
                            'left': mm_tl[0],
                            'top': mm_tl[1], 
                            'right': mm_br[0],
                            'bottom': mm_br[1]
                        }
                        return True
                    else:
                        print("[WARN] No frame available for minimap calibration")
                        return False
                else:
                    print(f"[WARN] Minimap coordinates outside window bounds. Window: {self.window['width']}x{self.window['height']}, Minimap relative: {mm_tl} to {mm_br}")
                    return False
            else:
                print("[WARN] No manual minimap config found")
                return False
                
        except Exception as e:
            print(f"[WARN] Minimap calibration failed: {e}")
            return False

    def _detect_player(self, minimap):
        """Detect player position on the minimap using simple template matching."""
        
        try:
            if minimap is None or minimap.size == 0:
                return False
                
            # Ensure minimap is grayscale
            if len(minimap.shape) == 3:
                minimap = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
                
            if PLAYER_TEMPLATE is not None:
                # Use simple template matching
                player = utils.single_match(minimap, PLAYER_TEMPLATE, threshold=0.7)
                if player:
                    config.player_pos = utils.convert_to_relative(player, minimap)
                    return True
                else:
                    # Fallback to center of minimap
                    minimap_height, minimap_width = minimap.shape[:2]
                    center_pos = (minimap_width // 2, minimap_height // 2)
                    config.player_pos = utils.convert_to_relative(center_pos, minimap)
                    return True
            else:
                # No template available, use center of minimap
                minimap_height, minimap_width = minimap.shape[:2]
                center_pos = (minimap_width // 2, minimap_height // 2)
                config.player_pos = utils.convert_to_relative(center_pos, minimap)
                return True
                
        except Exception as e:
            print(f"[WARN] Player detection failed: {e}")
            return False

    def _detect_others(self, minimap):
        """Detect other players on the minimap using simple template matching."""
        
        try:
            if minimap is None or minimap.size == 0:
                config.others_pos = []
                return
                
            # Ensure minimap is grayscale
            if len(minimap.shape) == 3:
                minimap = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
                
            if OTHER_TEMPLATE is not None:
                # Use simple multi-match
                others = utils.multi_match(minimap, OTHER_TEMPLATE, threshold=0.8)
                if others:
                    # Convert to relative coordinates
                    config.others_pos = [utils.convert_to_relative(pos, minimap) for pos in others[:3]]  # Limit to 3
                else:
                    config.others_pos = []
            else:
                config.others_pos = []
                
        except Exception as e:
            print(f"[WARN] Others detection failed: {e}")
            config.others_pos = []

    def _detect_runes(self, minimap):
        """Detect runes on the minimap using simple template matching."""
        
        try:
            if minimap is None or minimap.size == 0:
                return False, None
                
            # Ensure minimap is grayscale
            if len(minimap.shape) == 3:
                minimap = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
                
            if RUNE_TEMPLATE is not None:
                # Use simple template matching
                rune = utils.single_match(minimap, RUNE_TEMPLATE, threshold=0.7)
                if rune:
                    rune_pos = utils.convert_to_relative(rune, minimap)
                    return True, rune_pos
                else:
                    return False, None
            else:
                return False, None
                
        except Exception as e:
            print(f"[WARN] Rune detection failed: {e}")
            return False, None

    def _main(self):
        """Constantly monitors the player's position and in-game events."""

        while True:
            # Find MapleStory window only if we don't have it cached
            if not hasattr(self, '_cached_window_rect') or self._cached_window_rect is None:
                rect = self._find_maple_window()
                
                self.window['left'] = rect[0]
                self.window['top'] = rect[1]
                self.window['width'] = max(rect[2] - rect[0], MMT_WIDTH)
                self.window['height'] = max(rect[3] - rect[1], MMT_HEIGHT)

                print(f"[INFO] Window coordinates: {self.window}")
            else:
                # Use cached window coordinates
                rect = self._cached_window_rect
                self.window['left'] = rect[0]
                self.window['top'] = rect[1]
                self.window['width'] = max(rect[2] - rect[0], MMT_WIDTH)
                self.window['height'] = max(rect[3] - rect[1], MMT_HEIGHT)

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

            # Extract minimap for processing
            if self.calibrated and hasattr(self, 'minimap_bounds'):
                mm_tl = (self.minimap_bounds['left'], self.minimap_bounds['top'])
                mm_br = (self.minimap_bounds['right'], self.minimap_bounds['bottom'])
                
                # Extract minimap from the current frame using window-relative coordinates
                minimap = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                if len(minimap.shape) == 3:
                    minimap_gray = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
                else:
                    minimap_gray = minimap
                
                # Store current minimap for display
                self.minimap_sample = minimap
                
                # Detect player position
                if self._detect_player(minimap_gray):
                    # Detect runes
                    rune_active, rune_pos = self._detect_runes(minimap_gray)
                    
                    # Detect other players
                    self._detect_others(minimap_gray)
                    
                    # Update minimap data structure
                    self.minimap = {
                        'minimap': minimap,
                        'rune_active': rune_active,
                        'rune_pos': rune_pos,
                        'player_pos': config.player_pos,
                        'others_pos': config.others_pos,
                        'path': config.path if hasattr(config, 'path') else []
                    }
                
            time.sleep(0.1)  # 10 FPS
