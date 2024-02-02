from pathlib import Path
from time import sleep
import numpy as np
from subprocess import Popen
from PIL import ImageGrab
import pyautogui as pag
import cv2

# https://github.com/MasonStooksbury/Free-Games-V2/blob/main/Free_Games_V2.py


# Function to easily capture screenshots
def captureScreenshot():
    # Capture the entire screen, convert to a numpy array, then convert to OpenCV format
    return cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)


def findTemplateInScreenshot(screenshot, template_path):
    # Read the template image
    template = cv2.imread(template_path, 0)
    template_w, template_h = template.shape[::-1]

    # Convert screenshot to grayscale for template matching
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # Check for a strong enough match (e.g., >=70%)
    if max_val >= 0.7:
        top_left = max_loc
        # bottom_right = (top_left[0] + template_w, top_left[1] + template_h)

        # Calculate the center coordinates
        center_x = top_left[0] + template_w // 2
        center_y = top_left[1] + template_h // 2

        # Draw a green rectangle around the matched area
        # cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)

        return screenshot, (center_x, center_y)
    else:
        return None, None
