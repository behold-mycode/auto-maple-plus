import time
import src.runesolvercore.gdi_capture as gdi_capture
from src.common.arduino_input import press
import numpy as np
import cv2 as cv
import mss
import src.common.utils as utils
import src.common.config as config
import math
import os

# Try to import TensorFlow, but make it optional
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("[INFO] TensorFlow not available, using computer vision method for rune solving")

# DEFINE CV Variables
RUNE_BGRA = (255, 102, 221, 255)
INSIDE_CS_TEMPLATE = cv.imread('assets/insidecashshop.png', 0)
CS_FAIL_TEMPLATE = cv.imread('assets/csFail.png',0)

# TensorFlow model for rune solving (only if TensorFlow is available)
class RuneSolverML:
    def __init__(self):
        self.model = None
        self.label_map = None
        self.model_loaded = False
        if TENSORFLOW_AVAILABLE:
            self.load_model()
    
    def load_model(self):
        """Load the TensorFlow model for rune solving."""
        if not TENSORFLOW_AVAILABLE:
            return False
            
        try:
            # Try to load the synthetic model we created
            synthetic_model_path = 'assets/models/rune_solver_model.h5'
            if os.path.exists(synthetic_model_path):
                self.model = tf.keras.models.load_model(synthetic_model_path)
                self.model_loaded = True
                print("[INFO] Loaded synthetic TensorFlow model for rune solving")
                return True
            
            # Try to load the best model from root directory
            best_model_path = 'best_rune_model.h5'
            if os.path.exists(best_model_path):
                self.model = tf.keras.models.load_model(best_model_path)
                self.model_loaded = True
                print("[INFO] Loaded best TensorFlow model for rune solving")
                return True
            
            # Try to load SavedModel format as fallback
            saved_model_path = 'assets/models/rune_model_rnn_filtered_cannied/saved_model'
            if os.path.exists(saved_model_path):
                self.model = tf.saved_model.load(saved_model_path)
                self.model_loaded = True
                print("[INFO] Loaded TensorFlow SavedModel for rune solving")
                return True
            
            # Try to load .h5 format as final fallback
            model_path = 'assets/models/rune_model.h5'
            label_map_path = 'assets/label_map.pbtxt'
            
            if os.path.exists(model_path) and os.path.exists(label_map_path):
                self.model = tf.keras.models.load_model(model_path)
                self.label_map = self.load_label_map(label_map_path)
                self.model_loaded = True
                print("[INFO] Loaded existing TensorFlow .h5 model")
                return True
            else:
                print("[INFO] No existing TensorFlow model found, using computer vision method")
                return False
        except Exception as e:
            print(f"[WARNING] Failed to load TensorFlow model: {e}")
            return False
    
    def load_label_map(self, label_map_path):
        """Load the label map for the model."""
        try:
            label_map = {}
            with open(label_map_path, 'r') as f:
                for line in f:
                    if 'id:' in line and 'name:' in line:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            id_val = int(parts[1])
                            name = parts[3].strip('"')
                            label_map[id_val] = name
            return label_map
        except Exception as e:
            print(f"[WARNING] Failed to load label map: {e}")
            return {}
    
    def predict_arrow_direction(self, image):
        """Predict arrow direction using TensorFlow model."""
        if not self.model_loaded or not TENSORFLOW_AVAILABLE:
            return None
            
        try:
            # Preprocess image for model
            processed_image = self.preprocess_image(image)
            if processed_image is None:
                return None
            
            # Make prediction based on model type
            if hasattr(self.model, 'predict'):
                # Keras model
                prediction = self.model.predict(processed_image, verbose=0)
                predicted_class = np.argmax(prediction[0])
            else:
                # SavedModel - try to call it directly
                prediction = self.model(processed_image)
                if isinstance(prediction, dict):
                    # If prediction is a dict, get the output tensor
                    output_key = list(prediction.keys())[0]
                    prediction = prediction[output_key]
                predicted_class = np.argmax(prediction.numpy()[0])
            
            # Map prediction to direction
            directions = ['up', 'down', 'left', 'right']
            if predicted_class < len(directions):
                return directions[predicted_class]
            else:
                return None
        except Exception as e:
            print(f"[WARNING] TensorFlow prediction failed: {e}")
            return None
    
    def preprocess_image(self, image):
        """Preprocess image for TensorFlow model."""
        try:
            # Resize to model input size (assuming 64x64)
            resized = cv.resize(image, (64, 64))
            
            # Convert to RGB if needed
            if len(resized.shape) == 3:
                resized = cv.cvtColor(resized, cv.COLOR_BGR2RGB)
            
            # Normalize pixel values
            normalized = resized.astype(np.float32) / 255.0
            
            # Add batch dimension
            batched = np.expand_dims(normalized, axis=0)
            
            return batched
        except Exception as e:
            print(f"[WARNING] Image preprocessing failed: {e}")
            return None

# Initialize ML solver
ml_solver = RuneSolverML()

