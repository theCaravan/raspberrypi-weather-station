"""Main Program"""
from functions import *

unicornhatmini.set_brightness(SCREEN_BRIGHTNESS)

# Run a display of all the numbers as a welcome greeting and a diagnostic
test_numbers()

# Set none of the buttons as pressed
b_is_pressed = False
a_is_pressed = False
y_is_pressed = False
x_is_pressed_hide_screen = False

initial_run = True
error_in_program = False


def pressed_b():
    """Run this when pressing the B (upper left) button on the Unicorn Hat Mini"""
    global b_is_pressed
    global initial_run

    if b_is_pressed:
        b_is_pressed = False
        unicornhatmini.clear()
        unicornhatmini.show()
        initial_run = True

    else:
        b_is_pressed = True


def pressed_a():
    """Run this when pressing the A (upper right) button on the Unicorn Hat Mini"""
    global a_is_pressed
    global initial_run

    if a_is_pressed:
        a_is_pressed = False
        unicornhatmini.clear()
        unicornhatmini.show()
        initial_run = True
    else:
        a_is_pressed = True


def pressed_y():
    """Run this when pressing the Y (bottom left) button on the Unicorn Hat Mini"""
    global y_is_pressed

    if y_is_pressed:
        y_is_pressed = False
    else:
        y_is_pressed = True


def pressed_x_hide_screen():
    """Hide/Show the clock when pressing the X (bottom right) button on the Unicorn Hat Mini"""
    global x_is_pressed_hide_screen

    if x_is_pressed_hide_screen:
        x_is_pressed_hide_screen = False
    else:
        x_is_pressed_hide_screen = True


while True:
    # Time values are grabbed here
    if not MOCK_RUN:
        datetime_now = datetime.now()
    else:
        datetime_now = MOCK_DATETIME

    current_unix_time = int(time.mktime(datetime_now.timetuple()))
    today_date_str = datetime_now.strftime("%d/%m/%Y")

    BUTTON_B.when_pressed = pressed_b
    BUTTON_A.when_pressed = pressed_a
    BUTTON_Y.when_pressed = pressed_y
    BUTTON_X.when_pressed = pressed_x_hide_screen

    if x_is_pressed_hide_screen:
        a_is_pressed = False
        b_is_pressed = False
        initial_run = True

        time.sleep(TIME_DELAY)
        unicornhatmini.clear()

        unicornhatmini.show()
        continue

    test_numbers()

    just_pressed = False
    t = datetime.utcnow()
    sleep_time = 60 - t.second
    for i in range(sleep_time * 20):
        saved_b = b_is_pressed
        saved_a = a_is_pressed
        saved_y = y_is_pressed
        saved_x = x_is_pressed_hide_screen

        time.sleep(TIME_DELAY)
        if saved_x != x_is_pressed_hide_screen or saved_y != y_is_pressed \
                or saved_a != a_is_pressed or saved_b != b_is_pressed:
            just_pressed = True
            break

    # Clear new screen pressed buttons if this wasn't just pressed
    # Allows a screen to reset to the main on its own at the next minute
    if not just_pressed:
        a_is_pressed = False
        b_is_pressed = False
        unicornhatmini.clear()
        initial_run = True
