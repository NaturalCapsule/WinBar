import sys
import time
import pyperclip
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QApplication, QScrollBar, QPushButton
from PyQt5.QtGui import QIcon
from configparser import ConfigParser
import os
import keyboard

config = ConfigParser()

config.read('config/config.ini')
get_info = config.getboolean("Panel", "storeClipboard")

username = os.getlogin()

file_path = f"C:/Users/{username}/AppData/file.txt"

class CheckThread(QThread):
    command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.last_content = ""
        self.file = None

    def run(self):
        use_file = get_info
        if use_file:
            with open(file_path, "a") as f:
                while True:
                    current_content = pyperclip.paste()
                    if current_content != self.last_content:
                        self.last_content = current_content
                        f.write(current_content + "\n")
                        f.flush()
                        self.command_signal.emit(current_content)
                    time.sleep(0.5)

        else:
            while True:
                current_content = pyperclip.paste()
                if current_content != self.last_content:
                    self.last_content = current_content
                    self.command_signal.emit(current_content)
                time.sleep(0.5)

class ClipBoard(QWidget):
    def __init__(self):
        super().__init__()


        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen_geometry = QApplication.desktop().screenGeometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        self.window_height = int(self.screen_height * 0.4)
        self.window_width = int(self.screen_width * 0.3)

        self.center_x = (self.screen_width - self.window_width) // 2
        self.center_y = (self.screen_height - self.window_height) // 2

        with open('config/style.css', 'r') as f:
            self.css = f.read()
        self.setStyleSheet(self.css)

        self.setObjectName("MainclipWindow")

        self.scroll_bar = QScrollBar(self)
        self.scroll_bar.setObjectName("scrollBar")
        self.animation = QPropertyAnimation(self, b"geometry")

        self.initUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_keys)
        self.timer.start(100)

        self.test = QTimer(self)
        self.test.timeout.connect(self.clear_history)
        self.test.start(100)

        self.delete_text = False

        self.clipboard_thread = CheckThread()
        self.clipboard_thread.command_signal.connect(self.update_list)
        self.clipboard_thread.start()


    def mousePressEvent(self, event):
        self.oldpos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldpos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldpos = event.globalPos()


    def initUI(self):
        self.resize(self.window_width, self.window_height)

        self.setGeometry(-self.window_width, self.center_y, self.window_width, self.window_height)

        layout = QVBoxLayout(self)

        self.qlist = QListWidget(self)
        self.qlist.setObjectName("clipBoard")
        layout.addWidget(self.qlist)

        self.delete_button = QPushButton("Clear History", self)
        self.delete_button.clicked.connect(self.delete_texts)
        self.delete_button.setObjectName("ClipButtons")
        
        self.hide_app = QPushButton("Hide app")
        self.hide_app.clicked.connect(self.hide_button)
        self.hide_app.setObjectName("ClipButtons")

        layout.addWidget(self.delete_button)
        layout.addWidget(self.hide_app)

        self.setLayout(layout)

    def animate_app(self, show):
        if show:
            self.animation.setDuration(300)
            self.animation.setStartValue(QRect(-self.window_width, self.center_y, self.window_width, self.window_height))
            self.animation.setEndValue(QRect(self.center_x, self.center_y, self.window_width, self.window_height))
            self.animation.start()
        else:
            self.animation.setStartValue(QRect(self.center_x, self.center_y, self.window_width, self.window_height))
            self.animation.setEndValue(QRect(-self.window_width, self.center_y, self.window_width, self.window_height))  # Target position
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()


    def toggle_side_clipboard(self):
        if self.x() < 0:
            self.show()
            self.animate_app(show=True)
        else:
            self.animate_app(show=False)


    def hide_button(self):
        self.animation.setStartValue(QRect(self.center_x, self.center_y, self.window_width, self.window_height))
        self.animation.setEndValue(QRect(-self.window_width, self.center_y, self.window_width, self.window_height))  # Target position
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def check_keys(self):
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift') and keyboard.is_pressed("H"):
            self.toggle_side_clipboard()

    def delete_texts(self):
        with open(file_path, "w") as f:
            self.delete_text = True

    def update_list(self, content):
        use_file = get_info

        self.qlist.addScrollBarWidget(self.scroll_bar, Qt.AlignLeft)

        file_content = []

        if use_file:
            try:
                with open(file_path, "r") as f:
                    new_ = f.read()
                    file_content = new_.split("\n")

                    for new_text in file_content:
                        if new_text.strip():
                            self.qlist.addItem(new_text.strip())
            except FileNotFoundError:
                print("test.txt file not found, starting with an empty list.")
            except Exception as e:
                print(f"Error reading file: {e}")

        if content.strip() and content not in file_content:
            self.qlist.addItem(content.strip())
            
            try:
                with open(file_path, "a") as f:
                    f.write(content.strip() + "\n")
            except Exception as e:
                print(f"Error writing to file: {e}")

        if self.delete_text:
            self.qlist.clear()

        self.qlist.scrollToBottom()

    def clear_history(self):
        if self.delete_text:
            self.qlist.clear()
            self.delete_text = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipBoard()
    window.setWindowTitle("Clipboard History")
    window.setWindowIcon(QIcon("svgs/clipboard.svg"))
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec_())