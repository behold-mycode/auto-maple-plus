"""
Virtual key input module for cross-platform keyboard control.
"""

import time
import platform
import threading
from typing import Optional

# Platform-specific imports
if platform.system() == "Darwin":  # macOS
    try:
        from pynput.keyboard import Key, Controller
        KEYBOARD_AVAILABLE = True
    except ImportError:
        KEYBOARD_AVAILABLE = False
        print("[WARN] pynput not available on macOS, keyboard input disabled")
else:
    try:
        import keyboard as kb
        KEYBOARD_AVAILABLE = True
    except ImportError:
        KEYBOARD_AVAILABLE = False
        print("[WARN] keyboard library not available, keyboard input disabled")

# Global keyboard controller
_keyboard_controller = None

def _get_keyboard_controller():
    """Get or create the keyboard controller."""
    global _keyboard_controller
    if _keyboard_controller is None and KEYBOARD_AVAILABLE:
        if platform.system() == "Darwin":
            _keyboard_controller = Controller()
        else:
            _keyboard_controller = True  # keyboard library doesn't need controller
    return _keyboard_controller

def press(key: str, duration: float = 0.1):
    """
    Press a key for a specified duration.
    
    Args:
        key: The key to press (string representation)
        duration: How long to hold the key in seconds
    """
    if not KEYBOARD_AVAILABLE:
        print(f"[WARN] Keyboard input disabled, cannot press {key}")
        return
        
    try:
        if platform.system() == "Darwin":
            controller = _get_keyboard_controller()
            if controller:
                # Convert string key to pynput Key if needed
                if hasattr(Key, key.upper()):
                    key_obj = getattr(Key, key.upper())
                else:
                    key_obj = key
                
                controller.press(key_obj)
                time.sleep(duration)
                controller.release(key_obj)
        else:
            # Windows/Linux using keyboard library
            kb.press_and_release(key)
            time.sleep(duration)
    except Exception as e:
        print(f"[WARN] Failed to press key {key}: {e}")

def key_down(key: str):
    """
    Press down a key (without releasing).
    
    Args:
        key: The key to press down
    """
    if not KEYBOARD_AVAILABLE:
        print(f"[WARN] Keyboard input disabled, cannot press down {key}")
        return
        
    try:
        if platform.system() == "Darwin":
            controller = _get_keyboard_controller()
            if controller:
                if hasattr(Key, key.upper()):
                    key_obj = getattr(Key, key.upper())
                else:
                    key_obj = key
                controller.press(key_obj)
        else:
            kb.press(key)
    except Exception as e:
        print(f"[WARN] Failed to press down key {key}: {e}")

def key_up(key: str):
    """
    Release a key.
    
    Args:
        key: The key to release
    """
    if not KEYBOARD_AVAILABLE:
        print(f"[WARN] Keyboard input disabled, cannot release {key}")
        return
        
    try:
        if platform.system() == "Darwin":
            controller = _get_keyboard_controller()
            if controller:
                if hasattr(Key, key.upper()):
                    key_obj = getattr(Key, key.upper())
                else:
                    key_obj = key
                controller.release(key_obj)
        else:
            kb.release(key)
    except Exception as e:
        print(f"[WARN] Failed to release key {key}: {e}")

def is_pressed(key: str) -> bool:
    """
    Check if a key is currently pressed.
    
    Args:
        key: The key to check
        
    Returns:
        True if the key is pressed, False otherwise
    """
    if not KEYBOARD_AVAILABLE:
        return False
        
    try:
        if platform.system() == "Darwin":
            # pynput doesn't have a direct is_pressed method
            # This is a simplified implementation
            return False
        else:
            return kb.is_pressed(key)
    except Exception as e:
        print(f"[WARN] Failed to check if key {key} is pressed: {e}")
        return False 