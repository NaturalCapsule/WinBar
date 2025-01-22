import sys
import time
import pyperclip
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QApplication, QScrollBar, QPushButton
from PyQt5.QtGui import QIcon
from configparser import ConfigParser
import os

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

        with open('config/style.css', 'r') as f:
            self.css = f.read()
        self.setStyleSheet(self.css)

        self.setObjectName("MainclipWindow")

        self.scroll_bar = QScrollBar(self)
        self.scroll_bar.setObjectName("scrollBar")

        self.initUI()

        self.clipboard_thread = CheckThread()
        self.clipboard_thread.command_signal.connect(self.update_list)
        self.clipboard_thread.start()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.qlist = QListWidget(self)
        self.qlist.setObjectName("clipBoard")
        self.qlist.setMinimumSize(250, 250)
        self.qlist.addScrollBarWidget(self.scroll_bar, Qt.AlignLeft)

        self.delete_button = QPushButton("Delete copied texts!", self)
        self.delete_button.clicked.connect(self.delete_texts)
        self.delete_button.setObjectName("deleteButton")

        layout.addWidget(self.qlist)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def delete_texts(self):
        with open(file_path, "w") as f:
            pass

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

        self.qlist.scrollToBottom()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipBoard()
    window.setWindowTitle("Clipboard History")
    window.setWindowIcon(QIcon("svgs/clipboard.svg"))
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec_())