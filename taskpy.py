import sys
import psutil
import time
from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget, QToolTip, QPushButton
from PyQt5.QtCore import Qt, QTimer, QEvent, QPoint, QObject
import pynvml
import subprocess
import configparser
import WinTmp
from PyQt5.QtGui import QIcon
import os
import threading

import pyuac
import glob
import shutil
import tkinter.messagebox as message

username = os.getlogin()


class CustomTaskbar(QWidget):
    def __init__(self):
        super().__init__()
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        self.loadConfig()
        self.initUI()
        self.open_apps = {}
        if not pyuac.isUserAdmin():
            pyuac.runAsAdmin()


    def loadConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini')


        self.taskbar_height_warning = config.getboolean('Appearance', 'taskbar_height_warning')

        self.taskbar_height = config.getint('Appearance', 'taskbar_height')
        self.background_color = config.get('Appearance', 'background_color')
        self.text_color = config.get('Appearance', 'text_color')
        self.font_size = config.getint('Appearance', 'font_size')
        self.border_radius = config.getint('Appearance', 'border_radius')
        self.transparent = config.getboolean('Appearance', 'transparency')
        if self.transparent == True:
            self.setAttribute(Qt.WA_TranslucentBackground)

        self.tool_background = config.get('Tooltip', 'tool_tip_background_color')
        self.tool_text_color = config.get('Tooltip', 'tool_tip_text_color')
        self.tool_font_size = config.getint('Tooltip', 'tool_tip_font_size')
        self.tool_border_radius = config.getint('Tooltip', 'tool_tip_border_radius')
        self.tool_border_color = config.get('Tooltip', 'tool_tip_border_color')
        self.tool_padding = config.getint('Tooltip', 'tool_tip_padding')
        self.tool_border = config.getint('Tooltip', 'tool_tip_border')


        self.button_color = config.get('button', 'button_color')
        self.background_button_color = config.get('button', 'backround_button_color')
        self.hover_button_color = config.get('button', 'hover_button')
        self.hover_padding = config.get('button', 'hover_padding')
        self.hover_border_radius = config.get('button', 'hover_border_radius')
        self.hover_border = config.get('button', 'hover_border')
        self.button_border = config.get('button', 'button_border')
        self.padding_button = config.get('button', 'padding_button')

        self.active_border_color = config.get('active', 'active_border_color')
        self.active_border = config.getint('active', 'active_border')
        self.active_border_radius = config.getint('active', 'active_border_radius')
        self.active_background_color = config.get('active', 'active_background_color')

        self.trash_layout: int = config.getint('trash', 'trash_layout')

    def messagebox(self):
        message.showwarning("TaskBar Height is out of bounds!", "This warning message indicates that you set the taskbar height way too high, please lower it.\n\nBut hey who gives a shit this is an open source project, if you still wannna change it,\nGo to the config.ini file and set the taskbar_height_warning to 'False'!... :)")


    def taskbar_warning(self):
        if self.taskbar_height > 80:
            self.messagebox()
            sys.exit()

    def layout1(self, main_layout, sys_info_layout, trash_layout, dock_layout, time_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addLayout(trash_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(time_layout)

    def layout2(self, main_layout, sys_info_layout, trash_layout, dock_layout, time_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(trash_layout)
        main_layout.addLayout(time_layout)

    def layout3(self, main_layout, sys_info_layout, dock_layout, time_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(time_layout)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        screen_width = QApplication.desktop().screenGeometry().width()
        taskbar_height = self.taskbar_height
        self.setGeometry(0, QApplication.desktop().screenGeometry().height() - taskbar_height, screen_width, taskbar_height)
        self.setFixedHeight(taskbar_height)

        if self.taskbar_height_warning:
            self.taskbar_warning()

        self.setStyleSheet(f"""
            /* Taskbar styles */
            QWidget {{
                background-color: {self.background_color};  /* Taskbar background color */
                color: {self.text_color};    /* Taskbar text color */
                font-size: {self.font_size}px; /* Taskbar font size */
                border-radius: {self.border_radius}px; /* Taskbar border radius */
            }}

            QPushButton {{
                background-color: {self.background_button_color};
                color:{self.button_color};
                border: {self.button_border}px;
                padding: {self.padding_button}px;
            }}

            QPushButton:hover {{
                background-color: {self.hover_button_color};
                border-radius: {self.hover_border_radius}px;
                border: {self.hover_border}px;
                padding: {self.hover_padding}px;
            }}

            /* Tooltip styles */
            QToolTip {{
                background-color: {self.tool_background};   /* Tooltip background color */
                color: {self.tool_text_color};               /* Tooltip text color */
                border: {self.tool_border}px solid {self.tool_border_color}; /* Tooltip border color */
                padding: {self.tool_padding}px;              /* Padding around tooltip text */
                font-size: {self.tool_font_size}px;          /* Tooltip font size */
                border-radius: {self.tool_border_radius}px;  /* Tooltip border radius */
            }}
        """)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        trash_layout = QHBoxLayout()

        sys_info_layout = QHBoxLayout()
        self.sys_info_label = QLabel("Loading...")
        sys_info_layout.addWidget(self.sys_info_label)


        self.tooltip_timer = QTimer(self)
        self.tooltip_timer.timeout.connect(self.updateTooltip)
        self.tooltip_timer.setInterval(1000)

        dock_layout = QHBoxLayout()
        dock_layout.addStretch()

        ########################################## ADD YOUR APPS LIKE THESE 6 APPS ##########################################
        self.addDockIcon("C:/Windows/explorer.exe", "explorer.png", dock_layout)
        self.addDockIcon("C:/Program Files/JetBrains/PyCharm Community Edition 2024.1.4/bin/pycharm64.exe", "pycharm.png", dock_layout)
        self.addDockIcon("C:/Program Files/Mozilla Firefox/firefox.exe", "firefox.png", dock_layout)
        self.addDockIcon(f"C:/Users/{username}/AppData/Local/Programs/Microsoft VS Code/Code.exe", "code.png", dock_layout)
        self.addDockIcon("C:/Content Manager.exe", "cm.png", dock_layout)
        self.addDockIcon("C:/Program Files (x86)/Steam/steam.exe", "steam.png", dock_layout)
        ########################################## ADD YOUR APPS LIKE THESE 6 APPS ##########################################

        self.trash_button(trash_layout)

        dock_layout.addStretch()

        time_layout = QHBoxLayout()
        self.time_label = QLabel("")
        time_layout.addWidget(self.time_label)

        if self.trash_layout == 0:
            self.layout3(main_layout, sys_info_layout, dock_layout, time_layout)
        elif self.trash_layout == 2:
            self.layout2(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout)
        else:
            self.layout1(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout)

        self.updateSystemInfo()
        timer = QTimer(self)
        timer.timeout.connect(self.updateSystemInfo)
        timer.start(1000)

        self.updateTime()
        time_timer = QTimer(self)
        time_timer.timeout.connect(self.updateTime)
        time_timer.start(1000)

        self.sys_info_label.installEventFilter(self)

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


    def delete_temp_files(self):
        temp_paths = [r"C:\Windows\Temp\*", fr"C:\Users\{username}\AppData\Local\Temp\*"]

        for temp_path in temp_paths:
            # Use glob to get all directories in the directory matching the pattern
            files = glob.glob(temp_path)

            for file in files:
                try:
                    # Only delete directories, skip .txt files
                    if os.path.isdir(file):
                        shutil.rmtree(file)  # Remove directories
                        print(f"Deleted directory: {file}")
                    else:
                        # Skip text files
                        if file.endswith('.txt'):
                            print(f"Skipped a file: {file}")
                        else:
                            os.remove(file)  # Optionally, remove other non-text files (if needed)
                except PermissionError as e:
                    print(f"Permission error deleting {file}: {e}. Skipping.")
                except OSError as e:
                    print(f"Error deleting {file}: {e}. Skipping.")

    def trash_button(self, layout):
        self.button = QPushButton(f"")
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.background_color};
                color: {self.text_color};
                font-size: {self.font_size}px;
                border-radius: {self.border_radius}px;
                border: 10px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_button_color};
                border-radius: {self.hover_border_radius}px;
                border: {self.hover_border}px;
                padding: {self.padding_button}px;
            }}
        """)


        self.button.setToolTip("This button deletes all the temporary files which stored in your system!, Make sure you have ran this as Administrator!")
        self.button.clicked.connect(self.delete_temp_files)
        layout.addWidget(self.button)
        self.button.enterEvent = self.show_tooltip_above
        self.button.leaveEvent = self.hide_tooltip

    def show_tooltip_above(self, event):

        tooltip_position = self.button.mapToGlobal(QPoint(0, -self.button.height() - 40))
        QToolTip.showText(tooltip_position, self.button.toolTip(), self.button)
        event.accept()

    def hide_tooltip(self, event):
        QToolTip.hideText()
        event.accept()

    def eventfilter(self, source, event):
        if source == self.button and event.type() == QEvent.ToolTip:
            tooltip_position = source.mapToGlobal(QPoint(0, -source.height() - 20))
            QToolTip.showText(tooltip_position, source.toolTip(), source)
            return True
        return super().eventfilter(source, event)

    def monitorApp(self, app_name, pid, button):
        while psutil.pid_exists(pid):
            time.sleep(5)

        button.setProperty('app_pid', None)
        button.setStyleSheet("border: none;")


    def launchApp(self, app_name, app_path, button):

        process = subprocess.Popen(app_path)
        self.open_apps[app_name] = psutil.Process(process.pid)

        button.setProperty('app_pid', process.pid)

        button.setStyleSheet(f"""
            border: {self.active_border}px solid {self.active_border_color};  /* Green border to indicate running state */
            background-color: {self.active_background_color};     /* Darker background to indicate active state */
            border-radius: {self.active_border_radius}px;
        """)

        threading.Thread(target=self.monitorApp, args=(app_name, process.pid, button), daemon=True).start()

    def get_cpu_temperature(self):
        cpu = WinTmp.CPU_Temp()
        if cpu == 0.0 or cpu is None:
            return "Please make sure you have ran this program as an Administrator"

        return f"{cpu:.2f}°C"

    def get_used_vram(self):
        vram_used = pynvml.nvmlDeviceGetMemoryInfo(self.handle).used
        vram_used_gb = vram_used / (1024 ** 3)
        return vram_used_gb

    def get_nvidia_gpu_usage(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                                    stdout=subprocess.PIPE, text=True)
            temperature = result.stdout.strip()
            return f"{temperature}"
        except FileNotFoundError:
            return "nvidia-smi not found. Make sure NVIDIA drivers are installed."


    def get_nvidia_gpu_temperature(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                                    stdout=subprocess.PIPE, text=True)
            temperature = result.stdout.strip()
            return f"{temperature}"
        except FileNotFoundError:
            return "nvidia-smi not found. Make sure NVIDIA drivers are installed."


    def get_tot_vram(self):
        vram_total = pynvml.nvmlDeviceGetMemoryInfo(self.handle).total
        vram_total_gb = vram_total / (1024 ** 3)
        return vram_total_gb

    def updateSystemInfo(self):
        cpu_usage = psutil.cpu_percent()
        cpu_temp = self.get_cpu_temperature()
        ram_info = psutil.virtual_memory()
        ram_usage = ram_info.percent
        gpu_usage = self.get_nvidia_gpu_usage()
        gpu_temp = self.get_nvidia_gpu_temperature()
        used_vram = self.get_used_vram()
        tot_vram = self.get_tot_vram()

        cpu_freq = psutil.cpu_freq().current
        ram_used_gb = ram_info.used / (1024 ** 3)
        ram_total_gb = ram_info.total / (1024 ** 3)
        self.cpu_tooltip = f"CPU Frequency: {cpu_freq:.2f} MHz\nCPU Usage: {cpu_usage}%\nCPU Temp: {cpu_temp}"
        self.ram_tooltip = f"RAM Used: {ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB\nRAM Usage: {ram_usage}%"
        self.gpu_tooltip = f"GPU Temperature: {gpu_temp}°C\nGPU Usage: {gpu_usage}%\nGPU VRAM Used: {used_vram:.2f} GB / {tot_vram} GB"

        self.sys_info_label.setText(f"CPU: {cpu_usage}% | RAM: {ram_usage}% | GPU: {gpu_usage}%")

    def updateTime(self):
        # This for the battery (i know the battery should not be in this function but it is what it is.)
        try:
            battery = psutil.sensors_battery()[0]
            battery_plugged = psutil.sensors_battery()[2]

        except TypeError:
            battery = ''
            battery_plugged = ''

        if battery is None:
            battery = ''

        battery_icon = ''

        batteries = {"Battery-full": "  ","battery-three-quarters": "  ", "battery-half": "  ", "battery-quarter": "  ", "battery-low": "  ", "battery-charging": "  ", "battery-empty": "  "}

        if battery != '' and battery_plugged:
            battery_icon = batteries.get("battery-charging")

        elif battery != '' and battery == 100:
            battery_icon = batteries.get("battery-full")

        elif battery != '' and battery >= 60 and battery < 100:
            battery_icon = batteries.get("battery-three-quarters")
        
        elif battery != '' and battery < 60 and battery >= 40:
            battery_icon = batteries.get("battery-half")

        elif battery != '' and battery <= 59 and battery >= 40:
           battery_icon = batteries.get("battery-quarter")

        elif battery != '' and battery <= 39 and battery >= 10:
            battery_icon = batteries.get("battery-low")

        elif battery != '' and battery < 10:
            battery_icon = batteries.get("battery-empty")

        current_time = time.strftime("%H:%M:%S")
        self.time_label.setText(f"{battery_icon} {battery}|{current_time}")


    def updateTooltip(self):
        self.updateSystemInfo()
        QToolTip.showText(self.sys_info_label.mapToGlobal(self.sys_info_label.rect().center()),
                          f"{self.cpu_tooltip}\n\n{self.ram_tooltip}\n\n{self.gpu_tooltip}",
                          self.sys_info_label)

    def eventFilter(self, obj, event):
        if obj == self.sys_info_label:
            if event.type() == QEvent.Enter:
                self.tooltip_timer.start()
            elif event.type() == QEvent.Leave:
                self.tooltip_timer.stop()
                QToolTip.hideText()
        return super().eventFilter(obj, event)

config = configparser.ConfigParser()
config.read('config.ini')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    taskbar = CustomTaskbar()
    taskbar.show()

    sys.exit(app.exec_())