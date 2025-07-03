"""An interpreter that reads and executes user-created routines."""

import threading
import time
import git
import cv2
import inspect
import importlib
import traceback
from src.common.arduino_input import press
from os.path import splitext, basename
from src.common import config, utils
from src.routine import components
from src.routine.routine import Routine
from src.command_book.command_book import CommandBook
from src.routine.components import Point
from src.common.interfaces import Configurable
from src.runesolvercore.runesolver import enterCashshop
import numpy as np

# Import the RuneSolver class functionality
import src.runesolvercore.runesolver as runesolver

# The rune's buff icon
RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)


class Bot(Configurable):
    """A class that interprets and executes user-defined routines."""

    DEFAULT_CONFIG = {
        'NPC/Gather': 'y',
        'Feed pet': '9',
        'Cash Shop': '`',
        '2x EXP Buff': '7',
        'Mushroom Buff': '8',
        'Additional EXP Buff': '9',
        'Gold Pot': '10',
        'Wealth Acquisition': '-'
    }

    def __init__(self):
        """Loads a user-defined routine on start up and initializes this Bot's main thread."""

        super().__init__('keybindings')
        config.bot = self

        # Simple rune solving variables (original approach)
        self.rune_pos = (0, 0)
        self.rune_closest_pos = (0, 0)
        
        self.submodules = []
        self.command_book = None            # CommandBook instance
        
        # Cached settings to avoid Tkinter threading issues
        self.cached_settings = {
            'auto_feed': False,
            'num_pets': 1,
            'auto_buff_exp': False,
            'expbuff_use_interval': 1,
            'cs_reset_toggle': False,
            'cs_reset_interval': 1
        }
        
        self.last_settings_update = 0
        self.settings_update_interval = 5  # Update settings every 5 seconds
        
        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Bot object's main thread.
        """
        print('\n[~] Starting bot')
        self.ready = True
        
        # Load command book
        config.routine = Routine()
        # Don't set command_book here - it will be set when load_commands is called
        
        # Start main thread
        t = threading.Thread(target=self._main, daemon=True)
        t.start()

    def _update_settings_cache(self):
        """Update cached settings from the GUI to avoid threading issues."""
        try:
            if hasattr(config, 'gui') and config.gui:
                # Access settings through the correct GUI structure
                if hasattr(config.gui, 'settings'):
                    # Access pet settings
                    if hasattr(config.gui.settings, 'pets'):
                        self.cached_settings['auto_feed'] = config.gui.settings.pets.auto_feed.get()
                        self.cached_settings['num_pets'] = config.gui.settings.pets.num_pets.get()
                    
                    # Access exp buff settings
                    if hasattr(config.gui.settings, 'expbuffsettings'):
                        self.cached_settings['auto_buff_exp'] = config.gui.settings.expbuffsettings.expbuff_use_toggle.get()
                        self.cached_settings['expbuff_use_interval'] = config.gui.settings.expbuffsettings.expbuff_use_interval.get()
                    
                    # Access misc settings
                    if hasattr(config.gui.settings, 'miscsettings'):
                        self.cached_settings['cs_reset_toggle'] = config.gui.settings.miscsettings.cs_reset_toggle.get()
                        self.cached_settings['cs_reset_interval'] = config.gui.settings.miscsettings.cs_reset_interval.get()
        except Exception as e:
            print(f"[WARN] Failed to update settings cache: {e}")

    def _main(self):
        """
        The main body of Bot that executes the user's routine.
        :return:    None
        """
        self.ready = True
        config.listener.enabled = True
        last_fed = time.time()
        last_enteredCS = time.time()
        last_30m_expbuffed = None
        
        while True:
            if config.enabled and len(config.routine) > 0:
                # Update settings cache periodically
                now = time.time()
                if now - self.last_settings_update > self.settings_update_interval:
                    if hasattr(config, 'gui') and config.gui:
                        config.gui.root.after_idle(self._update_settings_cache)
                    self.last_settings_update = now
                
                # Auto-feed pets
                if self.cached_settings['auto_feed'] and now - last_fed > 1200:
                    last_fed = now
                    self.feed_pets()
                
                # Auto buff EXP
                if self.cached_settings['auto_buff_exp']:
                    expbuff_interval = self.cached_settings['expbuff_use_interval'] * 60  # Convert to seconds
                    
                    if last_30m_expbuffed is None or (now - last_30m_expbuffed) >= expbuff_interval:
                        last_30m_expbuffed = now
                        if hasattr(self, 'buff') and self.buff:
                            # Use the buff command from command book if available
                            if hasattr(self.buff, 'main'):
                                self.buff.main()
                            else:
                                print("[WARN] Buff command not properly initialized")
                
                # CS reset functionality
                if self.cached_settings['cs_reset_toggle']:
                    cs_reset_interval = self.cached_settings['cs_reset_interval'] * 60
                    if now - last_enteredCS > cs_reset_interval:
                        last_enteredCS = now
                        config.enabled = False
                        time.sleep(1)
                        runesolver.enterCashshop()
                        time.sleep(1)
                        config.enabled = True
                
                # Execute routine sequence
                self._execute_routine_sequence()
                
            else:
                time.sleep(0.1)

    def _execute_routine_sequence(self):
        """Execute the routine sequence with rune detection (original approach)."""
        # Highlight the current Point in GUI
        config.gui.root.after(0, config.gui.view.routine.select, config.routine.index)
        config.gui.root.after(0, config.gui.view.details.display_info, config.routine.index)
        
        # Get current routine element
        element = config.routine[config.routine.index]
        
        # Check for rune before executing the routine element
        if not config.rune_cd and self._should_solve_rune():
            # Calculate distance to rune from all routine points
            distances = [utils.distance(self.rune_pos, config.routine[i].location) 
                        for i in range(len(config.routine))]
            closest_index = np.argmin(distances)
            self.rune_closest_pos = config.routine[closest_index].location
            
            # If we're at the closest point to the rune, solve it
            if isinstance(element, Point) and element.location == self.rune_closest_pos:
                self._solve_rune()
        
        # Execute the routine element
        element.execute()
        
        # Step to next routine element
        config.routine.step()

    def _should_solve_rune(self):
        """Check if we should solve a rune (original approach - direct capture check)."""
        try:
            # Direct check of capture system's rune detection
            if (hasattr(config.capture, 'minimap') and 
                config.capture.minimap and 
                config.capture.minimap.get('rune_active', False)):
                
                rune_pos = config.capture.minimap.get('rune_pos', None)
                if rune_pos:
                    # Convert relative position to absolute position if needed
                    if config.capture.minimap_sample is not None:
                        self.rune_pos = utils.convert_to_absolute(rune_pos, config.capture.minimap_sample)
                    else:
                        self.rune_pos = rune_pos
                    return True
            return False
        except Exception as e:
            print(f"[WARN] Error checking rune status: {e}")
            return False

    @utils.run_if_enabled
    def _solve_rune(self):
        """
        Moves to the position of the rune and solves the arrow-key puzzle.
        :param model:   The TensorFlow model to classify with.
        :param sct:     The mss instance object with which to take screenshots.
        :return:        None
        """
        
        # Check if command book is properly loaded
        if not self.command_book:
            print("[ERROR] Command book not properly loaded for rune solving")
            return
            
        # Use the command book's move and adjust commands (CommandBook provides dict interface)
        if 'move' in self.command_book:
            move = self.command_book['move']
            move(*self.rune_pos).execute()
        
        if 'adjust' in self.command_book:
            adjust = self.command_book['adjust']
            adjust(*self.rune_pos).execute()
        
        time.sleep(0.5)
        print('\nSolving rune:')
        
        # Create a comprehensive config wrapper for rune solver
        class RuneSolverConfig:
            def __init__(self, bot_config):
                self.config = bot_config
                # Add hwnd for compatibility (not actually used with MSS capture)
                self.hwnd = None
                # Add window boundaries (not used with current MSS implementation)
                self.left = 0
                self.top = 0
                self.right = 100
                self.bottom = 100
        
        solver_instance = RuneSolverConfig(self.config)
        result = runesolver.solve_rune_raw(solver_instance)
        
        if result:
            print("Rune solved successfully!")
        else:
            print("Rune solving failed")
            
        self.rune_pos = (0, 0)
        self.rune_closest_pos = (0, 0)

    def load_commands(self, file):
        try:
            # Create CommandBook instance - this handles all the loading logic
            command_book = CommandBook(file)
            
            # Set up the bot interface as originally designed
            self.command_book = command_book  # The wrapper that provides dict interface
            self.buff = command_book.buff     # Direct buff access 
            self.module_name = command_book.name
            
            # Update GUI settings if available
            if hasattr(config, 'gui') and config.gui is not None:
                config.gui.root.after(0, config.gui.settings.update_class_bindings)
        except ValueError as e:
            print(f"[ERROR] Failed to load command book: {e}")
            pass    # TODO: UI warning popup, say check cmd for errors

    def update_submodules(self, force=False):
        """
        Pulls updates from the submodule repositories. If FORCE is True,
        rebuilds submodules by overwriting all local changes.
        """

        utils.print_separator()
        print('[~] Retrieving latest submodules:')
        self.submodules = []
        repo = git.Repo.init()
        with open('.gitmodules', 'r') as file:
            lines = file.readlines()
            i = 0
            while i < len(lines):
                if lines[i].startswith('[') and i < len(lines) - 2:
                    path = lines[i + 1].split('=')[1].strip()
                    url = lines[i + 2].split('=')[1].strip()
                    self.submodules.append(path)
                    try:
                        repo.git.clone(url, path)       # First time loading submodule
                        print(f" -  Initialized submodule '{path}'")
                    except git.exc.GitCommandError:
                        sub_repo = git.Repo(path)
                        if not force:
                            sub_repo.git.stash()        # Save modified content
                        sub_repo.git.fetch('origin', 'main')
                        sub_repo.git.reset('--hard', 'FETCH_HEAD')
                        if not force:
                            try:                # Restore modified content
                                sub_repo.git.checkout('stash', '--', '.')
                                print(f" -  Updated submodule '{path}', restored local changes")
                            except git.exc.GitCommandError:
                                print(f" -  Updated submodule '{path}'")
                        else:
                            print(f" -  Rebuilt submodule '{path}'")
                        sub_repo.git.stash('clear')
                    i += 3
                else:
                    i += 1

    def feed_pets(self):
        """Feed pets using Arduino input."""
        from src.common.arduino_input import press
        num_pets = self.cached_settings['num_pets']
        for _ in range(num_pets):
            press(self.config['Feed pet'], 1)
            time.sleep(0.1)
