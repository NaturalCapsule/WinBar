import ctypes
from ctypes import wintypes



ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_TOP = 1
ABE_BOTTOM = 3
ABE_RIGHT = 2
ABE_LEFT = 0



class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]

appbar_data = None

def register_as_taskbar(QApplication, taskbar_height, width_gap, winId, position):
    global appbar_data
    screen_width = QApplication.desktop().screenGeometry().width()
    screen_height = QApplication.desktop().screenGeometry().height()
    appbar_data = APPBARDATA()
    appbar_data.cbSize = ctypes.sizeof(APPBARDATA)
    appbar_data.hWnd = int(winId())

    if position == 'left':
        appbar_data.uEdge = ABE_LEFT
        appbar_data.rc = wintypes.RECT(
            0,
            0,
            taskbar_height,
            screen_height
        )

    elif position == 'right':
        appbar_data.uEdge = ABE_RIGHT
        appbar_data.rc = wintypes.RECT(
            screen_width - taskbar_height,
            0,
            screen_width,
            screen_height 
        )


    elif position == 'top':
        appbar_data.uEdge = ABE_TOP
        appbar_data.rc = wintypes.RECT(
            width_gap, 
            screen_height - taskbar_height, 
            screen_width - width_gap, 
            screen_height
        )

    elif position == 'bottom':
        appbar_data.uEdge = ABE_BOTTOM
        appbar_data.rc = wintypes.RECT(
            width_gap, 
            screen_height - taskbar_height, 
            screen_width - width_gap, 
            screen_height
        )

    # appbar_data.rc = wintypes.RECT(
    #     width_gap, 
    #     screen_height - taskbar_height, 
    #     screen_width - width_gap, 
    #     screen_height
    # )

    ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(appbar_data))
    ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(appbar_data))

def closeEvent(event):
    ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(appbar_data))
    event.accept()
