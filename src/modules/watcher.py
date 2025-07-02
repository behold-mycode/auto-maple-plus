"""A module for detecting and notifying the user of dangerous in-game events."""

from src.common import config, utils
import time
from datetime import datetime
import os
import cv2
import threading
import numpy as np
import platform
from src.routine.components import Point
from src.common import config
import sys
import os

# Add the project root to Python path to find resources
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from resources import watcher_scan_table

import mss
from src.gui.automation.main import AutomationParams
import src.modules.automation as automation

# Cross-platform keyboard input handling
if platform.system() == "Darwin":  # macOS
    try:
        import pynput
        from pynput import keyboard as kb_listener
        KEYBOARD_AVAILABLE = True
    except ImportError:
        print("[WARN] pynput not available on macOS. Install with: pip install pynput")
        KEYBOARD_AVAILABLE = False
else:
    try:
        import keyboard as kb
        KEYBOARD_AVAILABLE = True
    except ImportError:
        print("[WARN] keyboard library not available")
        KEYBOARD_AVAILABLE = False

# Load template files with error handling
def load_template_safe(path):
    """Load a template file with error handling."""
    if os.path.exists(path):
        template = cv2.imread(path, 0)  # Load as grayscale
        if template is not None:
            return template
    print(f"[WARN] Failed to load template: {path}")
    return None

# A rune's symbol on the minimap (direct template matching)
RUNE_TEMPLATE = load_template_safe('assets/rune_template.png')

# Other players' symbols on the minimap (direct template matching)
OTHER_TEMPLATE = load_template_safe('assets/other_template.png')

# The Elite Boss's warning sign
ELITE_TEMPLATE = cv2.imread('assets/elite_template.jpg', 0)

# Rune CD Templates
RUNE_CD1_TEMPLATE = cv2.imread('assets/runeCD.png', 0)
RUNE_CD2_TEMPLATE = cv2.imread('assets/runeCD2.png', 0)

# EXP Text as Chat Anchor
LOGIN_SCREEN = cv2.imread('assets/Login.png',0)
SECONDPW_SCREEN = cv2.imread('assets/2ndpwKB.png',0)

def get_alert_path(name):
    return os.path.join(Watcher.ALERTS_DIR, f'{name}.mp3')


