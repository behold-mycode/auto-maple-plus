"""A key listener to track user inputs."""

import config
import time
import utils
import threading
import keyboard as kb
from bot import Bot


class Listener:
    def __init__(self):
        """Initializes this Listener object's main thread."""

        self.thread = threading.Thread(target=Listener._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts listening to user inputs.
        :return:    None
        """

        print('\nStarted keyboard listener.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly listens for user inputs and updates variables in config accordingly.
        :return:    None
        """

        while True:
            if config.listening:
                if kb.is_pressed('insert'):
                    Bot.toggle_enabled()
                    time.sleep(0.667)
                elif kb.is_pressed('F6'):
                    Bot.load_routine(config.routine)
                elif kb.is_pressed('F7'):
                    Bot.load_commands()
                    Bot.load_routine()
                elif kb.is_pressed('F8'):
                    displayed_pos = tuple('{:.3f}'.format(round(i, 3)) for i in config.player_pos)
                    utils.print_separator()
                    print(f'Current position: ({displayed_pos[0]}, {displayed_pos[1]})')
                    time.sleep(1)
            time.sleep(0.01)
