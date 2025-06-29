#!/usr/bin/env python3
"""
Test script for Arduino keyboard input system.
This script tests the Arduino connection and key press functionality.
"""

import sys
import time
import platform
from src.common.arduino_input import ArduinoInput

def test_arduino_connection():
    """Test basic Arduino connection."""
    print("🔌 Testing Arduino connection...")
    
    try:
        arduino = ArduinoInput()
        print("✅ Arduino connection successful!")
        return arduino
    except Exception as e:
        print(f"❌ Arduino connection failed: {e}")
        print("\n📋 Troubleshooting steps:")
        print("1. Make sure Arduino Leonardo is connected via USB")
        print("2. Check if the correct port is set in settings")
        print("3. Verify Arduino sketch is uploaded correctly")
        print("4. Try running: python -m serial.tools.list_ports")
        return None

def test_key_press(arduino, key):
    """Test pressing a specific key."""
    print(f"⌨️  Testing key press: '{key}'")
    try:
        arduino.press(key)
        print(f"✅ Key '{key}' pressed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to press key '{key}': {e}")
        return False

def test_key_sequence(arduino):
    """Test a sequence of key presses."""
    print("\n🎯 Testing key sequence...")
    
    test_keys = ['w', 'a', 's', 'd', 'space', 'enter']
    success_count = 0
    
    for key in test_keys:
        if test_key_press(arduino, key):
            success_count += 1
        time.sleep(0.5)  # Delay between keys
    
    print(f"\n📊 Key sequence test: {success_count}/{len(test_keys)} keys successful")
    return success_count == len(test_keys)

def test_hold_release(arduino):
    """Test holding and releasing keys."""
    print("\n🔒 Testing key hold/release...")
    
    try:
        print("Holding 'w' key for 2 seconds...")
        arduino.key_down('w')
        time.sleep(2)
        arduino.key_up('w')
        print("✅ Key hold/release test successful")
        return True
    except Exception as e:
        print(f"❌ Key hold/release test failed: {e}")
        return False

def test_scan_code(arduino):
    """Test DirectInput scan code functionality."""
    print("\n🔢 Testing DirectInput scan codes...")
    
    # Test some common scan codes
    scan_codes = {
        0x11: 'W key',
        0x1E: 'A key', 
        0x1F: 'S key',
        0x20: 'D key',
        0x39: 'Spacebar'
    }
    
    success_count = 0
    for scan_code, key_name in scan_codes.items():
        try:
            print(f"Testing scan code 0x{scan_code:02X} ({key_name})...")
            arduino.press_scan_code(scan_code)
            success_count += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"❌ Failed scan code 0x{scan_code:02X}: {e}")
    
    print(f"\n📊 Scan code test: {success_count}/{len(scan_codes)} successful")
    return success_count == len(scan_codes)

def main():
    """Main test function."""
    print("🚀 Auto Maple Plus - Arduino Input Test")
    print("=" * 50)
    
    # Check platform
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    
    # Test Arduino connection
    arduino = test_arduino_connection()
    if not arduino:
        print("\n❌ Cannot proceed without Arduino connection")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Key Sequence", lambda: test_key_sequence(arduino)),
        ("Hold/Release", lambda: test_hold_release(arduino)),
        ("Scan Codes", lambda: test_scan_code(arduino))
    ]
    
    print("\n🧪 Running comprehensive tests...")
    passed_tests = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed_tests += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed_tests}/{len(tests)} tests passed")
    
    if passed_tests == len(tests):
        print("🎉 All tests passed! Arduino input system is working correctly.")
        print("\n💡 You can now run Auto Maple Plus with cross-platform keyboard input!")
    else:
        print("⚠️  Some tests failed. Check Arduino connection and configuration.")
        print("\n🔧 Troubleshooting:")
        print("- Verify Arduino Leonardo is connected")
        print("- Check port settings in src/common/settings.py")
        print("- Ensure Arduino sketch is uploaded correctly")
        print("- Try reconnecting the Arduino")
    
    # Cleanup
    try:
        arduino.close()
        print("\n🔌 Arduino connection closed")
    except:
        pass

if __name__ == "__main__":
    main() 