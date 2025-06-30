"""A module for tracking useful in-game information."""

import time
import cv2
import threading
import platform
import mss
import numpy as np
import os
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

# Load template files with error handling
def load_template(path):
    """Load a template file with error handling."""
    if os.path.exists(path):
        template = cv2.imread(path, 0)
        if template is not None:
            return template
    print(f"[WARN] Failed to load template: {path}")
    return None

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = load_template('assets/minimap_tl_template.png')
MM_BR_TEMPLATE = load_template('assets/minimap_br_template.png')

# Set default dimensions if templates failed to load
if MM_TL_TEMPLATE is not None and MM_BR_TEMPLATE is not None:
    MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
    MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])
else:
    MMT_HEIGHT = 50  # Default fallback
    MMT_WIDTH = 50   # Default fallback

# The player's symbol on the minimap
PLAYER_TEMPLATE = load_template('assets/player_template.png')
if PLAYER_TEMPLATE is not None:
    PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape
else:
    PT_HEIGHT, PT_WIDTH = 10, 10  # Default fallback


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
        # Check for saved window configuration FIRST (from automation tools)
        saved_config = self._load_saved_window_config()
        if saved_config:
            print(f"[INFO] Using saved window config: {saved_config}")
            # Disable manual window position since we have automated config
            if hasattr(config, 'settings'):
                config.settings.use_manual_window_position = False
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
        # Check if templates are available
        if MM_TL_TEMPLATE is None or MM_BR_TEMPLATE is None:
            print("[INFO] Minimap templates not available, skipping template-based detection")
            return None
            
        try:
            with mss.mss() as sct:
                # Try each monitor individually for better results on multi-monitor setups
                for monitor_idx, monitor in enumerate(sct.monitors):
                    if monitor_idx == 0:  # Skip monitor 0 (all monitors combined)
                        continue
                        
                    print(f"[INFO] Searching for MapleStory window on monitor {monitor_idx}")
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)
                    
                    # Convert from BGRA to BGR if needed
                    if frame.shape[2] == 4:
                        frame = frame[:, :, :3]
                    
                    # Use multi-scale template matching for better results
                    tl_matches = utils.multi_scale_match(frame, MM_TL_TEMPLATE, threshold=0.7)
                    br_matches = utils.multi_scale_match(frame, MM_BR_TEMPLATE, threshold=0.7)
                    
                    print(f"[DEBUG] Found {len(tl_matches)} TL matches and {len(br_matches)} BR matches on monitor {monitor_idx}")
                    
                    if tl_matches and br_matches:
                        # Find the best pair of corners
                        best_window = None
                        best_score = 0
                        
                        for tl in tl_matches:
                            tl_x, tl_y, tl_scale, tl_conf = tl
                            
                            for br in br_matches:
                                br_x, br_y, br_scale, br_conf = br
                                
                                # Skip if scales are too different (should be similar)
                                if abs(tl_scale - br_scale) > 0.2:
                                    continue
                                    
                                # Calculate window dimensions
                                left = max(0, tl_x - int(50 * tl_scale))  # Add margin scaled by template scale
                                top = max(0, tl_y - int(50 * tl_scale))
                                right = min(frame.shape[1], br_x + int(50 * br_scale))
                                bottom = min(frame.shape[0], br_y + int(50 * br_scale))
                                
                                # Validate reasonable window size and position
                                width = right - left
                                height = bottom - top
                                
                                # Skip if TL is below or to the right of BR
                                if tl_x >= br_x or tl_y >= br_y:
                                    continue
                                
                                # Validate reasonable window size (scaled by template scale)
                                min_width = 800 * min(tl_scale, br_scale)
                                max_width = 3000 * max(tl_scale, br_scale)
                                min_height = 600 * min(tl_scale, br_scale)
                                max_height = 2000 * max(tl_scale, br_scale)
                                
                                if min_width <= width <= max_width and min_height <= height <= max_height:
                                    # Calculate score based on confidence and distance
                                    conf_score = (tl_conf + br_conf) / 2
                                    distance_score = utils.distance((tl_x, tl_y), (br_x, br_y))
                                    score = conf_score * distance_score
                                    
                                    if score > best_score:
                                        best_score = score
                                        # Adjust for monitor position
                                        best_window = (
                                            left + monitor['left'],
                                            top + monitor['top'],
                                            right + monitor['left'],
                                            bottom + monitor['top']
                                        )
                        
                        if best_window:
                            print(f"[INFO] Found MapleStory window by template on monitor {monitor_idx}: {best_window}")
                            # Save the window config for future use
                            self._save_window_config({
                                'left': best_window[0],
                                'top': best_window[1],
                                'width': best_window[2] - best_window[0],
                                'height': best_window[3] - best_window[1],
                                'monitor_idx': monitor_idx
                            })
                            return best_window
                
                # If we get here, try one more time with all monitors combined
                print("[INFO] Trying template detection on all monitors combined")
                screenshot = sct.grab(sct.monitors[0])
                frame = np.array(screenshot)
                
                # Convert from BGRA to BGR if needed
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                
                # Use multi-scale template matching
                tl_matches = utils.multi_scale_match(frame, MM_TL_TEMPLATE, threshold=0.7)
                br_matches = utils.multi_scale_match(frame, MM_BR_TEMPLATE, threshold=0.7)
                
                print(f"[DEBUG] Found {len(tl_matches)} TL matches and {len(br_matches)} BR matches on combined display")
                
                if tl_matches and br_matches:
                    # Find the best pair of corners
                    best_window = None
                    best_score = 0
                    
                    for tl in tl_matches:
                        tl_x, tl_y, tl_scale, tl_conf = tl
                        
                        for br in br_matches:
                            br_x, br_y, br_scale, br_conf = br
                            
                            # Skip if scales are too different
                            if abs(tl_scale - br_scale) > 0.2:
                                continue
                                
                            # Skip if TL is below or to the right of BR
                            if tl_x >= br_x or tl_y >= br_y:
                                continue
                            
                            # Calculate window dimensions
                            left = max(0, tl_x - int(50 * tl_scale))
                            top = max(0, tl_y - int(50 * tl_scale))
                            right = min(frame.shape[1], br_x + int(50 * br_scale))
                            bottom = min(frame.shape[0], br_y + int(50 * br_scale))
                            
                            width = right - left
                            height = bottom - top
                            
                            # Validate reasonable window size
                            min_width = 800 * min(tl_scale, br_scale)
                            max_width = 3000 * max(tl_scale, br_scale)
                            min_height = 600 * min(tl_scale, br_scale)
                            max_height = 2000 * max(tl_scale, br_scale)
                            
                            if min_width <= width <= max_width and min_height <= height <= max_height:
                                # Calculate score
                                conf_score = (tl_conf + br_conf) / 2
                                distance_score = utils.distance((tl_x, tl_y), (br_x, br_y))
                                score = conf_score * distance_score
                                
                                if score > best_score:
                                    best_score = score
                                    best_window = (left, top, right, bottom)
                    
                    if best_window:
                        print(f"[INFO] Found MapleStory window by template on combined display: {best_window}")
                        # Save the window config
                        self._save_window_config({
                            'left': best_window[0],
                            'top': best_window[1],
                            'width': best_window[2] - best_window[0],
                            'height': best_window[3] - best_window[1],
                            'monitor_idx': 0
                        })
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

        calibration_attempts = 0
        max_calibration_attempts = 3
        
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
                calibration_attempts += 1
                print(f"[INFO] Minimap calibration attempt {calibration_attempts}/{max_calibration_attempts}")
                
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
                        calibration_attempts = 0  # Reset counter on success
                        print(f"[INFO] Minimap calibrated using manual config: TL={mm_tl}, BR={mm_br}, ratio={self.minimap_ratio:.2f}")
                    else:
                        print(f"[WARN] Manual minimap coordinates are outside window bounds: TL={mm_tl}, BR={mm_br}, window={self.window}")
                        manual_mm_config = None  # Fall back to template detection
                elif MM_TL_TEMPLATE is not None and MM_BR_TEMPLATE is not None:
                    # Fall back to template-based detection with multi-scale matching
                    try:
                        # Use multi-scale template matching for better results
                        tl_match = utils.find_best_match(self.frame, MM_TL_TEMPLATE, threshold=0.7)
                        br_match = utils.find_best_match(self.frame, MM_BR_TEMPLATE, threshold=0.7)
                        
                        if tl_match and br_match:
                            tl_x, tl_y, tl_scale, _ = tl_match
                            br_x, br_y, br_scale, _ = br_match
                            
                            # Calculate minimap borders scaled by template scale
                            top_border = int(MINIMAP_TOP_BORDER * tl_scale)
                            bottom_border = int(MINIMAP_BOTTOM_BORDER * br_scale)
                            
                            mm_tl = (
                                tl_x + bottom_border,
                                tl_y + top_border
                            )
                            mm_br = (
                                max(mm_tl[0] + PT_WIDTH, br_x - bottom_border),
                                max(mm_tl[1] + PT_HEIGHT, br_y - bottom_border)
                            )
                            
                            # Validate minimap dimensions
                            minimap_width = mm_br[0] - mm_tl[0]
                            minimap_height = mm_br[1] - mm_tl[1]
                            
                            if minimap_width > 0 and minimap_height > 0:
                                self.minimap_ratio = minimap_width / minimap_height
                                self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                                self.calibrated = True
                                calibration_attempts = 0  # Reset counter on success
                                print(f"[INFO] Minimap calibrated using multi-scale templates: TL={mm_tl}, BR={mm_br}, ratio={self.minimap_ratio:.2f}")
                                
                                # Save the minimap configuration for future use (convert to absolute coordinates)
                                self._save_minimap_config({
                                    'mm_left': mm_tl[0] + self.window['left'],    # Convert to absolute
                                    'mm_top': mm_tl[1] + self.window['top'],      # Convert to absolute
                                    'mm_right': mm_br[0] + self.window['left'],   # Convert to absolute
                                    'mm_bottom': mm_br[1] + self.window['top']    # Convert to absolute
                                })
                            else:
                                print(f"[WARN] Invalid minimap dimensions: width={minimap_width}, height={minimap_height}")
                                self.calibrated = False
                        else:
                            print("[WARN] Could not find minimap corners using multi-scale template matching")
                            self.calibrated = False
                    except Exception as e:
                        print(f"[WARN] Template-based minimap calibration failed: {e}")
                        self.calibrated = False
                        time.sleep(1)
                        continue
                else:
                    # No templates available, use fallback minimap area
                    print("[INFO] No minimap templates available, using fallback area")
                    # Use a reasonable area in the top-right corner for minimap
                    frame_height, frame_width = self.frame.shape[:2]
                    mm_tl = (frame_width - 200, 50)  # Top-right area
                    mm_br = (frame_width - 20, 200)   # Reasonable size
                    self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    self.calibrated = True
                    calibration_attempts = 0  # Reset counter on success
                    print(f"[INFO] Using fallback minimap area: TL={mm_tl}, BR={mm_br}")
            except Exception as e:
                print(f"[WARN] Minimap calibration failed: {e}")
                self.calibrated = False
                
                if calibration_attempts >= max_calibration_attempts:
                    print(f"[ERROR] Failed to calibrate minimap after {max_calibration_attempts} attempts. Using fallback mode.")
                    # Use a basic fallback - center area of the screen
                    frame_height, frame_width = self.frame.shape[:2]
                    mm_tl = (frame_width - 200, 50)  
                    mm_br = (frame_width - 20, 200)
                    self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    self.calibrated = True
                    print(f"[INFO] Using emergency fallback minimap area: TL={mm_tl}, BR={mm_br}")
                else:
                    time.sleep(2)
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
                        
                        if minimap.size == 0:
                            print("[WARN] Empty minimap region, recalibrating...")
                            print(f"[DEBUG] Minimap coordinates: TL={mm_tl}, BR={mm_br}")
                            print(f"[DEBUG] Window: {self.window}")
                            print(f"[DEBUG] Frame shape: {self.frame.shape if self.frame is not None else 'None'}")
                            self.calibrated = False
                            time.sleep(2)  # Add delay to prevent rapid recalibration
                            break

                        # Determine the player's position using template matching
                        if PLAYER_TEMPLATE is not None:
                            # Use template matching with our perfect templates
                            player_matches = utils.multi_scale_match(minimap, PLAYER_TEMPLATE, threshold=0.7)
                            if player_matches:
                                player_x, player_y, _, _ = player_matches[0]
                                config.player_pos = utils.convert_to_relative((player_x, player_y), minimap)
                            else:
                                # Use center as fallback
                                minimap_height, minimap_width = minimap.shape[:2]
                                center_pos = (minimap_width // 2, minimap_height // 2)
                                config.player_pos = utils.convert_to_relative(center_pos, minimap)
                        else:
                            # No player template available, use center of minimap as fallback
                            minimap_height, minimap_width = minimap.shape[:2]
                            center_pos = (minimap_width // 2, minimap_height // 2)
                            config.player_pos = utils.convert_to_relative(center_pos, minimap)
                            print("[DEBUG] No player template available, using minimap center")

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
                        self.calibrated = False
                        break

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

    def _save_window_config(self, config_data):
        """Save window configuration to file for future use."""
        try:
            import json
            import os
            
            config_file = "window_config.json"
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"[INFO] Saved window configuration to {config_file}")
        except Exception as e:
            print(f"[WARN] Failed to save window config: {e}")
            
        return config_data

    def _save_minimap_config(self, config_data):
        """Save minimap configuration to file for future use."""
        try:
            import json
            import os
            
            config_file = "minimap_config.json"
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"[INFO] Saved minimap configuration to {config_file}")
        except Exception as e:
            print(f"[WARN] Failed to save minimap config: {e}")
            
        return config_data
