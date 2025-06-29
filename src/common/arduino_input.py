"""
Arduino-based keyboard input module for cross-platform compatibility.
Replaces the Windows-specific interception library with Arduino HID keyboard emulation.
"""

import serial
import time
import platform
from typing import Optional
from . import settings


class ArduinoInput:
    """Handles keyboard input via Arduino Leonardo acting as a USB HID keyboard."""
    
    def __init__(self, port: Optional[str] = None, baud_rate: int = None):
        """
        Initialize Arduino input connection.
        
        Args:
            port: Serial port for Arduino (uses settings if None)
            baud_rate: Baud rate for serial communication (uses settings if None)
        """
        self.port = port or settings.arduino_port
        self.baud_rate = baud_rate or settings.arduino_baud
        self.serial_connection = None
        self.connected = False
        
        # Auto-detect port if not specified
        if self.port is None:
            self.port = self._auto_detect_port()
        
        self._connect()
    
    def _auto_detect_port(self) -> str:
        """Auto-detect Arduino port based on platform."""
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            # Common macOS Arduino ports
            possible_ports = [
                "/dev/tty.usbmodem*",
                "/dev/tty.usbserial*",
                "/dev/cu.usbmodem*",
                "/dev/cu.usbserial*"
            ]
            # For now, return a default - user should configure manually
            return "/dev/tty.usbmodem14101"  # Default, should be configurable
        elif system == "windows":
            return "COM3"  # Default Windows COM port
        elif system == "linux":
            return "/dev/ttyACM0"  # Default Linux port
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
    
    def _connect(self):
        """Establish serial connection to Arduino."""
        try:
            self.serial_connection = serial.Serial(
                self.port,
                self.baud_rate,
                timeout=1
            )
            self.connected = True
            print(f"[INFO] Connected to Arduino on {self.port}")
        except Exception as e:
            print(f"[ERROR] Could not open Arduino serial port {self.port}: {e}")
            self.connected = False
            self.serial_connection = None
    
    def _send_command(self, command: str):
        """Send a command to Arduino over serial."""
        if not self.connected or self.serial_connection is None:
            print(f"[WARN] Arduino not connected, command '{command}' ignored")
            return False
        
        try:
            cmd_bytes = f"{command}\n".encode('ascii')
            self.serial_connection.write(cmd_bytes)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send command '{command}': {e}")
            self.connected = False
            return False
    
    def press_key(self, key_code: int):
        """
        Press a key identified by its DirectInput scan code via Arduino.
        
        Args:
            key_code: DirectInput scan code for the key
        """
        command = f"p{key_code}"
        return self._send_command(command)
    
    def release_key(self, key_code: int):
        """
        Release a key identified by its DirectInput scan code via Arduino.
        
        Args:
            key_code: DirectInput scan code for the key
        """
        command = f"r{key_code}"
        return self._send_command(command)
    
    def press(self, key: str, duration: float = 0.1):
        """
        Press and release a key for a specified duration.
        This is a convenience method that maps common key names to scan codes.
        
        Args:
            key: Key name (e.g., 'a', 'space', 'enter', 'left', etc.)
            duration: How long to hold the key in seconds
        """
        # Map common key names to DirectInput scan codes
        key_mapping = {
            # Letters
            'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12,
            'f': 0x21, 'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24,
            'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31, 'o': 0x18,
            'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1F, 't': 0x14,
            'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D, 'y': 0x15,
            'z': 0x2C,
            
            # Numbers
            '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
            '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
            
            # Special keys
            'space': 0x39, 'enter': 0x1C, 'esc': 0x01, 'tab': 0x0F,
            'backspace': 0x0E, 'shift': 0x2A, 'ctrl': 0x1D, 'alt': 0x38,
            
            # Arrow keys
            'up': 0xC8, 'down': 0xD0, 'left': 0xCB, 'right': 0xCD,
            
            # Function keys
            'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E,
            'f5': 0x3F, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42,
            'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
            
            # Other symbols
            '-': 0x0C, '=': 0x0D, '`': 0x29,
        }
        
        # Convert key to lowercase for mapping
        key_lower = key.lower()
        
        if key_lower in key_mapping:
            scan_code = key_mapping[key_lower]
            self.press_key(scan_code)
            time.sleep(duration)
            self.release_key(scan_code)
        else:
            print(f"[WARN] Unknown key '{key}', cannot press")
    
    def key_down(self, key: str):
        """Hold down a key."""
        key_mapping = {
            # Letters
            'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12,
            'f': 0x21, 'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24,
            'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31, 'o': 0x18,
            'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1F, 't': 0x14,
            'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D, 'y': 0x15,
            'z': 0x2C,
            
            # Numbers
            '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
            '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
            
            # Special keys
            'space': 0x39, 'enter': 0x1C, 'esc': 0x01, 'tab': 0x0F,
            'backspace': 0x0E, 'shift': 0x2A, 'ctrl': 0x1D, 'alt': 0x38,
            
            # Arrow keys
            'up': 0xC8, 'down': 0xD0, 'left': 0xCB, 'right': 0xCD,
            
            # Function keys
            'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E,
            'f5': 0x3F, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42,
            'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
            
            # Other symbols
            '-': 0x0C, '=': 0x0D, '`': 0x29,
        }
        
        key_lower = key.lower()
        if key_lower in key_mapping:
            scan_code = key_mapping[key_lower]
            return self.press_key(scan_code)
        else:
            print(f"[WARN] Unknown key '{key}', cannot hold down")
            return False
    
    def key_up(self, key: str):
        """Release a key."""
        key_mapping = {
            # Letters
            'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12,
            'f': 0x21, 'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24,
            'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31, 'o': 0x18,
            'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1F, 't': 0x14,
            'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D, 'y': 0x15,
            'z': 0x2C,
            
            # Numbers
            '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
            '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
            
            # Special keys
            'space': 0x39, 'enter': 0x1C, 'esc': 0x01, 'tab': 0x0F,
            'backspace': 0x0E, 'shift': 0x2A, 'ctrl': 0x1D, 'alt': 0x38,
            
            # Arrow keys
            'up': 0xC8, 'down': 0xD0, 'left': 0xCB, 'right': 0xCD,
            
            # Function keys
            'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E,
            'f5': 0x3F, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42,
            'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
            
            # Other symbols
            '-': 0x0C, '=': 0x0D, '`': 0x29,
        }
        
        key_lower = key.lower()
        if key_lower in key_mapping:
            scan_code = key_mapping[key_lower]
            return self.release_key(scan_code)
        else:
            print(f"[WARN] Unknown key '{key}', cannot release")
            return False
    
    def close(self):
        """Close the serial connection."""
        if self.serial_connection:
            self.serial_connection.close()
            self.connected = False


# Global Arduino input instance
_arduino_input = None


def get_arduino_input() -> ArduinoInput:
    """Get the global Arduino input instance."""
    global _arduino_input
    if _arduino_input is None:
        _arduino_input = ArduinoInput()
    return _arduino_input


# Convenience functions that mirror the original interception API
def press(key: str, duration: float = 0.1):
    """Press and release a key (compatibility with original interception API)."""
    arduino = get_arduino_input()
    arduino.press(key, duration)


def key_down(key: str):
    """Hold down a key (compatibility with original interception API)."""
    arduino = get_arduino_input()
    return arduino.key_down(key)


def key_up(key: str):
    """Release a key (compatibility with original interception API)."""
    arduino = get_arduino_input()
    return arduino.key_up(key)


def PressKey(hex_key_code: int):
    """Press a key by DirectInput scan code (compatibility with original interception API)."""
    arduino = get_arduino_input()
    return arduino.press_key(hex_key_code)


def ReleaseKey(hex_key_code: int):
    """Release a key by DirectInput scan code (compatibility with original interception API)."""
    arduino = get_arduino_input()
    return arduino.release_key(hex_key_code) 