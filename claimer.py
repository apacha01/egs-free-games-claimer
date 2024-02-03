from pathlib import Path
from time import sleep
import numpy as np
from subprocess import Popen, PIPE
from PIL import ImageGrab
import pyautogui as pag
import cv2
import sys
import atexit
from datetime import datetime
from inspect import currentframe, getframeinfo

# https://github.com/MasonStooksbury/Free-Games-V2/blob/main/Free_Games_V2.py


# Utils
def logger(line_number, message):
    print(f"[{str(datetime.now())}][LN:{line_number:4}]: {message}")

def exit_with_error(error, line_number):
    logger(line_number, f"ERROR:\n\t{error}\n")
    logger(line_number, "Exiting...")
    sys.exit()


# Function to easily capture screenshots
def captureScreenshot():
    # Capture the entire screen, convert to a numpy array, then convert to OpenCV format
    logger(getframeinfo(currentframe()).lineno, "Taking screenshot...")
    return cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)


def findTemplateInScreenshot(screenshot, template_path):
    logger(getframeinfo(currentframe()).lineno, "Looking for template in screenshot...")
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

        logger(getframeinfo(currentframe()).lineno, "Found.")
        return screenshot, (center_x, center_y)
    else:
        logger(getframeinfo(currentframe()).lineno, "Not Found.")
        return None, None


verbose = True if len(sys.argv) > 1 and (sys.argv[1] == '-v' or sys.argv[1] == '--verbose') else False

cmd_to_execute = ["heroic"]
out_dest = None if verbose else PIPE

# Open the Heroic Games Launcher Desktop App
logger(getframeinfo(currentframe()).lineno, f"Executing command: '{str(cmd_to_execute)}'...")
process = Popen(cmd_to_execute, stdout=out_dest, stderr=out_dest)

atexit.register(process.terminate)

# Give the app a second to startup
sleep(5)

# Looking for the "Store" link on the left side of the app
logger(getframeinfo(currentframe()).lineno, "Looking for store button in menu...")
matched_image, coords = findTemplateInScreenshot(
    captureScreenshot(), str(Path("templates").joinpath("store_menu_button.png"))
)

# If not found then app didn't open
if matched_image is None:
    exit_with_error(
        "Couldn't find store button, check if Heroic Game Launcher actually opens.",
        getframeinfo(currentframe()).lineno,
    )
# Otherwise, make sure the window is focused, then get our free game
else:
    pag.click(x=coords[0], y=coords[1])
    sleep(2)

# For now just open, go to store and close
logger(getframeinfo(currentframe()).lineno, "Finished. Exiting...")
sys.exit()
