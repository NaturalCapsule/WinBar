import os
import elevate
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
from configparser import ConfigParser
import psutil
import subprocess
import pyuac

username = os.getlogin()

class DockApp:
    def __init__(self, dock_layout):
        if not pyuac.isUserAdmin():
            elevate.elevate(show_console = False)
            return
        self.dock_layout = dock_layout
        self.loadAppsFromConfig()
        self.open_apps = {}

    def addDockIcon(self, app_path, icon_path, layout):

        button = QPushButton()
        button.setObjectName('dock')
        button.setIcon(QIcon(icon_path))

        with open('config/style.css', 'r') as f:
            self.css = f.read()
        button.setStyleSheet(self.css)
        app_name = os.path.basename(app_path).replace(".exe", "")

        button.setProperty('app_name', app_name)
        button.setProperty('app_pid', None)
        button.clicked.connect(lambda: self.launchApp(app_name=app_name, app_path=app_path, button=button))
        layout.addSpacing(20)
        layout.addWidget(button)

    def loadAppsFromConfig(self):
        config = ConfigParser()
        config.read('config/config.ini')

        if 'DockApps' in config:
            for key, value in config['DockApps'].items():
                try:
                    app_path, icon_path = value.split(', ')
                    app_path = app_path.replace(f"{username}", os.getlogin())
                    self.addDockIcon(app_path, icon_path, self.dock_layout)
                except ValueError:
                    print(f"Invalid entry for {key} in config.ini. Expected format: app_path, icon_path")

    def launchApp(self, app_name, app_path, button):
        try:
            process = subprocess.Popen(app_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.open_apps[app_name] = psutil.Process(process.pid)

            button.setProperty('app_pid', process.pid)

            button.setStyleSheet(self.css)

            # threading.Thread(target=self.monitorApp, args=(app_name, process.pid, button), daemon=True).start()
        except Exception as e:
            print(f"Failed to launch {app_name}: {e}")
