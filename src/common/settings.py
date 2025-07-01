"""
A list of user-defined settings that can be changed by routines. Also contains a collection
of validator functions that can be used to enforce parameter types.
"""


#################################
#      Validator Functions      #
#################################
def validate_nonnegative_int(value):
    """
    Checks whether VALUE can be a valid non-negative integer.
    :param value:   The string to check.
    :return:        VALUE as an integer.
    """

    if int(value) >= 1:
        return int(value)
    raise ValueError(f"'{value}' is not a valid non-negative integer.")


def validate_boolean(value):
    """
    Checks whether VALUE is a valid Python boolean.
    :param value:   The string to check.
    :return:        VALUE as a boolean
    """

    value = value.lower()
    if value in {'true', 'false'}:
        return True if value == 'true' else False
    elif int(value) in {0, 1}:
        return bool(int(value))
    raise ValueError(f"'{value}' is not a valid boolean.")


def validate_arrows(key):
    """
    Checks whether string KEY is an arrow key.
    :param key:     The key to check.
    :return:        KEY in lowercase if it is a valid arrow key.
    """

    if isinstance(key, str):
        key = key.lower()
        if key in ['up', 'down', 'left', 'right']:
            return key
    raise ValueError(f"'{key}' is not a valid arrow key.")


def validate_horizontal_arrows(key):
    """
    Checks whether string KEY is either a left or right arrow key.
    :param key:     The key to check.
    :return:        KEY in lowercase if it is a valid horizontal arrow key.
    """

    if isinstance(key, str):
        key = key.lower()
        if key in ['left', 'right']:
            return key
    raise ValueError(f"'{key}' is not a valid horizontal arrow key.")


#########################
#       Settings        #
#########################
# A dictionary that maps each setting to its validator function
SETTING_VALIDATORS = {
    'move_tolerance': float,
    'adjust_tolerance': float,
    'record_layout': validate_boolean,
    'buff_cooldown': validate_nonnegative_int
}


def reset():
    """Resets all settings to their default values."""

    global move_tolerance, adjust_tolerance, record_layout, buff_cooldown
    global arduino_port, arduino_baud
    global maple_window_left, maple_window_top, maple_window_width, maple_window_height
    global use_manual_window_position, use_hotkey_window_selection
    
    move_tolerance = 0.075
    adjust_tolerance = 0.01
    record_layout = False
    buff_cooldown = 180
    
    # Arduino Configuration
    arduino_port = "/dev/cu.usbmodemHIDPC1"
    arduino_baud = 115200
    
    # Window Position Configuration
use_manual_window_position = True  # Modified by window selector
use_hotkey_window_selection = True
maple_window_left = 1727  # Modified by window selector
maple_window_top = 318  # Modified by window selector
maple_window_width = 1366  # Modified by window selector
maple_window_height = 768  # Modified by window selector


# The allowed error from the destination when moving towards a Point
move_tolerance = 0.075

# The allowed error from a specific location while adjusting to that location
adjust_tolerance = 0.01

# Whether the bot should save new player positions to the current layout
record_layout = False

# The amount of time (in seconds) to wait between each call to the 'buff' command
buff_cooldown = 180

# === Arduino Configuration ===
# Serial port for Arduino (auto-detected if None)
arduino_port = "/dev/cu.usbmodemHIDPC1"

# Baud rate for Arduino serial communication
arduino_baud = 115200

# === Window Position Configuration ===
# Set to True to use manual window position instead of auto-detection
use_manual_window_position = True  # Modified by window selector

# Set to True to enable hotkey window selection (press F12 to select window)
use_hotkey_window_selection = True

# These are the coordinates of your MapleStory window on screen
maple_window_left = 4896  # Modified by window selector
maple_window_top = 595  # Modified by window selector
maple_window_width = 2723  # Modified by window selector
maple_window_height = 1540  # Modified by window selector

reset()