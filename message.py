import tkinter.messagebox as message

class Message:
    def messagebox(self):
        message.showwarning("TaskBar Height is out of bounds!", "This warning message indicates that you set the taskbar height way too high, please lower it.\n\nBut hey who gives a shit, if you still wannna change it,\nGo to the config.ini file and set the taskbarHeightWarning to 'False'!... :)")

    def message(web_engine):
        message.showerror(f"{web_engine} has not been found!", f"{web_engine} has not been found make sure its installed in the default locaiton")

    def idk_what_to_call():
        message.showwarning("Warning!", "You set firefox and chrome to True make sure one of them is False to search the web!")
