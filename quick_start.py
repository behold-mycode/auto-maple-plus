#!/usr/bin/env python3
"""
Quick Start Script for Auto Maple Plus
This script helps you configure your Arduino and load a command book.
"""

import os
import sys
import glob
import serial.tools.list_ports

def find_arduino_port():
    """Find Arduino Leonardo port automatically."""
    ports = serial.tools.list_ports.comports()
    arduino_ports = []
    
    for port in ports:
        if 'Arduino' in port.description or 'Leonardo' in port.description:
            arduino_ports.append(port.device)
    
    return arduino_ports

def update_settings(port):
    """Update the Arduino port in settings.py."""
    settings_file = "src/common/settings.py"
    
    try:
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Update the ARDUINO_PORT line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('ARDUINO_PORT'):
                lines[i] = f'ARDUINO_PORT = "{port}"'
                break
        
        with open(settings_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated Arduino port to: {port}")
        return True
    except Exception as e:
        print(f"❌ Failed to update settings: {e}")
        return False

def main():
    print("🚀 Auto Maple Plus - Quick Start Setup")
    print("=" * 50)
    
    # Step 1: Find Arduino
    print("\n1. 🔍 Looking for Arduino Leonardo...")
    arduino_ports = find_arduino_port()
    
    if arduino_ports:
        print(f"✅ Found Arduino on: {arduino_ports[0]}")
        if len(arduino_ports) > 1:
            print(f"⚠️  Multiple Arduinos found: {arduino_ports}")
            print("   Using the first one...")
        
        # Update settings
        if update_settings(arduino_ports[0]):
            print("✅ Arduino port configured successfully!")
        else:
            print("❌ Failed to configure Arduino port")
            return
    else:
        print("❌ No Arduino Leonardo found!")
        print("   Please connect your Arduino Leonardo via USB")
        print("   Make sure the arduino_keyboard_controller.ino sketch is uploaded")
        return
    
    # Step 2: Test Arduino
    print("\n2. 🧪 Testing Arduino connection...")
    try:
        from src.common.arduino_input import ArduinoInput
        arduino = ArduinoInput()
        print("✅ Arduino connection successful!")
        arduino.close()
    except Exception as e:
        print(f"❌ Arduino test failed: {e}")
        print("   Please check your Arduino connection and sketch")
        return
    
    # Step 3: Show available command books
    print("\n3. 📚 Available Command Books:")
    command_books = glob.glob("resources/command_books/*.py")
    for i, book in enumerate(command_books, 1):
        name = os.path.basename(book).replace('.py', '')
        print(f"   {i}. {name}")
    
    # Step 4: Instructions
    print("\n4. 🎮 Next Steps:")
    print("   a) Run: python main.py")
    print("   b) In the GUI, go to Settings tab")
    print("   c) Load a command book for your character class")
    print("   d) Go to Edit tab to create or load a routine")
    print("   e) Press F1 to start the bot")
    
    print("\n📖 For detailed instructions, see: SETUP_GUIDE.md")
    print("🔧 For Arduino setup help, see: ARDUINO_SETUP.md")
    
    print("\n✅ Quick start setup complete!")

if __name__ == "__main__":
    main() 