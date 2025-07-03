"""
Virtual key input module using ONLY Arduino-based input.
All keyboard input goes through Arduino Leonardo acting as USB HID keyboard.
"""

import time
from .arduino_input import get_arduino_input

def press(key: str, duration: float = 0.1, down_time: float = None, up_time: float = None):
    """
    Press a key for a specified duration using Arduino ONLY.
    
    Args:
        key: The key to press (string representation)
        duration: How long to hold the key in seconds
        down_time: Legacy parameter (ignored)
        up_time: Legacy parameter (ignored)
    """
    arduino = get_arduino_input()
    arduino.press(key, duration)

def key_down(key: str):
    """
    Press down a key (without releasing) using Arduino ONLY.
    
    Args:
        key: The key to press down
    """
    arduino = get_arduino_input()
    return arduino.key_down(key)

def key_up(key: str):
    """
    Release a key using Arduino ONLY.
    
    Args:
        key: The key to release
    """
    arduino = get_arduino_input()
    return arduino.key_up(key)

def is_pressed(key: str) -> bool:
    """
    Arduino input doesn't support key state checking.
    Always returns False for compatibility.
    
    Args:
        key: The key to check
        
    Returns:
        Always False (Arduino doesn't support this)
    """
    print(f"[INFO] Arduino input doesn't support is_pressed for key '{key}', returning False")
    return False 