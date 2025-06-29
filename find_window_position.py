#!/usr/bin/env python3
"""
Window Position Finder for Auto Maple Plus
This tool helps you find the coordinates of your MapleStory window.
"""

import tkinter as tk
from tkinter import messagebox
import mss
import numpy as np
import cv2

class WindowPositionFinder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Window Position Finder")
        self.root.geometry("400x300")
        
        # Variables
        self.x_var = tk.StringVar(value="0")
        self.y_var = tk.StringVar(value="0")
        self.width_var = tk.StringVar(value="1366")
        self.height_var = tk.StringVar(value="768")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="MapleStory Window Position Finder", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.root, text="1. Position your MapleStory window where you want it\n2. Click 'Capture Screen' to see your screen\n3. Click on the top-left corner of MapleStory window\n4. Click on the bottom-right corner of MapleStory window\n5. Copy the coordinates to your settings.py", justify=tk.LEFT)
        instructions.pack(pady=10, padx=20)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        capture_btn = tk.Button(button_frame, text="Capture Screen", command=self.capture_screen)
        capture_btn.pack(side=tk.LEFT, padx=5)
        
        # Coordinates display
        coord_frame = tk.Frame(self.root)
        coord_frame.pack(pady=10)
        
        tk.Label(coord_frame, text="X (left):").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(coord_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, padx=5)
        
        tk.Label(coord_frame, text="Y (top):").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(coord_frame, textvariable=self.y_var, width=10).grid(row=1, column=1, padx=5)
        
        tk.Label(coord_frame, text="Width:").grid(row=2, column=0, sticky=tk.W)
        tk.Entry(coord_frame, textvariable=self.width_var, width=10).grid(row=2, column=1, padx=5)
        
        tk.Label(coord_frame, text="Height:").grid(row=3, column=0, sticky=tk.W)
        tk.Entry(coord_frame, textvariable=self.height_var, width=10).grid(row=3, column=1, padx=5)
        
        # Copy button
        copy_btn = tk.Button(self.root, text="Copy to Settings", command=self.copy_to_settings)
        copy_btn.pack(pady=10)
        
    def capture_screen(self):
        """Capture the screen and let user click to find coordinates."""
        try:
            with mss.mss() as sct:
                # Capture entire screen
                screenshot = sct.grab(sct.monitors[1])  # Primary monitor
                img_array = np.array(screenshot)
                
                # Convert from BGRA to BGR
                if img_array.shape[2] == 4:
                    img_array = img_array[:, :, :3]
                
                # Create window to display screenshot
                cv2.namedWindow("Click on MapleStory window corners", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Click on MapleStory window corners", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                
                coordinates = []
                
                def mouse_callback(event, x, y, flags, param):
                    if event == cv2.EVENT_LBUTTONDOWN:
                        coordinates.append((x, y))
                        print(f"Clicked at: ({x}, {y})")
                        
                        if len(coordinates) == 1:
                            cv2.circle(img_array, (x, y), 5, (0, 255, 0), -1)
                            cv2.putText(img_array, f"Top-left: ({x}, {y})", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.imshow("Click on MapleStory window corners", img_array)
                        elif len(coordinates) == 2:
                            cv2.circle(img_array, (x, y), 5, (0, 0, 255), -1)
                            cv2.putText(img_array, f"Bottom-right: ({x}, {y})", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.imshow("Click on MapleStory window corners", img_array)
                            
                            # Calculate window dimensions
                            x1, y1 = coordinates[0]
                            x2, y2 = coordinates[1]
                            
                            left = min(x1, x2)
                            top = min(y1, y2)
                            width = abs(x2 - x1)
                            height = abs(y2 - y1)
                            
                            # Update variables
                            self.x_var.set(str(left))
                            self.y_var.set(str(top))
                            self.width_var.set(str(width))
                            self.height_var.set(str(height))
                            
                            cv2.waitKey(1000)  # Show for 1 second
                            cv2.destroyAllWindows()
                
                cv2.setMouseCallback("Click on MapleStory window corners", mouse_callback)
                cv2.imshow("Click on MapleStory window corners", img_array)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screen: {e}")
    
    def copy_to_settings(self):
        """Copy the coordinates to settings.py file."""
        try:
            settings_content = f"""# === Window Position Configuration ===
# Set to True to use manual window position instead of auto-detection
use_manual_window_position = True

# Manual window position (only used if use_manual_window_position = True)
# These are the coordinates of your MapleStory window on screen
maple_window_left = {self.x_var.get()}      # X coordinate of window's left edge
maple_window_top = {self.y_var.get()}       # Y coordinate of window's top edge  
maple_window_width = {self.width_var.get()}  # Width of MapleStory window
maple_window_height = {self.height_var.get()}  # Height of MapleStory window
"""
            
            messagebox.showinfo("Settings", f"Copy these settings to src/common/settings.py:\n\n{settings_content}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate settings: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WindowPositionFinder()
    app.run() 