"""The central program that ties all the modules together."""

import time
import threading
from src.modules.bot import Bot
from src.modules.capture import Capture
from src.modules.notifier import Notifier
from src.modules.watcher import Watcher
from src.modules.listener import Listener
from src.modules.gui import GUI


def create_modules():
    """Create all modules but don't start them yet."""
    bot = Bot()
    capture = Capture()
    notifier = Notifier()
    listener = Listener()
    watcher = Watcher()
    
    return bot, capture, notifier, listener, watcher


def start_background_threads(gui):
    """Start all background threads after GUI is running."""
    
    def start_threads():
        print('\n[~] Starting background threads...')
        
        # Start capture first (bot depends on it)
        gui.capture.start()
        while not gui.capture.ready:
            time.sleep(0.01)
        print('[~] Capture ready')
        
        # Start bot (depends on capture)
        gui.bot.start()
        while not gui.bot.ready:
            time.sleep(0.01)
        print('[~] Bot ready')
        
        # Start notifier
        gui.notifier.start()
        while not gui.notifier.ready:
            time.sleep(0.01)
        print('[~] Notifier ready')
        
        # Start watcher
        gui.watcher.start()
        while not gui.watcher.ready:
            time.sleep(0.01)
        print('[~] Watcher ready')
        
        # Start listener last (depends on other modules)
        gui.listener.start()
        while not gui.listener.ready:
            time.sleep(0.01)
        print('[~] Listener ready')
        
        print('\n[~] Successfully initialized Auto Maple')
    
    # Schedule the thread startup to happen after GUI is running
    gui.root.after(100, start_threads)


def main():
    """Main entry point with safe startup sequence."""
    
    # Create all modules first
    bot, capture, notifier, listener, watcher = create_modules()
    
    # Create GUI (this will set up Tkinter)
    gui = GUI()
    
    # Store modules in GUI for access by background threads
    gui.bot = bot
    gui.capture = capture
    gui.notifier = notifier
    gui.listener = listener
    gui.watcher = watcher
    
    # Schedule background thread startup after GUI is running
    start_background_threads(gui)
    
    # Start GUI mainloop (this blocks until GUI is closed)
    gui.start()


if __name__ == '__main__':
    main()
