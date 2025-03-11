import sys
import os
import subprocess
import win32com.client
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
from rapidfuzz import process, fuzz

class AppSearch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluxSearch")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)

        with open('config/style.css', 'r') as f:
            css = f.read()

        self.search_bar = QLineEdit(self)
        self.search_bar.setObjectName('WinBar')
        self.search_bar.setStyleSheet(css)
        self.search_bar.setPlaceholderText("Search for an app...")
        self.search_bar.textChanged.connect(self.filter_results)
        layout.addWidget(self.search_bar)

        self.results_list = QListWidget(self)
        self.results_list.setObjectName('resultList')
        self.results_list.setStyleSheet(css)
        self.results_list.itemClicked.connect(self.launch_selected)
        layout.addWidget(self.results_list)


        self.lnk_files = []
        self.filtered_files = []


        self.search_bar.installEventFilter(self)
        self.results_list.installEventFilter(self)

        self.dragging = False

    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
            self.dragging = True
            self.oldpos = event.globalPos()
        elif event.type() == event.MouseMove and self.dragging:
            delta = QPoint(event.globalPos() - self.oldpos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldpos = event.globalPos()
        elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.dragging = False

        return super().eventFilter(obj, event)

    def find_shortcuts(self):
        search_dirs = [
            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs",
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser(r"C:\Users\Public\Desktop")
        ]

        lnk_paths = []
        for folder in search_dirs:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(".lnk"):
                        lnk_paths.append(os.path.join(root, file))

        print(f"Found {len(lnk_paths)} shortcuts (.lnk files).")
        return lnk_paths

    def filter_results(self):
        query = self.search_bar.text().strip().lower()
        if not query:
            self.results_list.clear()
            return

        matches = process.extract(query, self.lnk_files, limit=15, scorer=fuzz.partial_ratio)
        self.filtered_files = [match[0] for match in matches if match[1] > 50]

        self.results_list.clear()
        self.results_list.addItems([os.path.basename(path) for path in self.filtered_files])

    def launch_selected(self, item):
        index = self.results_list.row(item)
        if index < len(self.filtered_files):
            lnk_path = self.filtered_files[index]
            self.run_shortcut(lnk_path)

    def run_shortcut(self, lnk_path):
        resolved_path = self.resolve_shortcut(lnk_path)
        
        if not resolved_path or not os.path.exists(resolved_path):
            print(f"Error: Target of {lnk_path} not found.")
            return

        try:
            print(f"Launching: {lnk_path} → {resolved_path}")
            os.startfile(lnk_path)
        except Exception as e:
            print("Failed to launch shortcut:", e)
            subprocess.Popen(lnk_path, shell=True)
        sys.exit()

    def resolve_shortcut(self, lnk_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(lnk_path)
        return shortcut.TargetPath

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppSearch()
    window.setWindowIcon(QIcon('svgs/launcher.svg'))
    window.show()
    window.lnk_files = window.find_shortcuts()
    sys.exit(app.exec_())
