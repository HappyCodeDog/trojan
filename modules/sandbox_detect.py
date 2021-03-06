from ctypes import *

import random
import sys
import time
import win32api

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)
    ]

# get the elapsed time since last input
def get_last_input():
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)

    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
    run_time = windll.kernel32.GetTickCount()
    elapsed = run_time - struct_lastinputinfo.dwTime
    print(f"[*] It's been {elapsed} milliseconds since the last event.")
    return elapsed

class Detector:
    def __init__(self):
        self.double_clicks = 0
        self.keystrokes = 0
        self.mouse_clicks = 0

        self.max_double_clicks = 2
        self.max_keystrokes = 10     # random.randint(10, 25)
        self.max_mouse_clicks = 10   # random.randint(5, 25)
        self.max_input_threshold = 30000

    # this is a "stupid method", we can use pyWinhook instead
    def get_key_press(self):
        # iterating over the range of valid input keys
        for i in range(0, 0xff):
            state = win32api.GetAsyncKeyState(i)
            if state & 0x0001:  # if the key's state show it is pressed
                if i == 0x1:    # left-mouse-button click
                    self.mouse_clicks += 1
                    return time.time()
                elif i > 32 and i < 127:
                    self.keystrokes += 1
        return None

    def detect(self):
        previous_timestamp = None
        first_double_click = None
        double_click_threshold = 0.35


        # too long without an input. It's a sign of sandbox
        last_input = get_last_input()
        if last_input >= self.max_input_threshold:
            sys.exit(0)

        detection_complete = False
        while not detection_complete:
            keypress_time = self.get_key_press()
            if keypress_time is not None and previous_timestamp is not None:
                elapsed = keypress_time - previous_timestamp

                # it's a double click rather than single click
                if elapsed <= double_click_threshold:
                    self.mouse_clicks -= 2
                    self.double_clicks += 1
                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        if self.double_clicks >= self.max_double_clicks:
                            # if there are too many double clicks in a short period of time,
                            # they're likely to be generated by sandbox
                            if keypress_time - first_double_click <= \
                                (self.max_double_clicks*double_click_threshold):
                                    sys.exit(0)

            if (self.keystrokes >= self.max_keystrokes and self.double_clicks >= self.max_double_clicks
                    and self.mouse_clicks >= self.max_mouse_clicks):
                detection_complete = True

                previous_timestamp = keypress_time
            elif keypress_time is not None:
                previous_timestamp = keypress_time

if __name__ == '__main__':
    d = Detector()
    d.detect()
    print('okay.')



