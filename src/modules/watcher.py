"""
A module for detecting in-game events and managing alerts. Uses automated template matching
to find specific patterns on screen and set corresponding config flags.
"""

import cv2
import os
import time
import threading
import numpy as np
from datetime import datetime
from src.common import config, utils
from resources import watcher_scan_table


#################################
#    Template Loading Helper   #
#################################
def load_template_safe(path):
    """Load a template file with error handling."""
    if os.path.exists(path):
        template = cv2.imread(path, 0)  # Load as grayscale
        if template is not None:
            return template.astype(np.uint8)
    print(f"[WARN] Failed to load template: {path}")
    return None


#################################
#       Template Loading        #
#################################
# Rune CD Templates for bot logic
RUNE_CD1_TEMPLATE = load_template_safe('assets/runeCD.png')
RUNE_CD2_TEMPLATE = load_template_safe('assets/runeCD2.png')

# Other watcher templates
ELITE_TEMPLATE = load_template_safe('assets/elite_template.jpg')
OTHER_TEMPLATE = load_template_safe('assets/other_template.png')


#################################
#      Utility Functions        #
#################################
def get_alert_path(name):
    """Returns the path to an alert with the given NAME."""
    return os.path.join(Watcher.ALERTS_DIR, f'{name}.mp3')


class Watcher:
    ALERTS_DIR = os.path.join('assets', 'alerts')
    
    def __init__(self):
        """Loads alert music and initializes this Watcher object's main thread."""
        config.watcher = self
        self.ready = False

    def start(self):
        """Starts this Watcher object's main thread."""
        print('\n[~] Starting watcher')
        t = threading.Thread(target=self._main, daemon=True)
        t.start()

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
            minimap = config.capture.minimap_sample

            #scans in this section only activate if bot is enabled
            if config.enabled:
                # Check for rune CD (keep this - needed for bot logic)
                runeCD1 = utils.multi_match(frame, RUNE_CD1_TEMPLATE, threshold=0.85)
                runeCD2 = utils.multi_match(frame, RUNE_CD2_TEMPLATE, threshold=0.85)
                if len(runeCD1) > 0 or len(runeCD2) > 0:
                    config.rune_cd = True
                else:
                    config.rune_cd = False

                # Update key stats into monitoring console
                if config.rune_cd:
                    config.gui.view.monitoringconsole.set_runecdstat("Cooling down...")
                elif not config.rune_cd:
                    config.gui.view.monitoringconsole.set_runecdstat("Ready to Solve")

                # Check for number of other players in map
                others_count = len(config.others_pos) if hasattr(config, 'others_pos') else 0
                if others_count > 1:
                    config.map_overcrowded = True
                else:
                    config.map_overcrowded = False
                config.gui.view.monitoringconsole.set_noOthers(str(others_count))

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

                # Check for static conditions
                for scanEntry in sts:
                    params = sts[scanEntry]
                    flagname = params.get("flag")
                    target = cv2.imread("assets/"+params.get("ImgName"),0)
                    matchCount = utils.multi_match(frame=frame, template=target, threshold=0.8)
                    if matchCount != []:
                        setattr(config,flagname,True)
                    else:
                        setattr(config,flagname,False)

                # Custom checks
                charLocation_Current = config.player_pos
                if charLocation_Last == charLocation_Current:
                    config.player_stuck = True
                else:
                    config.player_stuck = False
                charLocation_Last = charLocation_Current

            # Update GUI flags regardless of bot enabled state
            if hasattr(config, 'gui') and config.gui and hasattr(config.gui, 'runtime'):
                config.gui.runtime.runtimeFlags.update_All_Flags()

            time.sleep(0.1)

    def _alert(self, name, volume=0.75):
        """
        Plays an alert to notify user of a dangerous in-game event. Alerts are stored
        as .mp3 files in the /assets/alerts directory.
        :param name:    The name of the alert mp3 file, excluding the file extension.
        :param volume:  A float between 0 and 1 denoting the volume level.
        :return:        None
        """

        def play_on_repeat():
            for _ in range(3):
                self._ping(name, volume)
                time.sleep(1.3)

        if config.enabled:
            alert_path = get_alert_path(name)
            if os.path.isfile(alert_path):
                print(f'\n[!] Playing alert: "{name}"')
                thread = threading.Thread(target=play_on_repeat)
                thread.daemon = True
                thread.start()
            else:
                print(f'\n[!] Could not find alert: "{name}"')

    def _ping(self, name, volume=0.5):
        """
        Plays a short sound clip to notify user of an in-game event. Alerts are stored
        as .mp3 files in the /assets/alerts directory.
        :param name:    The name of the alert mp3 file, excluding the file extension.
        :param volume:  A float between 0 and 1 denoting the volume level.
        :return:        None
        """

        alert_path = get_alert_path(name)
        if os.path.isfile(alert_path):
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(alert_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play()
            except ImportError:
                print("[WARN] pygame not available for audio alerts")
            except Exception as e:
                print(f"[WARN] Could not play alert: {e}")
        else:
            print(f'\n[!] Could not find alert: "{name}"')
