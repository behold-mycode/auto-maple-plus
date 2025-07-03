"""
Keyboard listener module for bot control hotkeys.
Game input uses Arduino-only, but system hotkeys (F4, F5, etc.) use system keyboard detection.
"""

import sys
import time
import threading
import platform
from src.common import config, utils
from src.common.interfaces import Configurable
from datetime import datetime

# Cross-platform keyboard input handling for HOTKEYS ONLY
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


class Listener(Configurable):
    DEFAULT_CONFIG = {
        'Start/stop': 'f4',
        'Recalibrate Minimap': 'f5',
        'Reload routine': 'f6',
        'Record position': 'f7'
    }
    BLOCK_DELAY = 1         # Delay after blocking restricted button press

    def __init__(self):
        """Initializes this Listener object's main thread for hotkey detection."""

        super().__init__('controls')
        config.listener = self

        self.enabled = False
        self.ready = False
        self.block_time = 0
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True
        
        # Cross-platform keyboard setup for HOTKEYS ONLY
        self.key_states = {}
        if platform.system() == "Darwin" and KEYBOARD_AVAILABLE:
            # macOS: Use pynput for keyboard listening
            self.listener = kb_listener.Listener(on_press=self._on_press, on_release=self._on_release)
            self.listener.start()
        elif not KEYBOARD_AVAILABLE:
            print("[WARN] No keyboard library available for hotkeys. Hotkeys will be disabled.")

        print("[INFO] Keyboard listener enabled for hotkeys (F4, F5, F6, F7)")
        print("[INFO] Game input uses Arduino-only mode")

    def _on_press(self, key):
        """Handle key press events (macOS) for hotkeys only."""
        # Normalize key object into comparable string (e.g. 'f4', 'space', 'a')
        key_name = None
        # Alphanumeric & symbol keys – have .char attribute
        if hasattr(key, 'char') and key.char is not None:
            key_name = key.char.lower()
        else:
            # Special keys – use .name if available, otherwise strip 'Key.'
            try:
                key_name = key.name.lower()
            except AttributeError:
                key_name = str(key).replace('Key.', '').lower()

        # Store state
        if key_name:
            self.key_states[key_name] = True

    def _on_release(self, key):
        """Handle key release events (macOS) for hotkeys only."""
        # Same normalisation as _on_press
        key_name = None
        if hasattr(key, 'char') and key.char is not None:
            key_name = key.char.lower()
        else:
            try:
                key_name = key.name.lower()
            except AttributeError:
                key_name = str(key).replace('Key.', '').lower()

        if key_name:
            self.key_states[key_name] = False

    def is_pressed(self, key):
        """Cross-platform key press detection for hotkeys only."""
        if platform.system() == "Darwin" and KEYBOARD_AVAILABLE:
            # macOS: Check key states with normalized lookup
            return self.key_states.get(key.lower(), False)
        elif KEYBOARD_AVAILABLE:
            # Windows/Linux: Use keyboard library
            return kb.is_pressed(key)
        return False

    def start(self):
        """
        Starts listening to user inputs for hotkeys.
        :return:    None
        """

        print('\n[~] Started keyboard listener (hotkeys enabled, game input via Arduino)')
        self.thread.start()

    def _main(self):
        """
        Constantly listens for user inputs and updates variables in config accordingly.
        :return:    None
        """

        self.ready = True
        while True:
            if self.enabled:
                if self.is_pressed(self.config['Start/stop']):
                    Listener.toggle_enabled()
                elif self.is_pressed(self.config['Recalibrate Minimap']):
                    Listener.recalibrate_minimap()
                elif self.is_pressed(self.config['Reload routine']):
                    Listener.reload_routine()
                elif self.restricted_pressed('Record position'):
                    Listener.record_position()
            time.sleep(0.01)

    def restricted_pressed(self, action):
        """Returns whether the key bound to ACTION is pressed only if the bot is disabled."""

        if self.is_pressed(self.config[action]):
            if not config.enabled:
                return True
            now = time.time()
            if now - self.block_time > Listener.BLOCK_DELAY:
                print(f"\n[!] Cannot use '{action}' while Auto Maple is enabled")
                self.block_time = now
        return False

    @staticmethod
    def toggle_enabled():
        """Resumes or pauses the current routine. Plays a sound to notify the user."""

        config.bot.rune_active = False

        if not config.enabled:
            Listener.recalibrate_minimap()      # Recalibrate only when being enabled.

        config.enabled = not config.enabled
        config.gui.root.after(0, config.gui.view.monitoringconsole.set_enabledstat, config.enabled)
        utils.print_state()

        # Cross-platform sound
        if platform.system() == "Darwin":  # macOS
            try:
                import subprocess
                if config.enabled:
                    subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
                else:
                    subprocess.run(['afplay', '/System/Library/Sounds/Basso.aiff'])
            except:
                pass
        else:  # Windows/Linux
            try:
                import winsound
                if config.enabled:
                    winsound.Beep(784, 333)     # G5
                else:
                    winsound.Beep(523, 333)     # C5
            except:
                pass
        time.sleep(0.267)

    @staticmethod
    def reload_routine():
        Listener.recalibrate_minimap()

        config.routine.load(config.routine.path)

        # Cross-platform sound
        if platform.system() == "Darwin":  # macOS
            try:
                import subprocess
                subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
                time.sleep(0.2)
                subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
                time.sleep(0.2)
                subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
            except:
                pass
        else:  # Windows/Linux
            try:
                import winsound
                winsound.Beep(523, 200)     # C5
                winsound.Beep(659, 200)     # E5
                winsound.Beep(784, 200)     # G5
            except:
                pass

    @staticmethod
    def recalibrate_minimap():
        config.capture.calibrated = False
        while not config.capture.calibrated:
            time.sleep(0.01)
        config.gui.root.after(0, config.gui.edit.minimap.redraw)

    @staticmethod
    def record_position():
        """Records the current position and displays a message to the user."""

        try:
            curr_cb = config.bot.command_book.name if config.bot and hasattr(config.bot, 'command_book') else None
            if curr_cb:
                curr_layout = config.layout
                if curr_layout:
                    curr_pos = config.player_pos
                    curr_time = time.strftime('%H:%M:%S')

                    curr_layout.add(*curr_pos)
                    config.gui.root.after(0, config.gui.edit.record.add_entry, curr_time, curr_pos)
                    print(f"\n[~] Recorded new position: ({curr_pos[0]}, {curr_pos[1]})")
                else:
                    print(f"\n[!] Cannot record position: no layout loaded.")
            else:
                print(f"\n[!] Cannot record position: no command book loaded.")
        except Exception as e:
            print(f"\n[!] Error recording position: {e}")
