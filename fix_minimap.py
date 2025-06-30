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
import sys
from PIL import Image, ImageTk

class MinimapFixer:
    """
    A tool to manually select and configure the minimap region for Auto Maple Plus.
    This tool is especially useful when automatic minimap detection fails.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Maple Plus - Minimap Fixer")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.window_config = None
        self.minimap_config = None
        self.selection_active = False
        self.selection_start = None
        self.selection_current = None
        self.screenshot = None
        self.screenshot_tk = None
        self.canvas = None
        self.scale_factor = 1.0
        
        self.load_configs()
        self.setup_ui()
        
    def load_configs(self):
        """Load existing window and minimap configurations."""
        try:
            # Load window config
            if os.path.exists("window_config.json"):
                with open("window_config.json", "r") as f:
                    self.window_config = json.load(f)
                    print(f"Loaded window config: {self.window_config}")
            
            # Load minimap config
            if os.path.exists("minimap_config.json"):
                with open("minimap_config.json", "r") as f:
                    self.minimap_config = json.load(f)
                    print(f"Loaded minimap config: {self.minimap_config}")
        except Exception as e:
            print(f"Error loading configurations: {e}")
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create control panel
        control_panel = tk.Frame(main_frame)
        control_panel.pack(fill=tk.X, side=tk.TOP, pady=5)
        
        # Buttons
        tk.Button(control_panel, text="Select Minimap", command=self.select_minimap).pack(side=tk.LEFT, padx=5)
        tk.Button(control_panel, text="Save Configuration", command=self.save_config).pack(side=tk.LEFT, padx=5)
        tk.Button(control_panel, text="Test Configuration", command=self.test_config).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready. Click 'Select Minimap' to begin.")
        status_label = tk.Label(main_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Selection info
        self.selection_info_var = tk.StringVar(value="No selection")
        selection_info = tk.Label(main_frame, textvariable=self.selection_info_var, anchor=tk.W)
        selection_info.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Canvas for screenshot
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Canvas scrollbars
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Canvas events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        
    def select_minimap(self):
        """Take a screenshot and allow the user to select the minimap region."""
        if not self.window_config:
            messagebox.showwarning("Warning", "No window configuration found. Please run window_selector.py first.")
            return
        
        try:
            with mss.mss() as sct:
                # Create a region dict for mss
                region = {
                    'left': self.window_config['left'],
                    'top': self.window_config['top'],
                    'width': self.window_config['width'],
                    'height': self.window_config['height']
                }
                
                # Take screenshot of the MapleStory window
                sct_img = sct.grab(region)
                img = np.array(sct_img)
                
                # Convert BGRA to RGB for display
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                self.screenshot = img
                self.display_screenshot()
                
                self.status_var.set("Screenshot taken. Draw a rectangle around the minimap.")
                self.selection_active = False
                self.selection_start = None
                self.selection_current = None
                self.update_selection_display()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {str(e)}")
            
    def display_screenshot(self):
        """Display the screenshot on the canvas."""
        if self.screenshot is None:
            return
            
        # Calculate scale factor for large screens
        h, w = self.screenshot.shape[:2]
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        if canvas_w <= 1 or canvas_h <= 1:  # Canvas not yet realized
            canvas_w = 800
            canvas_h = 600
            
        scale_w = canvas_w / w
        scale_h = canvas_h / h
        self.scale_factor = min(1.0, min(scale_w, scale_h))
        
        # Scale the image if needed
        if self.scale_factor < 1.0:
            display_w = int(w * self.scale_factor)
            display_h = int(h * self.scale_factor)
            display_img = cv2.resize(self.screenshot, (display_w, display_h), interpolation=cv2.INTER_AREA)
        else:
            self.scale_factor = 1.0
            display_img = self.screenshot
            
        # Convert to PhotoImage
        pil_img = Image.fromarray(display_img)
        self.screenshot_tk = ImageTk.PhotoImage(image=pil_img)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.screenshot_tk, anchor=tk.NW)
        self.canvas.config(scrollregion=(0, 0, display_img.shape[1], display_img.shape[0]))
        
        # If we have existing minimap config, draw it
        if self.minimap_config:
            self.draw_existing_minimap()
            
    def draw_existing_minimap(self):
        """Draw the existing minimap configuration on the canvas."""
        if not self.minimap_config:
            return
            
        # Calculate relative coordinates within the window
        left = self.minimap_config['mm_left'] - self.window_config['left']
        top = self.minimap_config['mm_top'] - self.window_config['top']
        right = self.minimap_config['mm_right'] - self.window_config['left']
        bottom = self.minimap_config['mm_bottom'] - self.window_config['top']
        
        # Scale coordinates
        scaled_left = left * self.scale_factor
        scaled_top = top * self.scale_factor
        scaled_right = right * self.scale_factor
        scaled_bottom = bottom * self.scale_factor
        
        # Draw rectangle
        self.canvas.create_rectangle(
            scaled_left, scaled_top, scaled_right, scaled_bottom,
            outline="yellow", width=2, tags="existing_minimap"
        )
        
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        if self.screenshot is None:
            return
            
        # Get canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convert to original image coordinates
        x = int(canvas_x / self.scale_factor)
        y = int(canvas_y / self.scale_factor)
        
        self.selection_active = True
        self.selection_start = (x, y)
        self.selection_current = (x, y)
        self.update_selection_display()
        
    def on_mouse_move(self, event):
        """Handle mouse movement."""
        if not self.selection_active or self.screenshot is None:
            return
            
        # Get canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convert to original image coordinates
        x = int(canvas_x / self.scale_factor)
        y = int(canvas_y / self.scale_factor)
        
        self.selection_current = (x, y)
        self.update_selection_display()
        
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        if not self.selection_active or self.screenshot is None:
            return
            
        # Get canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convert to original image coordinates
        x = int(canvas_x / self.scale_factor)
        y = int(canvas_y / self.scale_factor)
        
        self.selection_current = (x, y)
        self.update_selection_display()
        self.selection_active = False
        
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming."""
        if self.screenshot is None:
            return
            
        # Determine zoom direction
        if event.num == 4 or event.delta > 0:  # Scroll up
            zoom_factor = 1.1
        elif event.num == 5 or event.delta < 0:  # Scroll down
            zoom_factor = 0.9
        else:
            return
            
        # Zoom
        self.scale_factor *= zoom_factor
        self.scale_factor = max(0.1, min(3.0, self.scale_factor))  # Limit zoom range
        
        # Redisplay with new scale
        self.display_screenshot()
        self.update_selection_display()
        
    def update_selection_display(self):
        """Update the selection rectangle on the canvas."""
        self.canvas.delete("selection")
        
        if self.selection_start is None or self.selection_current is None:
            self.selection_info_var.set("No selection")
            return
            
        # Get coordinates
        x1, y1 = self.selection_start
        x2, y2 = self.selection_current
        
        # Ensure x1,y1 is top-left and x2,y2 is bottom-right
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        # Draw scaled rectangle
        scaled_left = left * self.scale_factor
        scaled_top = top * self.scale_factor
        scaled_right = right * self.scale_factor
        scaled_bottom = bottom * self.scale_factor
        
        self.canvas.create_rectangle(
            scaled_left, scaled_top, scaled_right, scaled_bottom,
            outline="red", width=2, tags="selection"
        )
        
        # Update info text
        width = right - left
        height = bottom - top
        ratio = width / height if height > 0 else 0
        
        # Calculate absolute coordinates
        abs_left = left + self.window_config['left']
        abs_top = top + self.window_config['top']
        abs_right = right + self.window_config['left']
        abs_bottom = bottom + self.window_config['top']
        
        self.selection_info_var.set(
            f"Minimap: ({abs_left}, {abs_top}) to ({abs_right}, {abs_bottom}), "
            f"Size: {width}x{height}, Ratio: {ratio:.2f}"
        )
        
    def get_selection_coords(self):
        """Get the selection coordinates adjusted for window position."""
        if self.selection_start is None or self.selection_current is None:
            return None
            
        # Get coordinates
        x1, y1 = self.selection_start
        x2, y2 = self.selection_current
        
        # Ensure x1,y1 is top-left and x2,y2 is bottom-right
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        # Calculate absolute coordinates
        abs_left = left + self.window_config['left']
        abs_top = top + self.window_config['top']
        abs_right = right + self.window_config['left']
        abs_bottom = bottom + self.window_config['top']
        
        return {
            'mm_left': abs_left,
            'mm_top': abs_top,
            'mm_right': abs_right,
            'mm_bottom': abs_bottom
        }
        
    def save_config(self):
        """Save the current selection to a configuration file."""
        coords = self.get_selection_coords()
        if not coords:
            messagebox.showerror("Error", "No selection made. Please select the minimap first.")
            return
            
        try:
            # Save minimap config
            with open("minimap_config.json", "w") as f:
                json.dump(coords, f, indent=2)
                
            self.minimap_config = coords
            messagebox.showinfo("Success", "Minimap configuration saved successfully!")
            self.status_var.set("Configuration saved. You can now test it or close this tool.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            
    def test_config(self):
        """Test the current minimap configuration."""
        if not self.minimap_config:
            messagebox.showerror("Error", "No minimap configuration available. Please select and save first.")
            return
            
        try:
            with mss.mss() as sct:
                # Create a region dict for mss
                region = {
                    'left': self.minimap_config['mm_left'],
                    'top': self.minimap_config['mm_top'],
                    'width': self.minimap_config['mm_right'] - self.minimap_config['mm_left'],
                    'height': self.minimap_config['mm_bottom'] - self.minimap_config['mm_top']
                }
                
                # Take screenshot of the minimap region
                sct_img = sct.grab(region)
                img = np.array(sct_img)
                
                # Convert BGRA to RGB
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Create a new window to display the minimap
                cv2.namedWindow("Minimap Region", cv2.WINDOW_NORMAL)
                cv2.imshow("Minimap Region", img)
                cv2.waitKey(1)
                
                self.status_var.set("Testing minimap configuration. Close the 'Minimap Region' window when done.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test configuration: {str(e)}")
            
    def run(self):
        """Run the minimap fixer application."""
        self.root.mainloop()
        # Clean up any OpenCV windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    fixer = MinimapFixer()
    fixer.run() 