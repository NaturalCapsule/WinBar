import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QMessageBox
from rapidfuzz import process, fuzz
import win32com.client


class AppSearch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluxBar - LNK Search")
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout(self)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search for a shortcut...")
        self.search_bar.textChanged.connect(self.filter_results)
        layout.addWidget(self.search_bar)

        self.results_list = QListWidget(self)
        self.results_list.itemClicked.connect(self.launch_selected)
        layout.addWidget(self.results_list)

        self.lnk_files = []
        self.filtered_files = []

    def find_shortcuts(self):
        search_dirs = [
            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs",
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.expanduser("~\\Desktop"),
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

    def resolve_shortcut(self, lnk_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(lnk_path)
        return shortcut.TargetPath

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppSearch()
    window.show()
    window.lnk_files = window.find_shortcuts()
    sys.exit(app.exec_())
