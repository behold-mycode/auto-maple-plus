#!/usr/bin/env python3
"""
Debug version of main.py with extensive logging to identify crash point
"""

import sys
import os
import traceback
import signal
import time

# Add src to path
sys.path.append('src')

def signal_handler(signum, frame):
    """Handle signals to get stack trace on crash"""
    print(f"\n[CRASH] Signal {signum} received!")
    print("Stack trace:")
    traceback.print_stack(frame)
    sys.exit(1)

# Set up signal handlers for common crash signals
signal.signal(signal.SIGSEGV, signal_handler)  # Segmentation fault
signal.signal(signal.SIGBUS, signal_handler)   # Bus error
signal.signal(signal.SIGILL, signal_handler)   # Illegal instruction
signal.signal(signal.SIGTRAP, signal_handler)  # Trace trap

def safe_import(module_name, description):
    """Safely import a module with logging"""
    try:
        print(f"[DEBUG] Importing {description}...")
        module = __import__(module_name)
        print(f"[DEBUG] ✓ {description} imported successfully")
        return module
    except Exception as e:
        print(f"[DEBUG] ✗ Failed to import {description}: {e}")
        traceback.print_exc()
        return None

def main():
    """Main function with extensive debugging"""
    print("[DEBUG] Starting debug version of Auto Maple...")
    
    try:
        # Import core modules with logging
        print("\n[DEBUG] === PHASE 1: Core Imports ===")
        config = safe_import('src.common.config', 'config')
        settings = safe_import('src.common.settings', 'settings')
        utils = safe_import('src.common.utils', 'utils')
        
        print("\n[DEBUG] === PHASE 2: Bot Modules ===")
        # Import classes directly like in original main.py
        from src.modules.bot import Bot
        from src.modules.capture import Capture
        from src.modules.listener import Listener
        from src.modules.watcher import Watcher
        from src.modules.notifier import Notifier
        from src.modules.gui import GUI
        print("[DEBUG] ✓ All bot modules imported successfully")
        
        print("\n[DEBUG] === PHASE 4: Command Book ===")
        command_book_module = safe_import('src.command_book.command_book', 'command book')
        
        print("\n[DEBUG] === PHASE 5: Routine ===")
        routine_module = safe_import('src.routine.routine', 'routine')
        
        print("\n[DEBUG] === PHASE 6: Arduino Input ===")
        arduino_module = safe_import('src.common.arduino_input', 'arduino input')
        
        print("\n[DEBUG] === PHASE 7: Initialize Bot ===")
        print("[DEBUG] Creating bot instance...")
        bot = Bot()
        print("[DEBUG] ✓ Bot instance created")
        
        print("[DEBUG] Setting config.bot...")
        config.bot = bot
        print("[DEBUG] ✓ config.bot set")
        
        print("\n[DEBUG] === PHASE 8: Initialize Capture ===")
        print("[DEBUG] Creating capture instance...")
        capture = Capture()
        print("[DEBUG] ✓ Capture instance created")
        
        print("[DEBUG] Setting config.capture...")
        config.capture = capture
        print("[DEBUG] ✓ config.capture set")
        
        print("\n[DEBUG] === PHASE 9: Initialize Listener ===")
        print("[DEBUG] Creating listener instance...")
        listener = Listener()
        print("[DEBUG] ✓ Listener instance created")
        
        print("[DEBUG] Setting config.listener...")
        config.listener = listener
        print("[DEBUG] ✓ config.listener set")
        
        print("\n[DEBUG] === PHASE 10: Initialize Watcher ===")
        print("[DEBUG] Creating watcher instance...")
        watcher = Watcher()
        print("[DEBUG] ✓ Watcher instance created")
        
        print("[DEBUG] Setting config.watcher...")
        config.watcher = watcher
        print("[DEBUG] ✓ config.watcher set")
        
        print("\n[DEBUG] === PHASE 11: Initialize Notifier ===")
        print("[DEBUG] Creating notifier instance...")
        notifier = Notifier()
        print("[DEBUG] ✓ Notifier instance created")
        
        print("[DEBUG] Setting config.notifier...")
        config.notifier = notifier
        print("[DEBUG] ✓ config.notifier set")
        
        print("\n[DEBUG] === PHASE 12: Initialize GUI ===")
        print("[DEBUG] Creating GUI instance...")
        gui = GUI()
        print("[DEBUG] ✓ GUI instance created")
        
        print("[DEBUG] Setting config.gui...")
        config.gui = gui
        print("[DEBUG] ✓ config.gui set")
        
        print("\n[DEBUG] === PHASE 13: Load Command Book ===")
        if command_book_module and config.bot:
            print("[DEBUG] Loading command book...")
            try:
                command_book = command_book_module.CommandBook('resources/command_books/astelle.py')
                print("[DEBUG] ✓ Command book loaded")
            except Exception as e:
                print(f"[DEBUG] ✗ Command book loading failed: {e}")
                traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 14: Load Routine ===")
        if routine_module and config.bot:
            print("[DEBUG] Loading routine...")
            try:
                routine = routine_module.Routine()
                routine.load('resources/routines/astelle/generic_flat_map.csv')
                print("[DEBUG] ✓ Routine loaded")
                
                print("[DEBUG] Setting config.routine...")
                config.routine = routine
                print("[DEBUG] ✓ config.routine set")
            except Exception as e:
                print(f"[DEBUG] ✗ Routine loading failed: {e}")
                traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 15: Start Bot Loop ===")
        print("[DEBUG] Starting bot loop...")
        try:
            config.bot.start()
            print("[DEBUG] ✓ Bot loop started")
            
            print("[DEBUG] Waiting for bot to be ready...")
            while not config.bot.ready:
                time.sleep(0.01)
            print("[DEBUG] ✓ Bot is ready")
        except Exception as e:
            print(f"[DEBUG] ✗ Bot loop start failed: {e}")
            traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 16: Start Capture ===")
        print("[DEBUG] Starting capture...")
        try:
            config.capture.start()
            print("[DEBUG] ✓ Capture started")
            
            print("[DEBUG] Waiting for capture to be ready...")
            while not config.capture.ready:
                time.sleep(0.01)
            print("[DEBUG] ✓ Capture is ready")
        except Exception as e:
            print(f"[DEBUG] ✗ Capture start failed: {e}")
            traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 17: Start Listener ===")
        print("[DEBUG] Starting listener...")
        try:
            config.listener.start()
            print("[DEBUG] ✓ Listener started")
            
            print("[DEBUG] Waiting for listener to be ready...")
            while not config.listener.ready:
                time.sleep(0.01)
            print("[DEBUG] ✓ Listener is ready")
        except Exception as e:
            print(f"[DEBUG] ✗ Listener start failed: {e}")
            traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 18: Start Watcher ===")
        print("[DEBUG] Starting watcher...")
        try:
            config.watcher.start()
            print("[DEBUG] ✓ Watcher started")
            
            print("[DEBUG] Waiting for watcher to be ready...")
            while not config.watcher.ready:
                time.sleep(0.01)
            print("[DEBUG] ✓ Watcher is ready")
        except Exception as e:
            print(f"[DEBUG] ✗ Watcher start failed: {e}")
            traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 19: Start Notifier ===")
        print("[DEBUG] Starting notifier...")
        try:
            config.notifier.start()
            print("[DEBUG] ✓ Notifier started")
            
            print("[DEBUG] Waiting for notifier to be ready...")
            while not config.notifier.ready:
                time.sleep(0.01)
            print("[DEBUG] ✓ Notifier is ready")
        except Exception as e:
            print(f"[DEBUG] ✗ Notifier start failed: {e}")
            traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 20: Start GUI ===")
        print("[DEBUG] Starting GUI...")
        try:
            config.gui.start()
            print("[DEBUG] ✓ GUI started")
        except Exception as e:
            print(f"[DEBUG] ✗ GUI start failed: {e}")
            traceback.print_exc()
        
        print("\n[DEBUG] === PHASE 21: Main Loop ===")
        print("[DEBUG] Entering main loop...")
        print("[DEBUG] Press Ctrl+C to stop or enable the bot to test toggle...")
        
        # Main loop
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[DEBUG] Keyboard interrupt received, shutting down...")
    except Exception as e:
        print(f"\n[DEBUG] Unexpected error: {e}")
        traceback.print_exc()
    finally:
        print("[DEBUG] Cleanup complete")

if __name__ == "__main__":
    main() 