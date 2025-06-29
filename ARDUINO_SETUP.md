# Arduino Keyboard Controller Setup Guide

This guide explains how to set up the Arduino Leonardo to act as a USB HID keyboard for Auto Maple, enabling cross-platform compatibility.

## Hardware Requirements

- **Arduino Leonardo** (or any Arduino with ATmega32u4 that supports USB HID)
- USB cable to connect Arduino to your computer
- Computer running macOS, Windows, or Linux

## Why Arduino?

The original Auto Maple used Windows-specific interception libraries that don't work on macOS or Linux. By using an Arduino Leonardo as a USB HID keyboard, we can send genuine hardware keystrokes that are indistinguishable from real keyboard input, making the bot work on any platform.

## Setup Instructions

### 1. Arduino Setup

1. **Connect your Arduino Leonardo** to your computer via USB
2. **Open Arduino IDE** and ensure your board is selected as "Arduino Leonardo"
3. **Open the sketch file** `arduino_keyboard_controller.ino`
4. **Upload the sketch** to your Arduino Leonardo
5. **Verify the upload** - you should see "Arduino Keyboard Controller Ready" in the Serial Monitor

### 2. Find Your Arduino Port

The Python bot needs to know which serial port your Arduino is connected to:

#### macOS:
```bash
ls /dev/tty.usbmodem*
ls /dev/cu.usbmodem*
```

#### Windows:
Check Device Manager > Ports (COM & LPT) for "Arduino Leonardo (COM#)"

#### Linux:
```bash
ls /dev/ttyACM*
```

### 3. Configure the Bot

Edit `src/common/settings.py` and set your Arduino port:

```python
# === Arduino Configuration ===
arduino_port = "/dev/tty.usbmodem14101"  # Replace with your actual port
arduino_baud = 115200
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

The requirements file has been cleaned up to remove Windows-specific dependencies and duplicates.

## How It Works

1. **Python Bot** sends commands over serial to Arduino
2. **Arduino** receives commands like "p208" (press key 208) or "r208" (release key 208)
3. **Arduino** maps DirectInput scan codes to actual keyboard events
4. **Computer** receives genuine USB HID keyboard input
5. **MapleStory** sees the input as real keyboard presses

## Command Protocol

The Arduino expects commands in this format:
- `p<code>\n` - Press key with DirectInput scan code
- `r<code>\n` - Release key with DirectInput scan code

Example:
- `p208\n` - Press Down Arrow key (scan code 0xD0 = 208)
- `r208\n` - Release Down Arrow key

## Key Mapping

The Arduino maps DirectInput scan codes to actual keys:

| Key | Scan Code | Key | Scan Code |
|-----|-----------|-----|-----------|
| A | 0x1E | Space | 0x39 |
| B | 0x30 | Enter | 0x1C |
| C | 0x2E | Esc | 0x01 |
| D | 0x20 | Tab | 0x0F |
| E | 0x12 | Ctrl | 0x1D |
| F | 0x21 | Alt | 0x38 |
| G | 0x22 | Shift | 0x2A |
| H | 0x23 | Up Arrow | 0xC8 |
| I | 0x17 | Down Arrow | 0xD0 |
| J | 0x24 | Left Arrow | 0xCB |
| K | 0x25 | Right Arrow | 0xCD |
| L | 0x26 | F1 | 0x3B |
| M | 0x32 | F2 | 0x3C |
| N | 0x31 | F3 | 0x3D |
| O | 0x18 | F4 | 0x3E |
| P | 0x19 | F5 | 0x3F |
| Q | 0x10 | F6 | 0x40 |
| R | 0x13 | F7 | 0x41 |
| S | 0x1F | F8 | 0x42 |
| T | 0x14 | F9 | 0x43 |
| U | 0x16 | F10 | 0x44 |
| V | 0x2F | F11 | 0x57 |
| W | 0x11 | F12 | 0x58 |
| X | 0x2D | 1 | 0x02 |
| Y | 0x15 | 2 | 0x03 |
| Z | 0x2C | 3 | 0x04 |
| | | 4 | 0x05 |
| | | 5 | 0x06 |
| | | 6 | 0x07 |
| | | 7 | 0x08 |
| | | 8 | 0x09 |
| | | 9 | 0x0A |
| | | 0 | 0x0B |
| | | - | 0x0C |
| | | = | 0x0D |
| | | ` | 0x29 |

## Troubleshooting

### Arduino Not Detected
- Check USB cable connection
- Try different USB ports
- Verify Arduino IDE shows correct board
- Check if Arduino appears in Device Manager (Windows) or `ls /dev/tty*` (macOS/Linux)

### Serial Connection Failed
- Verify the port name in settings.py matches your Arduino port
- Ensure Arduino is connected before starting the bot
- Check that no other program is using the serial port
- Try different baud rates (default is 115200)

### Keys Not Working
- Ensure MapleStory window is focused
- Check that Arduino sketch uploaded successfully
- Verify key mappings in the Arduino code
- Test with Serial Monitor to see if commands are received

### Permission Denied (Linux/macOS)
- Add your user to the dialout group (Linux): `sudo usermod -a -G dialout $USER`
- Grant accessibility permissions (macOS): System Preferences > Security & Privacy > Privacy > Accessibility

## Testing

1. **Upload the Arduino sketch** and open Serial Monitor
2. **Start the Python bot** - you should see "Connected to Arduino on [port]"
3. **Test basic functionality** - the bot should be able to send keystrokes
4. **Focus MapleStory** and test movement/combat commands

## Advantages

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Undetectable**: Sends genuine hardware keyboard events
- **Reliable**: No dependency on OS-specific APIs
- **Flexible**: Easy to modify key mappings or add new features

## Security Note

This method sends actual hardware keyboard events, which means:
- The Arduino will type even when other applications are focused
- Always ensure MapleStory is the active window when running the bot
- Consider adding a physical kill switch or emergency stop mechanism

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify Arduino connection and port settings
3. Test with Serial Monitor to debug communication
4. Ensure all dependencies are installed correctly 