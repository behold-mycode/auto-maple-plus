"""User friendly GUI to interact with Auto Maple."""

import time
import threading
import tkinter as tk
from tkinter import ttk
from src.common import config, settings
from src.gui import Menu, View, Edit, Settings, Notifer_Settings, Runtime_Flags, Automation_Settings
from src.gui.menu.file import Import_Settings

class GUI:
    DISPLAY_FRAME_RATE = 30
    RESOLUTIONS = {
        'DEFAULT': '800x800',
        'Edit': '1300x750',
        'Settings': '750x850',
        'Notifier': '600x775',
        'Monitoring': '400x575',
        'Automation': '400x525'
    }

    def __init__(self):
        config.gui = self

        self.root = tk.Tk()
        self.root.title('Auto Maple')
        icon = tk.PhotoImage(file='assets/icon.png')
        self.root.iconphoto(False, icon)
        self.root.geometry(GUI.RESOLUTIONS['DEFAULT'])
        # Force window to laptop monitor using macOS-specific approach
        # Center the window on the laptop monitor (0-2560 range)
        window_width = 1200  # Approximate GUI width
        window_height = 800  # Approximate GUI height
        laptop_center_x = 1280  # Center of laptop monitor (2560/2)
        laptop_center_y = 720   # Center of laptop monitor (1440/2)
        x = laptop_center_x - (window_width // 2)
        y = laptop_center_y - (window_height // 2)
        self.root.geometry(f"{GUI.RESOLUTIONS['DEFAULT']}+{x}+{y}")
        self.root.resizable(False, False)

        # Initialize GUI variables
        self.routine_var = tk.StringVar()

        # Build the GUI
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.navigation = ttk.Notebook(self.root)

        self.view = View(self.navigation)
        self.edit = Edit(self.navigation)
        self.settings = Settings(self.navigation)
        self.watcher_settings = Notifer_Settings(self.navigation)
        self.runtime_console = Runtime_Flags(self.navigation)
        self.automation_settings = Automation_Settings(self.navigation)

        self.navigation.pack(expand=True, fill='both')
        self.navigation.bind('<<NotebookTabChanged>>', self._resize_window)
        self.root.focus()

    def set_routine(self, arr):
        self.routine_var.set(arr)

    def clear_routine_info(self):
        """
        Clears information in various GUI elements regarding the current routine.
        Does not clear Listboxes containing routine Components, as that is handled by Routine.
        """

        self.view.details.clear_info()
        self.view.status.set_routine('')

        self.edit.minimap.redraw()
        self.edit.routine.commands.clear_contents()
        self.edit.routine.commands.update_display()
        self.edit.editor.reset()

    def _resize_window(self, e):
        """Callback to resize entire Tkinter window every time a new Page is selected."""

        nav = e.widget
        curr_id = nav.select()
        nav.nametowidget(curr_id).focus()      # Focus the current Tab
        page = nav.tab(curr_id, 'text')
        if self.root.state() != 'zoomed':
            if page in GUI.RESOLUTIONS:
                # Keep window on laptop monitor when switching tabs
                window_width = 1200
                window_height = 800
                laptop_center_x = 1280
                laptop_center_y = 720
                x = laptop_center_x - (window_width // 2)
                y = laptop_center_y - (window_height // 2)
                self.root.geometry(f"{GUI.RESOLUTIONS[page]}+{x}+{y}")
            else:
                # Keep window on laptop monitor when switching tabs
                window_width = 1200
                window_height = 800
                laptop_center_x = 1280
                laptop_center_y = 720
                x = laptop_center_x - (window_width // 2)
                y = laptop_center_y - (window_height // 2)
                self.root.geometry(f"{GUI.RESOLUTIONS['DEFAULT']}+{x}+{y}")

    def start(self):
        """Starts the GUI as well as any scheduled functions."""

        # Start GUI background threads using Tkinter's after() for thread safety
        self.root.after(200, self._start_background_threads)

        # Load previously used config after a delay to ensure bot is ready
        self.root.after(1000, self._load_previous_config)
            
        self.root.mainloop()

    def _start_background_threads(self):
        """Start GUI background threads safely after mainloop is running."""
        
        # Start display thread
        display_thread = threading.Thread(target=self._display_minimap)
        display_thread.daemon = True
        display_thread.start()

        # Start layout thread
        layout_thread = threading.Thread(target=self._save_layout)
        layout_thread.daemon = True
        layout_thread.start()

    def _display_minimap(self):
        delay = 1 / GUI.DISPLAY_FRAME_RATE
        while True:
            self.view.minimap.display_minimap()
            time.sleep(delay)

    def _save_layout(self):
        """Periodically saves the current Layout object."""

        while True:
            if config.layout is not None and settings.record_layout:
                config.layout.save()
            time.sleep(5)

    def _load_previous_config(self):
        """Load previously used command book and routine after bot is ready."""
        print("[~] Attempting to load last used command book and routine")
        import_root = Import_Settings("CBR")
        last_cb = import_root.get("last_cb")
        last_routine = import_root.get("last_routine")
        if last_cb != None:
            print()
            try:
                if hasattr(config, 'bot') and config.bot:
                    config.bot.load_commands(last_cb)
                    if last_routine != None:
                       config.routine.load(last_routine)
            except Exception as e:
                print(f"[WARN] Failed to load previous config: {e}")
        else:
            print("[!] Last loaded command book not found)")


if __name__ == '__main__':
    gui = GUI()
    gui.start()
