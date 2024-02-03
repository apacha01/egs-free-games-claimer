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

# Grab the free game
def grabFreeGame():
    # Make sure we are scrolled to the very top. Since we don't know how far down we are, let's pick some astronomical number to be sure
    pag.scroll(10000)
    found = False
    coords = ""

    # Focus on the store tab (we're on the menu, we selected the store)
    matched_image, coords = findTemplateInScreenshot(
            captureScreenshot(),
            str(Path("templates").joinpath("store_link.png")),
        )
    
    if matched_image is not None:
            # click so scroll works
            pag.click(x=coords[0], y=coords[1])
            sleep(1)
    else:
        exit_with_error('Something went wrong, store link on the page not found.', getframeinfo(currentframe()).lineno)

    # Search for, then click the 'Free Now' button on the game
    while not found:
        matched_image, center_coordinates = findTemplateInScreenshot(
            captureScreenshot(),
            str(Path("templates").joinpath("free_game_button.png")),
        )

        sleep(1.5)

        if matched_image is not None:
            found = True
            coords = center_coordinates
            break

        # May want to modify this, don't what screen MasonStooksbury has that he had this with -750, was to much for me
        pag.scroll(-5)

    if found:
        # added -100 don't know why it is needed but pag would click right under the game (something to do with how linux displays things?)
        pag.click(x=coords[0], y=coords[1] - 100)
        sleep(7)
    else:
        exit_with_error(
            "Free Game button not found.", getframeinfo(currentframe()).lineno
        )

    # Navigate Mature Content Warning screen
    matched_image, coords = findTemplateInScreenshot(
        captureScreenshot(),
        str(Path("templates").joinpath("continue_after_warning_button.png")),
    )

    if matched_image is not None:
        pag.click(x=coords[0], y=coords[1])
        sleep(5)
    else:
        logger(getframeinfo(currentframe()).lineno, "No Mature Content Warning screen, continuing...")

    # If game is already in library just return
    matched_image, coords = findTemplateInScreenshot(
        captureScreenshot(), str(Path("templates").joinpath("already_in_library_tag.png"))
    )

    if matched_image is not None:
        logger(getframeinfo(currentframe()).lineno, "Game already in library")
        return None

    # Find and click 'Get'
    matched_image, coords = findTemplateInScreenshot(
        captureScreenshot(), str(Path("templates").joinpath("get_game_button.png"))
    )

    if matched_image is not None:
        pag.click(x=coords[0], y=coords[1])
        sleep(5)
    else:
        exit_with_error(
            "Couldn't find 'Get' button.", getframeinfo(currentframe()).lineno
        )

    # Fill out EULA if available
    # matched_image, coords = findTemplateInScreenshot(
    #     captureScreenshot(), str(Path("templates").joinpath("eula_checkbox.png"))
    # )

    # if matched_image is not None:
    #     pag.click(x=coords[0], y=coords[1])
    #     sleep(2)
    #     matched_image, coords = findTemplateInScreenshot(
    #         captureScreenshot(),
    #         str(Path("templates").joinpath("eula_accept_button.png")),
    #     )
    #     if matched_image is not None:
    #         pag.click(x=coords[0], y=coords[1])
    #         sleep(5)
    # else:
    #     logger(getframeinfo(currentframe()).lineno, "No EULA, continuing...")

    # Find and click 'Place Order'
    matched_image, coords = findTemplateInScreenshot(
        captureScreenshot(),
        str(Path("templates").joinpath("place_order_button.png")),
    )

    if matched_image is not None:
        pag.click(x=coords[0], y=coords[1])
        sleep(5)
    else:
        exit_with_error(
            "Couldn't find 'Place Order' button.", getframeinfo(currentframe()).lineno
        )

    # Check if it was 'purchased'
    matched_image, coords = findTemplateInScreenshot(
        captureScreenshot(),
        str(Path("templates").joinpath("thank_you_for_your_order_title.png")),
    )

    if matched_image is None:
        logger(getframeinfo(currentframe()).lineno, "Claim may not have been completed, you should check just in case.")
        return None

    matched_image, coords = findTemplateInScreenshot(
        captureScreenshot(),
        str(Path("templates").joinpath("continue_browsing_button.png")),
    )

    if matched_image is not None:
        pag.click(x=coords[0], y=coords[1])
        sleep(5)
        logger(getframeinfo(currentframe()).lineno, "Finished claiming game.")

    return None

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
    sleep(5)

# Look for and get the free game
logger(getframeinfo(currentframe()).lineno, "Grabbing free game...")
grabFreeGame()

# Finished
logger(getframeinfo(currentframe()).lineno, "Exiting...")
sys.exit()
