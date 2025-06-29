#!/usr/bin/env python3
"""
Simple Minimap Fix Tool
This tool lets you manually set minimap coordinates to bypass template detection.
"""

import tkinter as tk
from tkinter import messagebox
import mss
import numpy as np
import cv2
import json
import os

class MinimapFixer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minimap Fix Tool")
        self.root.geometry("600x500")
        self.root.configure(bg='white')
        
        self.window_coords = None
        self.minimap_coords = None
        self.load_configs()
        
        self.setup_ui()
        
    def load_configs(self):
        """Load existing configurations."""
        # Load window config
        if os.path.exists("window_config.json"):
            with open("window_config.json", 'r') as f:
                self.window_coords = json.load(f)
        
        # Load minimap config if it exists
        if os.path.exists("minimap_config.json"):
            with open("minimap_config.json", 'r') as f:
                self.minimap_coords = json.load(f)
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Minimap Fix Tool", font=("Arial", 18, "bold"), 
                        bg='white', fg='black')
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Text(self.root, height=8, width=70, wrap=tk.WORD, font=("Arial", 12), 
                             bg='lightblue', fg='black', relief=tk.SUNKEN, bd=2)
        instructions.pack(pady=15, padx=20)
        instructions.insert(tk.END, """INSTRUCTIONS:

1. Make sure MapleStory is open and visible
2. Click "Select Minimap Area" below
3. Your MapleStory window will be captured
4. Click on the TOP-LEFT corner of the minimap (green dot)
5. Click on the BOTTOM-RIGHT corner of the minimap (red dot)
6. The minimap coordinates will be saved automatically

This will bypass the automatic template detection and use your manual selection instead.""")
        instructions.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=20)
        
        select_btn = tk.Button(button_frame, text="Select Minimap Area", command=self.select_minimap, 
                             bg="darkgreen", fg="white", font=("Arial", 14, "bold"), 
                             width=18, height=2, relief=tk.RAISED, bd=3)
        select_btn.pack(side=tk.LEFT, padx=10)
        
        test_btn = tk.Button(button_frame, text="Test Current Config", command=self.test_config,
                           bg="darkblue", fg="white", font=("Arial", 14, "bold"), 
                           width=18, height=2, relief=tk.RAISED, bd=3)
        test_btn.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready to fix minimap", font=("Arial", 12, "bold"), 
                                   bg='white', fg='darkblue')
        self.status_label.pack(pady=15)
        
        # Current config display
        if self.minimap_coords:
            config_text = f"Current minimap: ({self.minimap_coords['mm_left']},{self.minimap_coords['mm_top']}) to ({self.minimap_coords['mm_right']},{self.minimap_coords['mm_bottom']})"
            config_label = tk.Label(self.root, text=config_text, font=("Arial", 11), 
                                  bg='white', fg='darkgreen')
            config_label.pack(pady=5)
    
    def select_minimap(self):
        """Select the minimap area manually."""
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
                
                # Create window for selection
                cv2.namedWindow("Select Minimap Area", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Select Minimap Area", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                
                coordinates = []
                display_img = window_frame.copy()
                
                def mouse_callback(event, x, y, flags, param):
                    nonlocal display_img
                    if event == cv2.EVENT_LBUTTONDOWN:
                        coordinates.append((x, y))
                        print(f"Clicked at: ({x}, {y})")
                        
                        if len(coordinates) == 1:
                            # Draw green circle for first click
                            cv2.circle(display_img, (x, y), 8, (0, 255, 0), -1)
                            cv2.putText(display_img, "MINIMAP TOP-LEFT", (x+15, y-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                            cv2.imshow("Select Minimap Area", display_img)
                            
                        elif len(coordinates) == 2:
                            # Draw red circle for second click
                            cv2.circle(display_img, (x, y), 8, (0, 0, 255), -1)
                            cv2.putText(display_img, "MINIMAP BOTTOM-RIGHT", (x+15, y-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                            cv2.imshow("Select Minimap Area", display_img)
                            
                            # Calculate minimap area
                            x1, y1 = coordinates[0]
                            x2, y2 = coordinates[1]
                            
                            mm_left = min(x1, x2)
                            mm_top = min(y1, y2)
                            mm_right = max(x1, x2)
                            mm_bottom = max(y1, y2)
                            
                            # Show the cropped minimap
                            minimap = window_frame[mm_top:mm_bottom, mm_left:mm_right]
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
                            
                            self.minimap_coords = minimap_config
                            print(f"Minimap config saved: {minimap_config}")
                            
                            # Show success message
                            cv2.putText(display_img, "MINIMAP SAVED!", (display_img.shape[1]//2-200, display_img.shape[0]//2), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
                            cv2.imshow("Select Minimap Area", display_img)
                            cv2.waitKey(2000)  # Show for 2 seconds
                            cv2.destroyAllWindows()
                            
                            # Update status
                            self.status_label.config(text=f"Minimap saved: {mm_left},{mm_top} to {mm_right},{mm_bottom}")
                            
                            # Show success message
                            messagebox.showinfo("Success", f"Minimap area saved!\nTop-left: ({mm_left}, {mm_top})\nBottom-right: ({mm_right}, {mm_bottom})")
                
                cv2.setMouseCallback("Select Minimap Area", mouse_callback)
                
                # Add instructions on the image
                cv2.putText(display_img, "Click TOP-LEFT corner of minimap", (50, 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                cv2.putText(display_img, "Click BOTTOM-RIGHT corner of minimap", (50, display_img.shape[0]-50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                cv2.imshow("Select Minimap Area", display_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select minimap: {e}")
            self.status_label.config(text="Selection failed")
    
    def test_config(self):
        """Test the current minimap configuration."""
        if not self.minimap_coords:
            messagebox.showinfo("No Config", "No minimap configuration found. Please select the minimap area first.")
            return
        
        try:
            with mss.mss() as sct:
                # Capture the MapleStory window
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
                
                # Crop the minimap
                minimap = frame[self.minimap_coords['mm_top']:self.minimap_coords['mm_bottom'], 
                              self.minimap_coords['mm_left']:self.minimap_coords['mm_right']]
                
                # Show the minimap
                cv2.imshow("Test Minimap", minimap)
                cv2.waitKey(3000)  # Show for 3 seconds
                cv2.destroyAllWindows()
                
                messagebox.showinfo("Test Complete", "Minimap test completed. Check the displayed image to verify it's correct.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Test failed: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MinimapFixer()
    app.run() 