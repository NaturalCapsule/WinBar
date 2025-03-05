from ctypes import wintypes
import ctypes



ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_TOP = 1
ABE_BOTTOM = 3



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

def register_as_taskbar(QApplication, taskbar_height, width_gap, winId):
    global appbar_data
    appbar_data = APPBARDATA()
    appbar_data.cbSize = ctypes.sizeof(APPBARDATA)
    appbar_data.hWnd = int(winId())
    appbar_data.uEdge = ABE_BOTTOM  # Change to ABE_TOP if at top!. top bar will be added soon! (maybe...)

    screen_width = QApplication.desktop().screenGeometry().width()
    screen_height = QApplication.desktop().screenGeometry().height()


    appbar_data.rc = wintypes.RECT(
        width_gap, 
        screen_height - taskbar_height, 
        screen_width - width_gap, 
        screen_height
    )

    ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(appbar_data))
    ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(appbar_data))

def closeEvent(event):
    ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(appbar_data))
    event.accept()
