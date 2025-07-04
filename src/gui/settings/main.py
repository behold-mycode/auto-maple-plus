"""Displays Auto Maple's current settings and allows the user to edit them."""

import tkinter as tk
from src.gui.interfaces import KeyBindings
from src.gui.settings.pets import Pets
from src.gui.settings.expbuffsettings import ExpBuff
from src.gui.settings.miscsettings import Misc
from src.gui.interfaces import Tab, Frame
from src.common import config
from src.common.interfaces import Configurable


class Settings(Tab):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Settings', **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)

        self.column1 = Frame(self)
        self.column1.grid(row=0, column=1, sticky=tk.N, padx=10, pady=10)
        self.controls = KeyBindings(self.column1, 'Auto Maple Controls', config.listener)
        self.controls.pack(side=tk.TOP, fill='x', expand=True)
        self.common_bindings = KeyBindings(self.column1, 'In-game Keybindings', config.bot)
        self.common_bindings.pack(side=tk.TOP, fill='x', expand=True, pady=(10, 0))
        self.expbuffsettings = ExpBuff(self.column1)
        self.expbuffsettings.pack(side=tk.TOP, fill='x', expand=True, pady=(10, 0))
        self.miscsettings = Misc(self.column1)
        self.miscsettings.pack(side=tk.TOP, fill='x', expand=True, pady=(10, 0))
        self.pets = Pets(self.column1)
        self.pets.pack(side=tk.TOP, fill='x', expand=True, pady=(10, 0))

        self.column2 = Frame(self)
        self.column2.grid(row=0, column=2, sticky=tk.N, padx=10, pady=10)
        self.class_bindings = KeyBindings(self.column2, f'No Command Book Selected', None)
        self.class_bindings.pack(side=tk.TOP, fill='x', expand=True)

    def update_class_bindings(self):
        self.class_bindings.destroy()
        
        # Check if command book is properly loaded
        if (config.bot and 
            hasattr(config.bot, 'command_book') and 
            config.bot.command_book and
            hasattr(config.bot, 'module_name')):
            class_name = config.bot.module_name.capitalize()
            # Use the CommandBook instance directly - it's already a Configurable
            self.class_bindings = KeyBindings(self.column2, f'{class_name} Keybindings', config.bot.command_book)
        else:
            self.class_bindings = KeyBindings(self.column2, f'No Command Book Selected', None)
        
        self.class_bindings.pack(side=tk.TOP, fill='x', expand=True)
