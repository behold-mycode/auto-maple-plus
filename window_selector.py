#!/usr/bin/env python3
"""
Window Selector for Auto Maple Plus
This tool allows you to quickly select your MapleStory window with a hotkey.
"""

import tkinter as tk
from tkinter import messagebox
import mss
import numpy as np
import cv2
import threading
import time
import json
import os

class WindowSelector:
    def __init__(self):
        self.window_coords = None
        self.config_file = "window_config.json"
        self.load_saved_config()
        
    def load_saved_config(self):
        """Load previously saved window configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.window_coords = json.load(f)
                    print(f"[INFO] Loaded saved window config: {self.window_coords}")
        except Exception as e:
            print(f"[WARN] Failed to load saved config: {e}")
    
    def save_config(self, coords):
        """Save window configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(coords, f)
            print(f"[INFO] Saved window config: {coords}")
        except Exception as e:
            print(f"[WARN] Failed to save config: {e}")
    
    def select_window(self):
        """Open window selection interface."""
        try:
            with mss.mss() as sct:
                # Capture entire screen
                screenshot = sct.grab(sct.monitors[1])  # Primary monitor
                img_array = np.array(screenshot)
                
                # Convert from BGRA to BGR
                if img_array.shape[2] == 4:
                    img_array = img_array[:, :, :3]
                
                # Ensure image is in the correct format for OpenCV
                img_array = img_array.astype(np.uint8)
                
                # Create window to display screenshot
                cv2.namedWindow("Select MapleStory Window", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Select MapleStory Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                
                coordinates = []
                display_img = img_array.copy()  # Create a copy for drawing
                
                def mouse_callback(event, x, y, flags, param):
                    nonlocal display_img
                    if event == cv2.EVENT_LBUTTONDOWN:
                        coordinates.append((x, y))
                        print(f"Clicked at: ({x}, {y})")
                        
                        if len(coordinates) == 1:
                            # Draw on the display copy
                            cv2.circle(display_img, (x, y), 5, (0, 255, 0), -1)
                            cv2.putText(display_img, f"Top-left: ({x}, {y})", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.imshow("Select MapleStory Window", display_img)
                        elif len(coordinates) == 2:
                            # Draw on the display copy
                            cv2.circle(display_img, (x, y), 5, (0, 0, 255), -1)
                            cv2.putText(display_img, f"Bottom-right: ({x}, {y})", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.imshow("Select MapleStory Window", display_img)
                            
                            # Calculate window dimensions
                            x1, y1 = coordinates[0]
                            x2, y2 = coordinates[1]
                            
                            left = min(x1, x2)
                            top = min(y1, y2)
                            width = abs(x2 - x1)
                            height = abs(y2 - y1)
                            
                            coords = {
                                'left': left,
                                'top': top,
                                'width': width,
                                'height': height
                            }
                            
                            self.window_coords = coords
                            self.save_config(coords)
                            
                            cv2.waitKey(1000)  # Show for 1 second
                            cv2.destroyAllWindows()
                
                cv2.setMouseCallback("Select MapleStory Window", mouse_callback)
                cv2.imshow("Select MapleStory Window", display_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                return self.window_coords
                
        except Exception as e:
            print(f"[ERROR] Failed to select window: {e}")
            return None
    
    def get_window_coords(self):
        """Get the current window coordinates."""
        return self.window_coords

def main():
    """Main function for testing."""
    selector = WindowSelector()
    print("Click on the top-left and bottom-right corners of your MapleStory window...")
    coords = selector.select_window()
    if coords:
        print(f"Selected window: {coords}")
    else:
        print("Window selection cancelled or failed.")

if __name__ == "__main__":
    main() 