class Watcher:
    ALERTS_DIR = os.path.join('assets', 'alerts')

    def __init__(self):
        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

        self.room_change_threshold = 0.9
        self.rune_alert_delay = 270         # 4.5 minutes

        self.detectionTable = {}

    def start(self):
        """Starts this Watcher's thread."""
        print('\n[~] Started watcher')
        self.thread.start()

    def _main(self):
        self.ready = True
        rune_start_time = time.time()
        std = watcher_scan_table.scan_table_dynamic
        detectionTable = {}
        for scanEntry in std:
            detectionTable[scanEntry] = ""
        sts = watcher_scan_table.scan_table_static
        charLocation_Last = None

        while True:
            # Wait for capture to be ready
            if not config.capture or not config.capture.ready:
                time.sleep(0.1)
                continue
                
            frame = config.capture.frame #entire screen
            if frame is None:
                time.sleep(0.1)
                continue
                
            height, width, _ = frame.shape
            
            # Check if minimap is available
            if not config.capture.minimap or 'minimap' not in config.capture.minimap:
                time.sleep(0.1)
                continue
                
            minimap = config.capture.minimap['minimap'] #minimap only
            if minimap is None or minimap.size == 0:
                time.sleep(0.1)
                continue

            #scans in this section only activate if bot is enabled
            if config.enabled:
                # Check for rune CD
                runeCD1 = utils.multi_match(frame, RUNE_CD1_TEMPLATE, threshold=0.85)
                runeCD2 = utils.multi_match(frame, RUNE_CD2_TEMPLATE, threshold=0.85)
                if len(runeCD1) > 0 or len(runeCD2) > 0:
                    config.rune_cd = True
                else:
                    config.rune_cd = False

                # Check for rune
                now = time.time()
                if not config.bot.rune_active:
                    if RUNE_TEMPLATE is not None:
                        # Use direct template matching with multi-scale for better detection
                        matches = utils.multi_scale_match(minimap, RUNE_TEMPLATE, threshold=0.7)
                        rune_start_time = now
                        if matches and config.routine.sequence:
                            abs_rune_pos = (matches[0][0], matches[0][1])
                            config.bot.rune_pos = utils.convert_to_relative(abs_rune_pos, minimap)
                            distances = list(map(distance_to_rune, config.routine.sequence))
                            index = np.argmin(distances)
                            config.bot.rune_closest_pos = config.routine[index].location
                            if config.rune_cd == False:
                                config.bot.rune_active = True
                                print(f"[INFO] Rune detected at {config.bot.rune_pos}")
                elif now - rune_start_time > self.rune_alert_delay:     # Alert if rune hasn't been solved
                    config.bot.rune_active = False

                # Update key stats into monitoring console
                if config.rune_cd:
                    config.gui.view.monitoringconsole.set_runecdstat("Cooling down...")
                elif not config.rune_cd:
                    config.gui.view.monitoringconsole.set_runecdstat("Ready to Solve")

                # Check for number of other players in map
                if OTHER_TEMPLATE is not None:
                    # Use direct template matching with multi-scale for better detection
                    others_matches = utils.multi_scale_match(minimap, OTHER_TEMPLATE, threshold=0.95)
                    others = len(others_matches)
                    if others > 1:
                        config.map_overcrowded = True
                        print(f"[INFO] {others} other players detected in map")
                    elif others <= 1:
                        config.map_overcrowded = False
                    config.gui.view.monitoringconsole.set_noOthers(str(others))
                else:
                    # Fallback if template is not available
                    config.map_overcrowded = False
                    config.gui.view.monitoringconsole.set_noOthers("0")

                # Scan against dynamic scan table
                for scanEntry in std:
                    params = std[scanEntry]
                    flagname = params.get("flag")
                    target = cv2.imread("assets/"+params.get("ImgName"),0)
                    matchCount = utils.multi_match(frame=frame, template=target, threshold=0.8)                   
                    if params.get("Invert") == "False":
                        if matchCount != []:
                            if detectionTable[scanEntry] == "":
                                detectionTable[scanEntry] = datetime.now()
                            else:
                                firstDetection = detectionTable[scanEntry]
                                if (datetime.now() - firstDetection).total_seconds() > int(params.get("Threshold")):
                                    setattr(config,flagname,True)

                        else:
                            detectionTable[scanEntry] = ""
                            setattr(config,flagname,False)
                    if params.get("Invert") == "True":
                        if matchCount == []:
                            if detectionTable[scanEntry] == "":
                                detectionTable[scanEntry] = datetime.now()
                            else:
                                firstDetection = detectionTable[scanEntry]
                                if (datetime.now() - firstDetection).total_seconds() > int(params.get("Threshold")):
                                    setattr(config,flagname,True)
                        else:
                            detectionTable[scanEntry] = ""
                            setattr(config,flagname,False)

                #scan for chat
                try:
                    game_window = config.capture.window
                    chatbox_window = {"top": game_window["top"] + game_window["height"] - 125, "left": game_window["left"] + 15, "width": 390, "height":100}
                    with mss.mss() as sct:
                        # The screen part to capture
                        output = "assets/chat.png"
                        sct_img = sct.grab(chatbox_window)
                        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                    img = cv2.imread("assets/chat.png")

                    #remove specifically achievements mega
                    noAchiv = cv2.bitwise_and(img,img,mask=cv2.bitwise_not(cv2.inRange(img, (255,255,220), (255,255,230))))

                    # set white range and threshold
                    lowcolor =(210,210,210) #gm chat color is dimmest at 210 210 210
                    highcolor = (255,255,255) #pure white
                    thresh = cv2.inRange(noAchiv, lowcolor, highcolor)
                    #count pixels ch. is 19 pixels
                    count = np.count_nonzero(thresh)
                    if count >= 80:
                        config.chatbox_msg = True
                    else:
                        config.chatbox_msg = False
                except:
                    print("scanforchat fail")

                #scan for stationary
                if charLocation_Last == None:
                    charLocation_Last = config.player_pos
                    charLocation_Time = datetime.now()
                if charLocation_Last != config.player_pos:
                    charLocation_Last = config.player_pos
                    charLocation_Time = datetime.now()
                    setattr(config,"player_stuck",False)
                if config.player_pos == charLocation_Last and (datetime.now()-charLocation_Time).total_seconds() > 15:
                    setattr(config,"player_stuck",True)
            

            try:
                config.gui.runtime_console.runtimeFlags.update_All_Flags()
            except:
                pass

            #scans below here activate regardless of bot enabled status
            #scan for login screens
            loginscreen = utils.multi_match(frame, LOGIN_SCREEN, 0.7)
            if loginscreen != []:
                autoLoginToggle = AutomationParams('Automation Settings').get("auto_login2FA_toggle")
                if autoLoginToggle:
                    automation.autoLogin()
            
            #scan for secondPW screens
            secondPWscreen = utils.multi_match(frame, SECONDPW_SCREEN, 0.8)
            if secondPWscreen != []:
                autosecondaryToggle = AutomationParams('Automation Settings').get("auto_2ndPW_toggle")
                if autosecondaryToggle:
                    automation.auto2ndPW()

            time.sleep(0.1)


    def _alert(self, name, volume=0.75):
        """
        Plays an alert to notify user of a dangerous event. Stops the alert
        once the key bound to 'Start/stop' is pressed.
        """

        config.enabled = False
        config.listener.enabled = False
        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play(-1)
        
        # Cross-platform key detection
        while True:
            if platform.system() == "Darwin" and KEYBOARD_AVAILABLE:
                # macOS: Use pynput key states
                if config.listener.key_states.get(config.listener.config['Start/stop'], False):
                    break
            elif KEYBOARD_AVAILABLE:
                # Windows/Linux: Use keyboard library
                if kb.is_pressed(config.listener.config['Start/stop']):
                    break
            else:
                # Fallback: wait for a fixed time
                time.sleep(5)
                break
            time.sleep(0.1)
            
        self.mixer.stop()
        time.sleep(2)
        config.listener.enabled = True

    def _ping(self, name, volume=0.5):
        """A quick notification for non-dangerous events."""

        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play()


#################################
#       Helper Functions        #
#################################
def distance_to_rune(point):
    """
    Calculates the distance from POINT to the rune.
    :param point:   The position to check.
    :return:        The distance from POINT to the rune, infinity if it is not a Point object.
    """

    if isinstance(point, Point):
        return utils.distance(config.bot.rune_pos, point.location)
    return float('inf')
