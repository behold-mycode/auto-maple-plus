import mss
import numpy as np
import cv2
import json

with open('window_config.json') as f:
    cfg = json.load(f)
region = {
    'left': cfg['left'],
    'top': cfg['top'],
    'width': cfg['width'],
    'height': cfg['height']
}
with mss.mss() as sct:
    img = np.array(sct.grab(region))
    cv2.imwrite('manual_window_test.png', img)
print('Saved manual_window_test.png')