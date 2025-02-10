from PyQt5.QtWidgets import QLabel, QPushButton
from functools import partial
import subprocess
import json

def cmd(command):
    subprocess.Popen(command, shell=True)

def load_widgets_from_json(parent, file_path):
    try:
        with open(file_path, "r") as file:
            widgets = json.load(file)

        for widget in widgets:
            if widget["type"] == "label":
                label = QLabel(widget["text"])
                label.setObjectName(widget['name'])
                parent.main_layout.addWidget(label)

            elif widget["type"] == "button":
                button = QPushButton(widget["text"])
                button.setObjectName(widget['name'])
                if "action" in widget:
                    button.clicked.connect(partial(cmd, widget['action']))

                parent.main_layout.addWidget(button)

    except Exception as e:
        print(f"Error loading widgets: {e}")
