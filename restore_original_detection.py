#!/usr/bin/env python3
"""
Restore Original Detection Implementation
This script restores the original, simple, and reliable template matching system.
"""

import os
import shutil
from pathlib import Path

def backup_current_files():
    """Backup current files before making changes."""
    print("📦 Creating backups of current files...")
    
    files_to_backup = [
        'src/modules/capture.py',
        'src/common/utils.py'
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = file_path + '.backup'
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backed up {file_path} to {backup_path}")
        else:
            print(f"⚠️  File not found: {file_path}")

def restore_original_capture_py():
    """Restore the original capture.py implementation."""
    print("🔧 Restoring original capture.py...")
    
    original_capture = '''"""
A module that handles screen capture and image processing for the bot.
"""

import cv2
import mss
import numpy as np
import threading
import time
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

        print('\\n[~] Started video capture')
        self.thread.start()

    def _find_maple_window(self):
        """Find the MapleStory window using Windows API."""
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            
            # Find MapleStory window
            handle = user32.FindWindowW(None, 'MapleStory')
            if not handle:
                print("[WARN] Could not find MapleStory window")
                return (0, 0, 1366, 768)  # Default fallback
            
            # Get window rectangle
            rect = wintypes.RECT()
            user32.GetWindowRect(handle, ctypes.pointer(rect))
            rect = (rect.left, rect.top, rect.right, rect.bottom)
            
            # Ensure coordinates are non-negative
            rect = tuple(max(0, x) for x in rect)
            
            return rect
            
        except Exception as e:
            print(f"[WARN] Failed to find MapleStory window: {e}")
            return (0, 0, 1366, 768)  # Default fallback

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
                
                return img
                
        except Exception as e:
            print(f"[WARN] Screenshot failed: {e}")
            return None

    def _calibrate_minimap(self):
        """Calibrate the minimap by finding its corners using template matching."""
        
        try:
            # Find the top-left corner of the minimap
            tl, _ = utils.single_match(self.frame, MM_TL_TEMPLATE)
            if not tl:
                print("[WARN] Could not find minimap top-left corner")
                return False
            
            # Find the bottom-right corner of the minimap
            _, br = utils.single_match(self.frame, MM_BR_TEMPLATE)
            if not br:
                print("[WARN] Could not find minimap bottom-right corner")
                return False
            
            # Calculate minimap boundaries with borders
            mm_tl = (
                tl[0] + MINIMAP_BOTTOM_BORDER,
                tl[1] + MINIMAP_TOP_BORDER
            )
            mm_br = (
                max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
                max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
            )
            
            # Validate minimap dimensions
            minimap_width = mm_br[0] - mm_tl[0]
            minimap_height = mm_br[1] - mm_tl[1]
            
            if minimap_width > 0 and minimap_height > 0:
                self.minimap_ratio = minimap_width / minimap_height
                self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                self.calibrated = True
                print(f"[INFO] Minimap calibrated: TL={mm_tl}, BR={mm_br}, ratio={self.minimap_ratio:.2f}")
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
'''
    
    with open('src/modules/capture.py', 'w') as f:
        f.write(original_capture)
    
    print("✅ Restored original capture.py")

def restore_original_utils_py():
    """Restore the original utils.py implementation."""
    print("🔧 Restoring original utils.py...")
    
    # Read the current utils.py to preserve non-template matching functions
    with open('src/common/utils.py', 'r') as f:
        current_content = f.read()
    
    # Define the original template matching functions
    original_template_functions = '''
def single_match(frame, template, threshold=0.8):
    """
    Finds the best match of TEMPLATE in FRAME using template matching.
    :param frame:      The image to search in.
    :param template:   The template to search for.
    :param threshold:  The minimum similarity score to consider a match.
    :return:          The best match coordinates (x, y) or None if no match found.
    """
    
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        return max_loc
    return None


def multi_match(frame, template, threshold=0.8):
    """
    Finds all matches of TEMPLATE in FRAME above the given threshold.
    :param frame:      The image to search in.
    :param template:   The template to search for.
    :param threshold:  The minimum similarity score to consider a match.
    :return:          List of match coordinates [(x, y), ...].
    """
    
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    matches = list(zip(*locations[::-1]))  # Convert to (x, y) format
    
    return matches


def convert_to_relative(point, frame):
    """
    Converts POINT into relative coordinates (0-1) based on FRAME.
    :param point:   The point in absolute coordinates.
    :param frame:   The image to use as a reference.
    :return:        The given point in relative coordinates.
    """
    
    x = point[0] / frame.shape[1]
    y = point[1] / frame.shape[0]
    return x, y


def convert_to_absolute(point, frame):
    """
    Converts POINT into absolute coordinates (in pixels) based on FRAME.
    Normalizes the units of the vertical axis to equal those of the horizontal
    axis by using config.mm_ratio.
    :param point:   The point in relative coordinates.
    :param frame:   The image to use as a reference.
    :return:        The given point in absolute coordinates.
    """
    
    x = int(round(point[0] * frame.shape[1]))
    y = int(round(point[1] * config.capture.minimap_ratio * frame.shape[0]))
    return x, y


def draw_location(frame, point, color):
    """
    Draws a circle at POINT on FRAME in the given COLOR.
    :param frame:   The image to draw on.
    :param point:   The point to draw at (in relative coordinates).
    :param color:   The color to draw in (B, G, R).
    """
    
    x, y = convert_to_absolute(point, frame)
    cv2.circle(frame, (x, y), 3, color, -1)
'''
    
    # Replace the template matching functions in the current utils.py
    import re
    
    # Remove existing template matching functions
    patterns_to_remove = [
        r'def single_match\(.*?\):.*?(?=def|\Z)',
        r'def multi_match\(.*?\):.*?(?=def|\Z)',
        r'def multi_scale_match\(.*?\):.*?(?=def|\Z)',
        r'def find_best_match\(.*?\):.*?(?=def|\Z)',
        r'def convert_to_relative\(.*?\):.*?(?=def|\Z)',
        r'def convert_to_absolute\(.*?\):.*?(?=def|\Z)',
        r'def draw_location\(.*?\):.*?(?=def|\Z)'
    ]
    
    modified_content = current_content
    for pattern in patterns_to_remove:
        modified_content = re.sub(pattern, '', modified_content, flags=re.DOTALL)
    
    # Add the original template matching functions
    # Find the end of the file and add the functions there
    lines = modified_content.split('\\n')
    
    # Find where to insert (after imports and before other functions)
    insert_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') and not line.strip().startswith('def single_match'):
            insert_index = i
            break
    
    # Insert the original functions
    original_lines = original_template_functions.strip().split('\\n')
    lines[insert_index:insert_index] = [''] + original_lines + ['']
    
    # Write back to file
    with open('src/common/utils.py', 'w') as f:
        f.write('\\n'.join(lines))
    
    print("✅ Restored original template matching functions in utils.py")

def disable_manual_configuration():
    """Disable manual configuration to use original template detection."""
    print("🔧 Disabling manual configuration...")
    
    # Update settings.py to disable manual window position
    settings_file = "src/common/settings.py"
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Replace manual window position settings
        content = content.replace('use_manual_window_position = True', 'use_manual_window_position = False')
        content = content.replace('# Modified by window selector', '# Disabled - using original template detection')
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        print("✅ Disabled manual window position in settings.py")

def main():
    """Main restoration function."""
    print("🔄 RESTORING ORIGINAL TEMPLATE MATCHING SYSTEM")
    print("=" * 60)
    
    # Create backups
    backup_current_files()
    
    # Restore original implementations
    restore_original_capture_py()
    restore_original_utils_py()
    disable_manual_configuration()
    
    print("\\n✅ RESTORATION COMPLETE!")
    print("\\nThe original template matching system has been restored with:")
    print("• Simple, direct template loading")
    print("• Basic template matching (single_match, multi_match)")
    print("• High threshold (0.8) for reliable detection")
    print("• Windows API window detection")
    print("• Manual configuration disabled")
    print("\\nThe system should now work reliably with your fixed 1366x768 resolution.")

if __name__ == "__main__":
    main() 