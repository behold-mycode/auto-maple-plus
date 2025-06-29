#!/usr/bin/env python3
"""
Simple Window Selector for Auto Maple Plus
A user-friendly tool to select your MapleStory window.
"""

import tkinter as tk
from tkinter import messagebox
import mss
import numpy as np
import cv2
import json
import os

class SimpleWindowSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MapleStory Window Selector")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.window_coords = None
        self.config_file = "window_config.json"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure the root window for better visibility
        self.root.configure(bg='white')
        
        # Title
        title = tk.Label(self.root, text="MapleStory Window Selector", font=("Arial", 18, "bold"), 
                        bg='white', fg='black')
        title.pack(pady=20)
        
        # Instructions
        instructions = tk.Text(self.root, height=10, width=65, wrap=tk.WORD, font=("Arial", 12), 
                             bg='lightblue', fg='black', relief=tk.SUNKEN, bd=2)
        instructions.pack(pady=15, padx=20)
        instructions.insert(tk.END, """INSTRUCTIONS:

1. Make sure MapleStory is open and visible on your screen
2. Click "Start Selection" below
3. Your screen will be captured and displayed
4. Click on the TOP-LEFT corner of your MapleStory window (green dot)
5. Click on the BOTTOM-RIGHT corner of your MapleStory window (red dot)
6. The tool will save your window position automatically

TIPS:
- Make sure MapleStory is not minimized
- Click precisely on the corners of the game window
- You can press ESC to cancel if needed""")
        instructions.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=20)
        
        start_btn = tk.Button(button_frame, text="Start Selection", command=self.start_selection, 
                            bg="darkgreen", fg="white", font=("Arial", 14, "bold"), 
                            width=18, height=2, relief=tk.RAISED, bd=3)
        start_btn.pack(side=tk.LEFT, padx=10)
        
        test_btn = tk.Button(button_frame, text="Test Saved Config", command=self.test_config,
                           bg="darkblue", fg="white", font=("Arial", 14, "bold"), 
                           width=18, height=2, relief=tk.RAISED, bd=3)
        test_btn.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready to select window", font=("Arial", 12, "bold"), 
                                   bg='white', fg='darkblue')
        self.status_label.pack(pady=15)
        
    def start_selection(self):
        """Start the window selection process."""
        self.status_label.config(text="Capturing screen...")
        self.root.update()
        
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
                cv2.namedWindow("Select MapleStory Window - Click corners", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Select MapleStory Window - Click corners", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                
                coordinates = []
                display_img = img_array.copy()
                
                def mouse_callback(event, x, y, flags, param):
                    nonlocal display_img
                    if event == cv2.EVENT_LBUTTONDOWN:
                        coordinates.append((x, y))
                        print(f"Clicked at: ({x}, {y})")
                        
                        if len(coordinates) == 1:
                            # Draw green circle for first click
                            cv2.circle(display_img, (x, y), 8, (0, 255, 0), -1)
                            cv2.putText(display_img, "TOP-LEFT", (x+15, y-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                            cv2.imshow("Select MapleStory Window - Click corners", display_img)
                            
                        elif len(coordinates) == 2:
                            # Draw red circle for second click
                            cv2.circle(display_img, (x, y), 8, (0, 0, 255), -1)
                            cv2.putText(display_img, "BOTTOM-RIGHT", (x+15, y-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                            cv2.imshow("Select MapleStory Window - Click corners", display_img)
                            
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
                            
                            # Show success message
                            cv2.putText(display_img, "WINDOW SAVED!", (display_img.shape[1]//2-200, display_img.shape[0]//2), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
                            cv2.imshow("Select MapleStory Window - Click corners", display_img)
                            cv2.waitKey(2000)  # Show for 2 seconds
                            cv2.destroyAllWindows()
                            
                            # Update status
                            self.status_label.config(text=f"Window saved: {left},{top} {width}x{height}")
                
                cv2.setMouseCallback("Select MapleStory Window - Click corners", mouse_callback)
                cv2.imshow("Select MapleStory Window - Click corners", display_img)
                
                # Add instructions on the image
                cv2.putText(display_img, "Click TOP-LEFT corner of MapleStory window", (50, 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                cv2.putText(display_img, "Press ESC to cancel", (50, display_img.shape[0]-50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                cv2.imshow("Select MapleStory Window - Click corners", display_img)
                
                key = cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                if key == 27:  # ESC key
                    self.status_label.config(text="Selection cancelled")
                elif self.window_coords:
                    messagebox.showinfo("Success", f"Window position saved!\nLeft: {self.window_coords['left']}\nTop: {self.window_coords['top']}\nWidth: {self.window_coords['width']}\nHeight: {self.window_coords['height']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screen: {e}")
            self.status_label.config(text="Error occurred")
    
    def save_config(self, coords):
        """Save window configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(coords, f)
            print(f"[INFO] Saved window config: {coords}")
        except Exception as e:
            print(f"[WARN] Failed to save config: {e}")
    
    def test_config(self):
        """Test the saved window configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    messagebox.showinfo("Saved Config", f"Current saved configuration:\nLeft: {config_data['left']}\nTop: {config_data['top']}\nWidth: {config_data['width']}\nHeight: {config_data['height']}")
            else:
                messagebox.showinfo("No Config", "No saved window configuration found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleWindowSelector()
    app.run() 