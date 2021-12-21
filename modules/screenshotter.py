# import base64
import win32api
import win32con
import win32gui
import win32ui

def get_dimensions():
    # get the size of screen, which decides the size of screenshot
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return width, height, left, top

def screenshot(name='screenshot'):
    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    # create device context
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # create device context base on memory
    mem_dc = img_dc.CreateCompatibleDC()

    # create bitmap object
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)

    # set the memory-based device context to point at the captured bitmap object
    mem_dc.SelectObject(screenshot)

    # copy screen to our device context in memory and save it to file
    # like memcpy(), but just for GDI object
    mem_dc.BitBlt((0,0), (width,height), img_dc, (left,top), win32con.SRCCOPY)
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp')

    # free the object
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())

def run():
    screenshot()
    with open('screenshot.bmp') as f:
        img = f.read()
    return img

if __name__ == '__main__':
    screenshot()