import pyautogui
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer


class ScrollingLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(180)


        self.setObjectName('windowTitle')
        
        self.setFixedSize(150, 18)

        with open('config/style.css', 'r') as file:
            css = file.read()

        self.setStyleSheet(css)

        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_text)
        self.scroll_timer.start(100)

        self.full_text = ""
        self.scroll_position = 0

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_window_title)
        self.update_timer.start(500)

    def check_window_title(self):
        new_title = pyautogui.getActiveWindowTitle() or "No Active Window"
        
        if new_title != self.full_text:
            self.full_text = new_title
            self.scroll_position = 0
            if len(self.full_text) > 20:
                self.scroll_timer.start()
            else:
                self.scroll_timer.stop()
                self.setText(self.full_text)

    def scroll_text(self):
        if len(self.full_text) > 20:
            self.scroll_position += 1
            if self.scroll_position > len(self.full_text):
                self.scroll_position = 0
            self.setText(self.full_text[self.scroll_position:] + "   " + self.full_text[:self.scroll_position])