def solve_rune_raw():
    """Solves rune puzzles using either ML or computer vision."""
    # Try ML method first if available
    if ml_solver.model_loaded:
        # Capture rune area
        rune_area = capture_rune_area()
        if rune_area is not None:
            # Try ML prediction
            direction = ml_solver.predict_arrow_direction(rune_area)
            if direction:
                print(f"[ML] Predicted arrow direction: {direction}")
                return direction
    
    # Fall back to computer vision method
    return solve_rune_cv()

def capture_rune_area():
    """Capture the rune area for ML processing."""
    try:
        # Capture screen area where rune appears
        with mss.mss() as sct:
            # Adjust these coordinates based on your screen resolution
            monitor = {"top": 200, "left": 400, "width": 200, "height": 200}
            screenshot = sct.grab(monitor)
            image = np.array(screenshot)
            
            # Convert to BGR for OpenCV
            image = cv.cvtColor(image, cv.COLOR_BGRA2BGR)
            return image
    except Exception as e:
        print(f"[WARNING] Failed to capture rune area: {e}")
        return None

def solve_rune_cv():
    """Original computer vision method for rune solving."""
    # Original rune solving logic here
    # This is the fallback method when ML is not available
    
    # For now, return a default direction
    # You can implement the original CV logic here
    return 'up'

def find_arrow_directions(img, debug=False):
    bgr = cv.cvtColor(img, cv.COLOR_BGRA2BGR)
    hsv = cv.cvtColor(bgr, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv)
    m, n = len(h), len(h[0])
    valid_gradient = []
    directions = []

    if debug:
        visited = [[False for _ in range(n)] for _ in range(m)]
        canvas = np.zeros(img.shape[:2], dtype="uint8")

    def hue_is_red(r, c):
        return 5 <= h[r][c] <= 12 and s[r][c] >= 65 and v[r][c] >= 128

    def hue_is_valid(r1, c1, r2, c2, diff):
        return abs(int(h[r1][c1]) - int(h[r2][c2])) <= diff and s[r2][c2] >= 150 and v[r2][c2] >= 150 and h[r2][c2] <= 70

    def near_gradient(r, c):
        for i, j in valid_gradient:
            if abs(i-r) < 15 and abs(c-j) < 15:
                return True
        return False

    def gradient_exists(r1, c1, delta_r, delta_c):
        if near_gradient(r1, c1):
            return False

        tmp_r1, tmp_c1 = r1, c1
        rune_gradient = False
        # The directional arrows that appear in runes are around 30 pixels long.
        for _ in range(30):
            r2 = tmp_r1 + delta_r
            c2 = tmp_c1 + delta_c
            if 0 <= r2 < m and 0 <= c2 < n:
                # Check if the next pixel maintains the gradient.
                if hue_is_valid(tmp_r1, tmp_c1, r2, c2, 10):
                    # If the pixel is a green-ish color, it is a possible arrow.
                    if 50 <= h[r2][c2] <= 70:
                        rune_gradient = True
                        valid_gradient.append((r1, c1))
                        break
                    tmp_r1 = r2
                    tmp_c1 = c2
                else:
                    break
            else:
                break

        return rune_gradient

    def expand_gradient(r1, c1, direction):
        stack = [(r1, c1)]
        while stack:
            r2, c2 = stack.pop()
            visited[r2][c2] = True
            if r2 + 1 < m:
                if not visited[r2 + 1][c2] and hue_is_valid(r2, c2, r2 + 1, c2, 2 if direction else 10):
                    stack.append((r2 + 1, c2))
            if r2 - 1 >= 0:
                if not visited[r2 - 1][c2] and hue_is_valid(r2, c2, r2 - 1, c2, 2 if direction else 10):
                    stack.append((r2 - 1, c2))
            if c2 + 1 < n:
                if not visited[r2][c2 + 1] and hue_is_valid(r2, c2, r2, c2 + 1, 10 if direction else 2):
                    stack.append((r2, c2 + 1))
            if c2 - 1 >= 0:
                if not visited[r2][c2 - 1] and hue_is_valid(r2, c2, r2, c2 - 1, 10 if direction else 2):
                    stack.append((r2, c2 - 1))
            canvas[r2][c2] = 180

    def find_direction(r, c):
        if gradient_exists(r, c, 0, -1):
            return "right"
        elif gradient_exists(r, c, 0, 1):
            return "left"
        elif gradient_exists(r, c, -1, 0):
            return "down"
        elif gradient_exists(r, c, 1, 0):
            return "up"
        else:
            return None

    _, imw, _ = img.shape
    rune_left_bound = math.trunc((imw - 500)/2)
    rune_right_bound = rune_left_bound + 500

    print("left: {}, right: {}".format(rune_left_bound,rune_right_bound))

    # The rune captcha was observed to appear within this part of the application window on 1366x768 resolution.
    for r in range(150, 300):
        for c in range(rune_left_bound, rune_right_bound):
            # Arrows start at a red-ish color and are around 15 pixels apart.
            if hue_is_red(r, c) and not near_gradient(r, c):
                direction = find_direction(r, c)
                if direction:
                    directions.append((direction, (r, c)))
                    if debug:
                        if direction == "LEFT" or direction == "RIGHT":
                            expand_gradient(r, c, 1)
                        else:
                            expand_gradient(r, c, 0)

    if debug:
        cv.imshow("Hue", h)
        cv.imshow("Saturation", s)
        cv.imshow("Value", v)
        cv.imshow("Original", img)
        cv.imshow("Parsed", canvas)
        cv.waitKey(0)

    return sorted(directions, key=lambda x: x[1][1])

