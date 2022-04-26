#documentation of ctype is given on below link
#https://docs.python.org/dev/library/ctypes.html?highlight=s#pointers
import ctypes
import time

SendInput = ctypes.windll.user32.SendInput

up = 0x26 #VK_UP
down = 0x28 #VK_DOWN
left = 0x25 #VK_LEFT
right = 0x27 #VK_RIGHT

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class keyboard_i(ctypes.Structure):
    _fields_ = [("KI1", ctypes.c_ushort),
                ("KI2", ctypes.c_ushort),
                ("Flags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("ExtraInfo", PUL)]

class hardware_i(ctypes.Structure):
    _fields_ = [("Msg", ctypes.c_ulong),
                ("upParamL", ctypes.c_short),
                ("upParamH", ctypes.c_ushort)]

class input_1(ctypes.Union):
    _fields_ = [("kbi", keyboard_i),
                ("hwi", hardware_i)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("input", input_1)]



def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    input_ = input_1()
    input_.kbi = keyboard_i( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), input_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    input_ = input_1()
    input_.kbi = keyboard_i( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), input_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

if __name__ == '__main__':
    PressKey(0x26)
    time.sleep(1)
    ReleaseKey(0x26)
    time.sleep(1)
