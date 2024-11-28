import tkinter.messagebox as message

class Message:
    def messagebox(self):
        message.showwarning("TaskBar Height is out of bounds!", "This warning message indicates that you set the taskbar height way too high, please lower it.\n\nBut hey who gives a shit this is an open source project, if you still wannna change it,\nGo to the config.ini file and set the taskbar_height_warning to 'False'!... :)")