def locate(self, *color):
    with gdi_capture.CaptureWindow(self.hwnd) as img:
        locations = []
        if img is None:
            pass
        else:
            # Crop the image to show only the mini-map.
            img_cropped = img[self.left:self.right, self.top:self.bottom]
            height, width = img_cropped.shape[0], img_cropped.shape[1]
            # Reshape the image from 3-d to 2-d by row-major order.
            img_reshaped = np.reshape(img_cropped, ((width * height), 4), order="C")
            for c in color:
                sum_x, sum_y, count = 0, 0, 0
                # Find all index(s) of np.ndarray matching a specified BGRA tuple.
                matches = np.where(np.all((img_reshaped == c), axis=1))[0]
                for idx in matches:
                    # Calculate the original (x, y) position of each matching index.
                    sum_x += idx % width
                    sum_y += idx // width
                    count += 1
                if count > 0:
                    x_pos = sum_x / count
        
                    y_pos = sum_y / count
                    locations.append((x_pos, y_pos))
        return locations

def get_rune_location(self):
    location = locate(self,RUNE_BGRA)
    return location[0] if len(location) > 0 else None

def enterCashshop(self):
    """Enters the cash shop to reset rune cooldown."""
    try:
        cashShopKey = self.config['Cash Shop']
        press(cashShopKey, 1)
        time.sleep(2)
        
        # Check if we're inside cash shop
        with mss.mss() as sct:
            window = config.capture.window
            output = "assets/cashshop_check.png"
            sct_img = sct.grab(window)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        
        # Check for cash shop template
        cashshop_img = cv.imread(output, 0)
        matches = utils.multi_match(cashshop_img, INSIDE_CS_TEMPLATE, threshold=0.8)
        
        if matches:
            print("Successfully entered cash shop")
            # Exit cash shop
            press('esc', 1)
            time.sleep(1)
            return True
        else:
            print("Failed to enter cash shop")
            return False
            
    except Exception as e:
        print(f"Error entering cash shop: {e}")
        return False

def get_rune_image(win):
        with gdi_capture.CaptureWindow(win) as img:
            return img.copy()

def solve_rune_raw(self):
    """Solve rune using machine learning approach with TensorFlow."""
    attempts = 0
    while attempts <= 3 and config.enabled == True:
        npcChatKey = self.config['NPC/Gather']
        press(npcChatKey, 1)
        time.sleep(0.2)

        with mss.mss() as sct:
            # The screen part to capture
            window = config.capture.window
            output = "assets/rune_capture.png"
            sct_img = sct.grab(window)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)

        # Load the captured rune image
        rune_img = cv.imread(output)
        if rune_img is None:
            print("Failed to capture rune image")
            attempts += 1
            continue

        # Use ML model to predict arrow sequence
        print("Using ML model to solve rune...")
        arrow_sequence = []
        
        # Try to detect 4 arrows using ML
        for i in range(4):
            direction = ml_solver.predict_arrow_direction(rune_img)
            if direction:
                arrow_sequence.append(direction)
                print(f"Arrow {i+1}: {direction}")
            else:
                print(f"Failed to detect arrow {i+1}")
                break
        
        # If ML didn't work, fall back to CV method
        if len(arrow_sequence) != 4:
            print("ML detection incomplete, using CV fallback...")
            directions = find_arrow_directions(rune_img)
            if len(directions) == 4:
                arrow_sequence = [d[0] for d in directions]
                print(f"CV detected sequence: {arrow_sequence}")
            else:
                print(f"CV detected {len(directions)} arrows, need 4")
                arrow_sequence = []

        if len(arrow_sequence) == 4:
            print(f"Solving rune with sequence: {arrow_sequence}")
            
            # Input the arrow sequence
            for direction in arrow_sequence:
                press(direction, 1)
                time.sleep(0.1)
            
            time.sleep(1)
            
            # Check if rune was solved
            rune_location = get_rune_location(self)
            if rune_location is None:
                print("Rune has been solved successfully!")
                time.sleep(1)
                return True
            else:
                print("Rune solving failed, trying again...")
        else:
            print("Could not identify complete arrow sequence, trying again...")
            press(npcChatKey, 1)
            time.sleep(1.5)
            attempts += 1
            if attempts > 3:
                print("Too many failed attempts, entering cash shop to reset...")
                enterCashshop(self)
                attempts = 0
                time.sleep(0.5)
                return False
        time.sleep(3)
    return False