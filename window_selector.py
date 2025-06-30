#!/usr/bin/env python3
"""
Window Selector for Auto Maple Plus
This tool allows you to quickly select your MapleStory window with a hotkey.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mss
import numpy as np
import cv2
import threading
import time
import json
import os
import sys
from PIL import Image, ImageTk

class EnhancedWindowSelector:
    """
    An improved window selector tool that works with ultrawide monitors and
    multiple display configurations.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced MapleStory Window Selector")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.monitors = []
        self.current_monitor_idx = 0
        self.selection_active = False
        self.selection_start = None
        self.selection_current = None
        self.screenshot = None
        self.screenshot_tk = None
        self.canvas = None
        self.scale_factor = 1.0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create control panel
        control_panel = ttk.Frame(main_frame)
        control_panel.pack(fill=tk.X, side=tk.TOP, pady=5)
        
        # Monitor selection
        ttk.Label(control_panel, text="Select Monitor:").pack(side=tk.LEFT, padx=5)
        self.monitor_var = tk.StringVar()
        self.monitor_combo = ttk.Combobox(control_panel, textvariable=self.monitor_var, state="readonly")
        self.monitor_combo.pack(side=tk.LEFT, padx=5)
        self.monitor_combo.bind("<<ComboboxSelected>>", self.on_monitor_change)
        
        # Buttons
        ttk.Button(control_panel, text="Refresh Monitors", command=self.refresh_monitors).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_panel, text="Take Screenshot", command=self.take_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_panel, text="Save Selection", command=self.save_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_panel, text="Test Config", command=self.test_config).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready. Select a monitor and take a screenshot.")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Selection info
        self.selection_info_var = tk.StringVar(value="No selection")
        selection_info = ttk.Label(main_frame, textvariable=self.selection_info_var, anchor=tk.W)
        selection_info.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Canvas for screenshot
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Canvas scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Canvas events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        
        # Refresh monitor list
        self.refresh_monitors()
        
    def refresh_monitors(self):
        """Refresh the list of available monitors."""
        with mss.mss() as sct:
            self.monitors = sct.monitors
            
        monitor_options = []
        for i, m in enumerate(self.monitors):
            if i == 0:
                monitor_options.append(f"All Monitors Combined ({m['width']}x{m['height']})")
            else:
                monitor_options.append(f"Monitor {i}: {m['width']}x{m['height']} at ({m['left']},{m['top']})")
        
        self.monitor_combo['values'] = monitor_options
        if monitor_options:
            self.monitor_combo.current(0)
            
        self.status_var.set(f"Found {len(self.monitors)-1} monitor(s). Select one and take a screenshot.")
            
    def on_monitor_change(self, event):
        """Handle monitor selection change."""
        idx = self.monitor_combo.current()
        self.current_monitor_idx = idx
        self.status_var.set(f"Selected monitor {idx}. Take a screenshot to continue.")
        
    def take_screenshot(self):
        """Take a screenshot of the selected monitor."""
        if not self.monitors:
            messagebox.showerror("Error", "No monitors detected. Try refreshing the monitor list.")
            return
            
        try:
            with mss.mss() as sct:
                monitor = self.monitors[self.current_monitor_idx]
                sct_img = sct.grab(monitor)
                
                # Convert to numpy array
                img = np.array(sct_img)
                
                # Convert BGRA to RGB for display
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                self.screenshot = img
                self.display_screenshot()
                
                self.status_var.set("Screenshot taken. Draw a rectangle around the MapleStory window.")
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
            
        # Get current scroll position
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
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
        
        # Adjust for monitor position
        monitor = self.monitors[self.current_monitor_idx]
        abs_left = left + monitor['left']
        abs_top = top + monitor['top']
        
        self.selection_info_var.set(
            f"Selection: ({abs_left}, {abs_top}) to ({abs_left + width}, {abs_top + height}), "
            f"Size: {width}x{height}"
        )
        
    def get_selection_coords(self):
        """Get the selection coordinates adjusted for monitor position."""
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
        
        # Adjust for monitor position
        monitor = self.monitors[self.current_monitor_idx]
        abs_left = left + monitor['left']
        abs_top = top + monitor['top']
        width = right - left
        height = bottom - top
        
        return {
            'left': abs_left,
            'top': abs_top,
            'width': width,
            'height': height,
            'monitor_idx': self.current_monitor_idx
        }
        
    def save_selection(self):
        """Save the current selection to a configuration file."""
        coords = self.get_selection_coords()
        if not coords:
            messagebox.showerror("Error", "No selection made. Please select the MapleStory window first.")
            return
            
        try:
            # Save window config
            with open("window_config.json", "w") as f:
                json.dump(coords, f, indent=2)
                
            # Also save to settings.py if it exists
            self.update_settings_file(coords)
                
            messagebox.showinfo("Success", "Window configuration saved successfully!")
            self.status_var.set("Configuration saved. You can now test it or close this tool.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            
    def update_settings_file(self, coords):
        """Update the settings.py file with manual window position."""
        try:
            settings_file = "src/common/settings.py"
            if not os.path.exists(settings_file):
                return
                
            with open(settings_file, "r") as f:
                content = f.readlines()
                
            # Find or add use_manual_window_position setting
            manual_pos_found = False
            window_left_found = False
            window_top_found = False
            window_width_found = False
            window_height_found = False
            
            for i, line in enumerate(content):
                if "use_manual_window_position" in line and "=" in line:
                    content[i] = f"use_manual_window_position = True  # Modified by window selector\n"
                    manual_pos_found = True
                elif "maple_window_left" in line and "=" in line:
                    content[i] = f"maple_window_left = {coords['left']}  # Modified by window selector\n"
                    window_left_found = True
                elif "maple_window_top" in line and "=" in line:
                    content[i] = f"maple_window_top = {coords['top']}  # Modified by window selector\n"
                    window_top_found = True
                elif "maple_window_width" in line and "=" in line:
                    content[i] = f"maple_window_width = {coords['width']}  # Modified by window selector\n"
                    window_width_found = True
                elif "maple_window_height" in line and "=" in line:
                    content[i] = f"maple_window_height = {coords['height']}  # Modified by window selector\n"
                    window_height_found = True
                    
            # Add settings if not found
            if not manual_pos_found:
                content.append(f"use_manual_window_position = True  # Added by window selector\n")
            if not window_left_found:
                content.append(f"maple_window_left = {coords['left']}  # Added by window selector\n")
            if not window_top_found:
                content.append(f"maple_window_top = {coords['top']}  # Added by window selector\n")
            if not window_width_found:
                content.append(f"maple_window_width = {coords['width']}  # Added by window selector\n")
            if not window_height_found:
                content.append(f"maple_window_height = {coords['height']}  # Added by window selector\n")
                
            # Write back to file
            with open(settings_file, "w") as f:
                f.writelines(content)
                
        except Exception as e:
            print(f"Warning: Could not update settings.py: {str(e)}")
            
    def test_config(self):
        """Test the current configuration by displaying the selected region."""
        coords = self.get_selection_coords()
        if not coords:
            messagebox.showerror("Error", "No selection made. Please select the MapleStory window first.")
            return
            
        try:
            with mss.mss() as sct:
                # Create a region dict for mss
                region = {
                    'left': coords['left'],
                    'top': coords['top'],
                    'width': coords['width'],
                    'height': coords['height']
                }
                
                # Take screenshot of the region
                sct_img = sct.grab(region)
                img = np.array(sct_img)
                
                # Convert BGRA to RGB
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Create a new window to display the region
                cv2.namedWindow("Selected Region", cv2.WINDOW_NORMAL)
                cv2.imshow("Selected Region", img)
                cv2.waitKey(1)
                
                self.status_var.set("Testing configuration. Close the 'Selected Region' window when done.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test configuration: {str(e)}")
            
    def run(self):
        """Run the window selector application."""
        self.root.mainloop()
        # Clean up any OpenCV windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    selector = EnhancedWindowSelector()
    selector.run() 