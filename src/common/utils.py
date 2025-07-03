import cv2
import numpy as np
from src.common import config


def single_match(frame, template, threshold=0.8):
    """
    Finds the first match of TEMPLATE in FRAME above the given threshold.
    :param frame:      The image to search in.
    :param template:   The template to search for.
    :param threshold:  The minimum similarity score to consider a match.
    :return:          The first match coordinates (x, y) or None if no match found.
    """
    
    try:
        # Ensure both frame and template are grayscale uint8
        if len(frame.shape) == 3:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            frame_gray = frame.astype(np.uint8)
            
        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template.astype(np.uint8)
        
        result = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            return max_loc
        return None
    except Exception as e:
        print(f"[WARN] Single match failed: {e}")
        return None


def multi_match(frame, template, threshold=0.8):
    """
    Finds all matches of TEMPLATE in FRAME above the given threshold.
    :param frame:      The image to search in.
    :param template:   The template to search for.
    :param threshold:  The minimum similarity score to consider a match.
    :return:          List of match coordinates [(x, y), ...].
    """
    
    try:
        # Ensure both frame and template are grayscale uint8
        if len(frame.shape) == 3:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            frame_gray = frame.astype(np.uint8)
            
        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template.astype(np.uint8)
        
        result = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matches = list(zip(*locations[::-1]))  # Convert to (x, y) format
        return matches
    except Exception as e:
        print(f"[WARN] Multi match failed: {e}")
        return []


def convert_to_relative(point, img):
    """
    Converts absolute coordinates to relative coordinates (0-1 range).
    :param point: The absolute coordinates (x, y).
    :param img:   The image to get dimensions from.
    :return:      Relative coordinates (x, y) in 0-1 range.
    """
    height, width = img.shape[:2]
    return (point[0] / width, point[1] / height)


def convert_to_absolute(point, img):
    """
    Converts relative coordinates to absolute coordinates.
    :param point: The relative coordinates (x, y) in 0-1 range.
    :param img:   The image to get dimensions from.
    :return:      Absolute coordinates (x, y).
    """
    height, width = img.shape[:2]
    return (int(point[0] * width), int(point[1] * height))


def draw_location(img, location, color):
    """
    Draws a circle at the given location on the image.
    :param img:      The image to draw on.
    :param location: The location to draw at (relative coordinates).
    :param color:    The color to draw in BGR format.
    """
    try:
        point = convert_to_absolute(location, img)
        cv2.circle(img, point, 3, color, -1)
    except Exception as e:
        print(f"[WARN] Failed to draw location: {e}")

import math
import queue
import cv2
import threading
import numpy as np
from src.common import config, settings
from random import random


def run_if_enabled(function):
    """
    Decorator for functions that should only run if the bot is enabled.
    :param function:    The function to decorate.
    :return:            The decorated function.
    """

    def helper(*args, **kwargs):
        if config.enabled:
            return function(*args, **kwargs)
    return helper


def run_if_disabled(message=''):
    """
    Decorator for functions that should only run while the bot is disabled. If MESSAGE
    is not empty, it will also print that message if its function attempts to run when
    it is not supposed to.
    """

    def decorator(function):
        def helper(*args, **kwargs):
            if not config.enabled:
                return function(*args, **kwargs)
            elif message:
                print(message)
        return helper
    return decorator


def distance(a, b):
    """
    Applies the distance formula to two points.
    :param a:   The first point.
    :param b:   The second point.
    :return:    The distance between the two points.
    """

    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def separate_args(arguments):
    """
    Separates a given array ARGUMENTS into an array of normal arguments and a
    dictionary of keyword arguments.
    :param arguments:    The array of arguments to separate.
    :return:             An array of normal arguments and a dictionary of keyword arguments.
    """

    args = []
    kwargs = {}
    for a in arguments:
        a = a.strip()
        index = a.find('=')
        if index > -1:
            key = a[:index].strip()
            value = a[index+1:].strip()
            kwargs[key] = value
        else:
            args.append(a)
    return args, kwargs


def filter_color(img, ranges):
    """
    Returns a filtered copy of IMG that only contains pixels within the given RANGES.
    on the HSV scale.
    :param img:     The image to filter.
    :param ranges:  A list of tuples, each of which is a pair upper and lower HSV bounds.
    :return:        A filtered copy of IMG.
    """

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, ranges[0][0], ranges[0][1])
    for i in range(1, len(ranges)):
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, ranges[i][0], ranges[i][1]))

    # Mask the image
    color_mask = mask > 0
    result = np.zeros_like(img, np.uint8)
    result[color_mask] = img[color_mask]
    return result


def print_separator():
    """Prints a 3 blank lines for visual clarity."""

    print('\n\n')


def print_state():
    """Prints whether Auto Maple is currently enabled or disabled."""

    print_separator()
    print('#' * 18)
    print(f"#    {'ENABLED ' if config.enabled else 'DISABLED'}    #")
    print('#' * 18)


def closest_point(points, target):
    """
    Returns the point in POINTS that is closest to TARGET.
    :param points:      A list of points to check.
    :param target:      The point to check against.
    :return:            The point closest to TARGET, otherwise None if POINTS is empty.
    """

    if points:
        points.sort(key=lambda p: distance(p, target))
        return points[0]


def bernoulli(p):
    """
    Returns the value of a Bernoulli random variable with probability P.
    :param p:   The random variable's probability of being True.
    :return:    True or False.
    """

    return random() < p


def rand_float(start, end):
    """Returns a random float value in the interval [START, END)."""

    assert start < end, 'START must be less than END'
    return (end - start) * random() + start


##########################
#       Threading        #
##########################
class Async(threading.Thread):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.queue = queue.Queue()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)
        self.queue.put('x')

    def process_queue(self, root):
        def f():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                root.after(100, self.process_queue(root))
        return f


def async_callback(context, function, *args, **kwargs):
    """Returns a callback function that can be run asynchronously by the GUI."""

    def f():
        task = Async(function, *args, **kwargs)
        task.start()
        context.after(100, task.process_queue(context))
    return f
