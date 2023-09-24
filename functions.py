"""Define the functions used in this project"""
import os
import time
from unicornhatmini import UnicornHATMini
import slack_sdk
from constants import *

# Initialize Unicorn Hat Mini
unicornhatmini = UnicornHATMini()


def post_to_slack(slack_channel, post_text, slack_api_key, mock_run):
    """Post text to Slack. If mock_run = True, print the text here instead"""

    if mock_run:
        print("--- post_to_slack: This would have posted to Slack Channel '{}' ---".format(slack_channel))
        print(post_text)
        print("--- post_to_slack: End ---")
        return

    client = slack_sdk.WebClient(os.environ[slack_api_key])
    response = client.chat_postMessage(channel=slack_channel,
                                       text=post_text)
    return response


def clear_section(start_x, end_x, start_y, end_y):
    """Clear a section of pixels, such as when changing the number or an entire line for a new hour"""
    this_x = start_x

    if start_x > end_x:
        print("Error, cannot clear section as start_x: {} is greater than end_x: {}".format(start_x, end_x))

    if start_y > end_y:
        print("Error, cannot clear section as start_y: {} is greater than end_y: {}".format(start_y, end_y))

    while this_x <= end_x:
        this_y = start_y
        while this_y <= end_y:
            unicornhatmini.set_pixel(this_x, this_y, 0, 0, 0)
            this_y += 1
        this_x += 1

    time.sleep(TIME_DELAY)
    unicornhatmini.show()


def display_number(number, x_offset, y_offset, clear=False, rgb=None, test=False):
    """Display a single number"""
    if rgb is None:
        rgb = COLORS["white"]

    if clear or test:
        unicornhatmini.clear()

    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]

    for pixel in NUMBERS_TO_DRAW[number]:
        unicornhatmini.set_pixel(pixel[0] + x_offset, pixel[1] + y_offset, red, green, blue)

        # Show the same number 6 times to ensure the display is working on test mode
        if test:
            unicornhatmini.set_pixel(pixel[0] + x_offset + 6, pixel[1] + y_offset, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset - 5, pixel[1] + y_offset, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset, pixel[1] + y_offset - 4, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset + 6, pixel[1] + y_offset - 4, red, green, blue)
            unicornhatmini.set_pixel(pixel[0] + x_offset - 5, pixel[1] + y_offset - 4, red, green, blue)

        unicornhatmini.show()
        time.sleep(TIME_DELAY)


def test_numbers():
    """Initial run of the clock to show you the numbers and to verify it all works"""
    current_number = 9
    while current_number >= 0:
        display_number(current_number, 0, 0, test=True)
        time.sleep(TIME_DELAY * 2)
        current_number -= 1
    unicornhatmini.clear()
