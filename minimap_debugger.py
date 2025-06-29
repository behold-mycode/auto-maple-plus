#!/usr/bin/env python3
"""
Minimap Debugger for Auto Maple Plus
This tool helps debug minimap detection issues by showing what the program is capturing.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import mss
import numpy as np
import cv2
import json
import os
from src.common import utils

class MinimapDebugger:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minimap Debugger")
        self.root.geometry("800x600")
        
        self.window_coords = None
        self.load_window_config()
        
        self.setup_ui()
        
    def load_window_config(self):
        """Load saved window configuration."""
        try:
            if os.path.exists("window_config.json"):
                with open("window_config.json", 'r') as f:
                    self.window_coords = json.load(f)
                    print(f"[INFO] Loaded window config: {self.window_coords}")
        except Exception as e:
            print(f"[WARN] Failed to load window config: {e}")
    
    def setup_ui(self):
        # Configure the root window for better visibility
        self.root.configure(bg='white')
        
        # Title
        title = tk.Label(self.root, text="Minimap Debugger", font=("Arial", 18, "bold"), 
                        bg='white', fg='black')
        title.pack(pady=15)
        
        # Instructions
        instructions = tk.Label(self.root, text="This tool shows what the program is capturing and where it's looking for the minimap.", 
                              font=("Arial", 12), bg='white', fg='black')
        instructions.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=15)
        
        capture_btn = tk.Button(button_frame, text="Capture & Debug", command=self.capture_and_display, 
                              bg="darkgreen", fg="white", font=("Arial", 14, "bold"), 
                              width=15, height=2, relief=tk.RAISED, bd=3)
        capture_btn.pack(side=tk.LEFT, padx=10)
        
        manual_btn = tk.Button(button_frame, text="Manual Minimap Select", command=self.manual_minimap_select,
                             bg="darkblue", fg="white", font=("Arial", 14, "bold"), 
                             width=15, height=2, relief=tk.RAISED, bd=3)
        manual_btn.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready to debug", font=("Arial", 12, "bold"), 
                                   bg='white', fg='darkblue')
        self.status_label.pack(pady=10)
        
        # Debug info
        self.debug_text = tk.Text(self.root, height=12, width=80, font=("Courier", 11), 
                                 bg='black', fg='lime', relief=tk.SUNKEN, bd=2)
        self.debug_text.pack(pady=15, padx=20)
        
    def capture_and_display(self):
        """Capture the MapleStory window and display it with minimap overlay."""
        if not self.window_coords:
            messagebox.showerror("Error", "No window configuration found. Run the window selector first.")
            return
        
        self.status_label.config(text="Capturing MapleStory window...")
        self.root.update()
        
        try:
            with mss.mss() as sct:
                # Get all monitors
                monitors = sct.monitors
                print(f"Available monitors: {monitors}")
                
                # For ultrawide monitors, we need to capture the entire screen
                # and then crop to our window area
                print(f"Window coordinates: {self.window_coords}")
                
                # Capture the entire screen (monitor 0 is all monitors combined)
                screenshot = sct.grab(monitors[0])
                frame = np.array(screenshot)
                
                # Convert from BGRA to BGR if needed
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                
                print(f"Full screen capture shape: {frame.shape}")
                
                # Crop to just the MapleStory window using absolute coordinates
                window_frame = frame[self.window_coords['top']:self.window_coords['top'] + self.window_coords['height'], 
                                   self.window_coords['left']:self.window_coords['left'] + self.window_coords['width']]
                
                print(f"Window frame shape: {window_frame.shape}")
                
                # Load minimap coordinates if available
                minimap_coords = None
                if os.path.exists("minimap_config.json"):
                    with open("minimap_config.json", 'r') as f:
                        minimap_coords = json.load(f)
                
                # Create display image with overlay
                display_img = window_frame.copy()
                
                # Draw window border
                cv2.rectangle(display_img, (0, 0), (display_img.shape[1]-1, display_img.shape[0]-1), (0, 255, 0), 3)
                cv2.putText(display_img, "MAPLESTORY WINDOW", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                if minimap_coords:
                    # Draw minimap area
                    mm_left = minimap_coords['mm_left']
                    mm_top = minimap_coords['mm_top']
                    mm_right = minimap_coords['mm_right']
                    mm_bottom = minimap_coords['mm_bottom']
                    
                    cv2.rectangle(display_img, (mm_left, mm_top), (mm_right, mm_bottom), (0, 0, 255), 3)
                    cv2.putText(display_img, "MINIMAP AREA", (mm_left, mm_top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    # Show minimap coordinates
                    coord_text = f"({mm_left},{mm_top}) to ({mm_right},{mm_bottom})"
                    cv2.putText(display_img, coord_text, (mm_left, mm_bottom+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # Extract and show minimap
                    minimap = window_frame[mm_top:mm_bottom, mm_left:mm_right]
                    if minimap.size > 0:
                        # Resize minimap for display
                        minimap_height, minimap_width = minimap.shape[:2]
                        scale = min(200 / minimap_width, 200 / minimap_height)
                        new_width = int(minimap_width * scale)
                        new_height = int(minimap_height * scale)
                        minimap_resized = cv2.resize(minimap, (new_width, new_height))
                        
                        # Create minimap display window
                        cv2.namedWindow("Minimap View", cv2.WINDOW_NORMAL)
                        cv2.imshow("Minimap View", minimap_resized)
                        
                        self.status_label.config(text=f"Minimap: {coord_text}")
                    else:
                        self.status_label.config(text="Error: Invalid minimap area")
                else:
                    # Show template detection areas
                    height, width = display_img.shape[:2]
                    
                    # Top-left corner (typical minimap location)
                    tl_size = 100
                    cv2.rectangle(display_img, (0, 0), (tl_size, tl_size), (255, 0, 0), 2)
                    cv2.putText(display_img, "TOP-LEFT", (5, tl_size+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    
                    # Top-right corner
                    tr_size = 100
                    cv2.rectangle(display_img, (width-tr_size, 0), (width, tr_size), (255, 0, 0), 2)
                    cv2.putText(display_img, "TOP-RIGHT", (width-tr_size+5, tr_size+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    
                    # Bottom-right corner
                    br_size = 100
                    cv2.rectangle(display_img, (width-br_size, height-br_size), (width, height), (255, 0, 0), 2)
                    cv2.putText(display_img, "BOTTOM-RIGHT", (width-br_size+5, height-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    
                    cv2.putText(display_img, "No minimap config found - showing template areas", (10, height-50), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    cv2.putText(display_img, "Run fix_minimap.py to set minimap area manually", (10, height-20), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    
                    self.status_label.config(text="No minimap config - showing template areas")
                
                # Display the image
                cv2.namedWindow("MapleStory Window Debug", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("MapleStory Window Debug", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow("MapleStory Window Debug", display_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture window: {e}")
            self.status_label.config(text="Capture failed")
    
    def manual_minimap_select(self):
        """Manually select the minimap area."""
        if not self.window_coords:
            messagebox.showerror("Error", "No window configuration found. Run the window selector first.")
            return
        
        self.status_label.config(text="Capturing for manual selection...")
        self.root.update()
        
        try:
            with mss.mss() as sct:
                # Capture the window
                window = {
                    'left': self.window_coords['left'],
                    'top': self.window_coords['top'],
                    'width': self.window_coords['width'],
                    'height': self.window_coords['height']
                }
                
                screenshot = sct.grab(window)
                frame = np.array(screenshot)
                
                # Convert from BGRA to BGR if needed
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                
                # Create window for manual selection
                cv2.namedWindow("Manual Minimap Selection", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Manual Minimap Selection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                
                coordinates = []
                display_img = frame.copy()
                
                def mouse_callback(event, x, y, flags, param):
                    nonlocal display_img
                    if event == cv2.EVENT_LBUTTONDOWN:
                        coordinates.append((x, y))
                        print(f"Clicked at: ({x}, {y})")
                        
                        if len(coordinates) == 1:
                            cv2.circle(display_img, (x, y), 5, (0, 255, 0), -1)
                            cv2.putText(display_img, f"Minimap TL: ({x}, {y})", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.imshow("Manual Minimap Selection", display_img)
                        elif len(coordinates) == 2:
                            cv2.circle(display_img, (x, y), 5, (0, 0, 255), -1)
                            cv2.putText(display_img, f"Minimap BR: ({x}, {y})", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.imshow("Manual Minimap Selection", display_img)
                            
                            # Calculate minimap area
                            x1, y1 = coordinates[0]
                            x2, y2 = coordinates[1]
                            
                            mm_left = min(x1, x2)
                            mm_top = min(y1, y2)
                            mm_right = max(x1, x2)
                            mm_bottom = max(y1, y2)
                            
                            # Show the cropped minimap
                            minimap = frame[mm_top:mm_bottom, mm_left:mm_right]
                            cv2.imshow("Selected Minimap", minimap)
                            
                            # Save the coordinates
                            minimap_config = {
                                'mm_left': mm_left,
                                'mm_top': mm_top,
                                'mm_right': mm_right,
                                'mm_bottom': mm_bottom
                            }
                            
                            with open("minimap_config.json", 'w') as f:
                                json.dump(minimap_config, f)
                            
                            print(f"Minimap config saved: {minimap_config}")
                            
                            cv2.waitKey(2000)
                            cv2.destroyAllWindows()
                            
                            self.status_label.config(text=f"Minimap selected: {mm_left},{mm_top} to {mm_right},{mm_bottom}")
                
                cv2.setMouseCallback("Manual Minimap Selection", mouse_callback)
                cv2.putText(display_img, "Click TOP-LEFT corner of minimap", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                cv2.putText(display_img, "Click BOTTOM-RIGHT corner of minimap", (50, display_img.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                cv2.imshow("Manual Minimap Selection", display_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
        except Exception as e:
            messagebox.showerror("Error", f"Manual selection failed: {e}")
            self.status_label.config(text="Manual selection failed")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MinimapDebugger()
    app.run() 