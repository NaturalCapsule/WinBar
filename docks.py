import os
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
from configparser import ConfigParser
import psutil
import subprocess

username = os.getlogin()

class DockApp:
    def __init__(self):
        self.dock_buttons = []
        self.loadAppsFromConfig()
        self.open_apps = {}


    def addDockIcon(self, app_path, icon_path):
        dock_button = QPushButton()
        dock_button.setObjectName('dock')
        dock_button.setIcon(QIcon(icon_path))

        with open('config/style.css', 'r') as f:
            self.css = f.read()
        dock_button.setStyleSheet(self.css)
        app_name = os.path.basename(app_path).replace(".exe", "")

        dock_button.setProperty('app_name', app_name)
        dock_button.setProperty('app_pid', None)
        dock_button.clicked.connect(lambda: self.launchApp(app_name=app_name, app_path=app_path, button=dock_button))
        self.dock_buttons.append(dock_button)

    def loadAppsFromConfig(self):
        config = ConfigParser()
        config.read('config/config.ini')

        if 'DockApps' in config:
            for key, value in config['DockApps'].items():
                try:
                    app_path, icon_path = value.split(', ')
                    app_path = app_path.replace(f"{username}", os.getlogin())
                    self.addDockIcon(app_path, icon_path)
                except ValueError:
                    print(f"Invalid entry for {key} in config.ini. Expected format: app_path, icon_path")

    def launchApp(self, app_name, app_path, button):
        try:
            process = subprocess.Popen(app_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.open_apps[app_name] = psutil.Process(process.pid)

            button.setProperty('app_pid', process.pid)

            button.setStyleSheet(self.css)

        except Exception as e:
            print(f"Failed to launch {app_name}: {e}")