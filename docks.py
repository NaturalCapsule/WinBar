import os
import elevate
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
from configparser import ConfigParser
import psutil
import subprocess
import time
import threading
import pyuac

username = os.getlogin()

class DockApp:
    def __init__(self, dock_layout):
        # Check if the app is running as admin at the start
        if not pyuac.isUserAdmin():
            elevate.elevate(show_console = False)  # Relauching the script with admin rights
            return

        self.dock_layout = dock_layout
        self.loadAppsFromConfig()
        self.open_apps = {}

    def addDockIcon(self, app_path, icon_path, layout):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setStyleSheet("border: 10px;")

        app_name = os.path.basename(app_path).replace(".exe", "")

        button.setProperty('app_name', app_name)
        button.setProperty('app_pid', None)
        button.clicked.connect(lambda: self.launchApp(app_name=app_name, app_path=app_path, button=button))
        layout.addSpacing(20)
        layout.addWidget(button)

    def loadAppsFromConfig(self):
        config = ConfigParser()
        config.read('config.ini')
        self.active_border_color = config.get('active', 'activeBorderColor')
        self.active_border = config.getint('active', 'activeBorder')
        self.active_border_radius = config.getint('active', 'activeBorderRadius')
        self.active_background_color = config.get('active', 'activeBackgroundColor')

        if 'DockApps' in config:
            for key, value in config['DockApps'].items():
                try:
                    app_path, icon_path = value.split(', ')
                    app_path = app_path.replace(f"{username}", os.getlogin())  # Replace {username} with actual username
                    self.addDockIcon(app_path, icon_path, self.dock_layout)
                except ValueError:
                    print(f"Invalid entry for {key} in config.ini. Expected format: app_path, icon_path")

    def launchApp(self, app_name, app_path, button):
        try:
            # Launch the app with subprocess
            process = subprocess.Popen(app_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.open_apps[app_name] = psutil.Process(process.pid)

            button.setProperty('app_pid', process.pid)

            # Apply active styles to indicate the app is running
            button.setStyleSheet(f"""
                border: {self.active_border}px solid {self.active_border_color};
                background-color: {self.active_background_color};
                border-radius: {self.active_border_radius}px;
            """)

            threading.Thread(target=self.monitorApp, args=(app_name, process.pid, button), daemon=True).start()
        except Exception as e:
            print(f"Failed to launch {app_name}: {e}")

    # Function to monitor the app process
    def monitorApp(self, app_name, pid, button):
        while psutil.pid_exists(pid):
            time.sleep(5)

        # Reset the button style when the app is no longer running
        button.setProperty('app_pid', None)
        button.setStyleSheet("border: none;")
