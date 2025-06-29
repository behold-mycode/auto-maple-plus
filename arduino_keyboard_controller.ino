/*
 * Arduino Leonardo Keyboard Controller for Auto Maple
 * 
 * This sketch turns an Arduino Leonardo into a USB HID keyboard that receives
 * commands from the Python bot over serial and sends actual keystrokes.
 * 
 * Hardware Requirements:
 * - Arduino Leonardo (or any Arduino with ATmega32u4 that supports USB HID)
 * 
 * Usage:
 * 1. Upload this sketch to your Arduino Leonardo
 * 2. Connect Arduino to your computer via USB
 * 3. The Python bot will send commands over serial to control keyboard input
 * 
 * Command Format:
 * - "p<code>\n" - Press key with DirectInput scan code
 * - "r<code>\n" - Release key with DirectInput scan code
 * 
 * Example:
 * - "p208\n" - Press Down Arrow key (scan code 0xD0 = 208)
 * - "r208\n" - Release Down Arrow key
 */

#include <Keyboard.h>

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Initialize keyboard
  Keyboard.begin();
  
  // Optional: wait for serial connection (uncomment if needed)
  // while (!Serial) { delay(10); }
  
  Serial.println("Arduino Keyboard Controller Ready");
}

void loop() {
  // Read commands from serial
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    
    if (command.length() < 2) {
      return; // Ignore if too short to contain command type and code
    }
    
    char cmdType = command.charAt(0);
    int keyCode = command.substring(1).toInt(); // Parse the numeric part
    
    // Map DirectInput scan codes to actual keys
    if (cmdType == 'p') { // Press key
      switch (keyCode) {
        // Letters (A-Z):
        case 0x10: Keyboard.press('Q'); break;
        case 0x11: Keyboard.press('W'); break;
        case 0x12: Keyboard.press('E'); break;
        case 0x13: Keyboard.press('R'); break;
        case 0x14: Keyboard.press('T'); break;
        case 0x15: Keyboard.press('Y'); break;
        case 0x16: Keyboard.press('U'); break;
        case 0x17: Keyboard.press('I'); break;
        case 0x18: Keyboard.press('O'); break;
        case 0x19: Keyboard.press('P'); break;
        case 0x1E: Keyboard.press('A'); break;
        case 0x1F: Keyboard.press('S'); break;
        case 0x20: Keyboard.press('D'); break;
        case 0x21: Keyboard.press('F'); break;
        case 0x22: Keyboard.press('G'); break;
        case 0x23: Keyboard.press('H'); break;
        case 0x24: Keyboard.press('J'); break;
        case 0x25: Keyboard.press('K'); break;
        case 0x26: Keyboard.press('L'); break;
        case 0x2C: Keyboard.press('Z'); break;
        case 0x2D: Keyboard.press('X'); break;
        case 0x2E: Keyboard.press('C'); break;
        case 0x2F: Keyboard.press('V'); break;
        case 0x30: Keyboard.press('B'); break;
        case 0x31: Keyboard.press('N'); break;
        case 0x32: Keyboard.press('M'); break;
        
        // Number keys (0-9):
        case 0x02: Keyboard.press('1'); break;
        case 0x03: Keyboard.press('2'); break;
        case 0x04: Keyboard.press('3'); break;
        case 0x05: Keyboard.press('4'); break;
        case 0x06: Keyboard.press('5'); break;
        case 0x07: Keyboard.press('6'); break;
        case 0x08: Keyboard.press('7'); break;
        case 0x09: Keyboard.press('8'); break;
        case 0x0A: Keyboard.press('9'); break;
        case 0x0B: Keyboard.press('0'); break;
        case 0x0C: Keyboard.press('-'); break;
        case 0x0D: Keyboard.press('='); break;
        
        // Whitespace/utility keys:
        case 0x39: Keyboard.press(' '); break; // spacebar
        case 0x0F: Keyboard.press(KEY_TAB); break; // tab key
        case 0x0E: Keyboard.press(KEY_BACKSPACE); break; // backspace
        case 0x1C: // Enter (main keyboard)
        case 0x9C: Keyboard.press(KEY_RETURN); break; // Enter (numeric keypad)
        
        // Modifier keys:
        case 0x1D: Keyboard.press(KEY_LEFT_CTRL); break; // Left Ctrl
        case 0x2A: Keyboard.press(KEY_LEFT_SHIFT); break; // Left Shift
        case 0x36: Keyboard.press(KEY_RIGHT_SHIFT); break; // Right Shift
        case 0x38: Keyboard.press(KEY_LEFT_ALT); break; // Left Alt
        case 0xB8: Keyboard.press(KEY_RIGHT_ALT); break; // Right Alt
        
        // Arrow keys:
        case 0xC8: Keyboard.press(KEY_UP_ARROW); break;
        case 0xD0: Keyboard.press(KEY_DOWN_ARROW); break;
        case 0xCB: Keyboard.press(KEY_LEFT_ARROW); break;
        case 0xCD: Keyboard.press(KEY_RIGHT_ARROW); break;
        
        // Function keys (F1-F12):
        case 0x3B: Keyboard.press(KEY_F1); break;
        case 0x3C: Keyboard.press(KEY_F2); break;
        case 0x3D: Keyboard.press(KEY_F3); break;
        case 0x3E: Keyboard.press(KEY_F4); break;
        case 0x3F: Keyboard.press(KEY_F5); break;
        case 0x40: Keyboard.press(KEY_F6); break;
        case 0x41: Keyboard.press(KEY_F7); break;
        case 0x42: Keyboard.press(KEY_F8); break;
        case 0x43: Keyboard.press(KEY_F9); break;
        case 0x44: Keyboard.press(KEY_F10); break;
        case 0x57: Keyboard.press(KEY_F11); break;
        case 0x58: Keyboard.press(KEY_F12); break;
        
        // Special keys:
        case 0x01: Keyboard.press(KEY_ESC); break; // Escape
        case 0x29: Keyboard.press('`'); break; // Backtick
        
        default:
          // Unknown key code, ignore
          break;
      }
    }
    else if (cmdType == 'r') { // Release key
      switch (keyCode) {
        // Letters:
        case 0x10: Keyboard.release('Q'); break;
        case 0x11: Keyboard.release('W'); break;
        case 0x12: Keyboard.release('E'); break;
        case 0x13: Keyboard.release('R'); break;
        case 0x14: Keyboard.release('T'); break;
        case 0x15: Keyboard.release('Y'); break;
        case 0x16: Keyboard.release('U'); break;
        case 0x17: Keyboard.release('I'); break;
        case 0x18: Keyboard.release('O'); break;
        case 0x19: Keyboard.release('P'); break;
        case 0x1E: Keyboard.release('A'); break;
        case 0x1F: Keyboard.release('S'); break;
        case 0x20: Keyboard.release('D'); break;
        case 0x21: Keyboard.release('F'); break;
        case 0x22: Keyboard.release('G'); break;
        case 0x23: Keyboard.release('H'); break;
        case 0x24: Keyboard.release('J'); break;
        case 0x25: Keyboard.release('K'); break;
        case 0x26: Keyboard.release('L'); break;
        case 0x2C: Keyboard.release('Z'); break;
        case 0x2D: Keyboard.release('X'); break;
        case 0x2E: Keyboard.release('C'); break;
        case 0x2F: Keyboard.release('V'); break;
        case 0x30: Keyboard.release('B'); break;
        case 0x31: Keyboard.release('N'); break;
        case 0x32: Keyboard.release('M'); break;
        
        // Numbers and symbols:
        case 0x02: Keyboard.release('1'); break;
        case 0x03: Keyboard.release('2'); break;
        case 0x04: Keyboard.release('3'); break;
        case 0x05: Keyboard.release('4'); break;
        case 0x06: Keyboard.release('5'); break;
        case 0x07: Keyboard.release('6'); break;
        case 0x08: Keyboard.release('7'); break;
        case 0x09: Keyboard.release('8'); break;
        case 0x0A: Keyboard.release('9'); break;
        case 0x0B: Keyboard.release('0'); break;
        case 0x0C: Keyboard.release('-'); break;
        case 0x0D: Keyboard.release('='); break;
        
        // Whitespace/utility:
        case 0x39: Keyboard.release(' '); break;
        case 0x0F: Keyboard.release(KEY_TAB); break;
        case 0x0E: Keyboard.release(KEY_BACKSPACE); break;
        case 0x1C:
        case 0x9C: Keyboard.release(KEY_RETURN); break;
        
        // Modifiers:
        case 0x1D: Keyboard.release(KEY_LEFT_CTRL); break;
        case 0x2A: Keyboard.release(KEY_LEFT_SHIFT); break;
        case 0x36: Keyboard.release(KEY_RIGHT_SHIFT); break;
        case 0x38: Keyboard.release(KEY_LEFT_ALT); break;
        case 0xB8: Keyboard.release(KEY_RIGHT_ALT); break;
        
        // Arrows:
        case 0xC8: Keyboard.release(KEY_UP_ARROW); break;
        case 0xD0: Keyboard.release(KEY_DOWN_ARROW); break;
        case 0xCB: Keyboard.release(KEY_LEFT_ARROW); break;
        case 0xCD: Keyboard.release(KEY_RIGHT_ARROW); break;
        
        // Function keys:
        case 0x3B: Keyboard.release(KEY_F1); break;
        case 0x3C: Keyboard.release(KEY_F2); break;
        case 0x3D: Keyboard.release(KEY_F3); break;
        case 0x3E: Keyboard.release(KEY_F4); break;
        case 0x3F: Keyboard.release(KEY_F5); break;
        case 0x40: Keyboard.release(KEY_F6); break;
        case 0x41: Keyboard.release(KEY_F7); break;
        case 0x42: Keyboard.release(KEY_F8); break;
        case 0x43: Keyboard.release(KEY_F9); break;
        case 0x44: Keyboard.release(KEY_F10); break;
        case 0x57: Keyboard.release(KEY_F11); break;
        case 0x58: Keyboard.release(KEY_F12); break;
        
        // Special keys:
        case 0x01: Keyboard.release(KEY_ESC); break;
        case 0x29: Keyboard.release('`'); break;
        
        default:
          // Unknown code, ignore
          break;
      }
    }
  }
} 