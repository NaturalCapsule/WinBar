import sys
import psutil
import time
from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget, QToolTip, QPushButton
from PyQt5.QtCore import Qt, QTimer, QEvent, QPoint
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QFont
import pynvml
import subprocess
import configparser
import WinTmp
import os
import threading
import glob
import shutil
import tkinter.messagebox as message
from docks import DockApp
from wifi import ConnectedToWifi
from datetime import date

username = os.getlogin()

class CustomTaskbar(QWidget):
    def __init__(self):
        super().__init__()

        self.loadConfig()
        self.initUI()
        self.open_apps = {}

    def loadConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.taskbar_height_warning = config.getboolean('Appearance', 'taskbarHeightWarning')
        self.taskbar_height = config.getint('Appearance', 'taskbarHeight')
        self.background_color = config.get('Appearance', 'backgroundColor')
        self.text_color = config.get('Appearance', 'textColor')
        self.font_size = config.getint('Appearance', 'fontSize')
        self.border_radius = config.getint('Appearance', 'borderRadius')
        self.transparent = config.getboolean('Appearance', 'transparency')
        if self.transparent == True:
            self.setAttribute(Qt.WA_TranslucentBackground)

        self.tool_background = config.get('Tooltip', 'toolTipBackgroundColor')
        self.tool_text_color = config.get('Tooltip', 'toolTipTextColor')
        self.tool_font_size = config.getint('Tooltip', 'toolTipFontSize')
        self.tool_border_radius = config.getint('Tooltip', 'toolTipBorderRadius')
        self.tool_border_color = config.get('Tooltip', 'toolTipBorderColor')
        self.tool_padding = config.getint('Tooltip', 'toolTipPadding')
        self.tool_border = config.getint('Tooltip', 'toolTipBorder')

        self.button_color = config.get('button', 'buttonColor')
        self.background_button_color = config.get('button', 'backroundButtonColor')
        self.hover_button_color = config.get('button', 'hoverButton')
        self.hover_padding = config.get('button', 'hoverPadding')
        self.hover_border_radius = config.get('button', 'hoverBorderRadius')
        self.hover_border = config.get('button', 'hoverBorder')
        self.button_border = config.get('button', 'buttonBorder')
        self.padding_button = config.get('button', 'paddingButton')

        self.trash_layout: int = config.getint('trash', 'trashLayout')

    def messagebox(self):
        message.showwarning("TaskBar Height is out of bounds!", "This warning message indicates that you set the taskbar height way too high, please lower it.\n\nBut hey who gives a shit this is an open source project, if you still wannna change it,\nGo to the config.ini file and set the taskbar_height_warning to 'False'!... :)")


    def taskbar_warning(self):
        if self.taskbar_height > 80:
            self.messagebox()
            sys.exit()

    def layout1(self, main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addLayout(trash_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(wifi_layout)
        main_layout.addLayout(battery_layout)
        main_layout.addLayout(time_layout)

    def layout2(self, main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(trash_layout)
        main_layout.addLayout(wifi_layout)
        main_layout.addLayout(battery_layout)
        main_layout.addLayout(time_layout)

    def layout3(self, main_layout, sys_info_layout, dock_layout, time_layout, wifi_layout, battery_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(wifi_layout)
        main_layout.addLayout(battery_layout)
        main_layout.addLayout(time_layout)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        screen_width = QApplication.desktop().screenGeometry().width()
        taskbar_height = self.taskbar_height
        self.setGeometry(0, QApplication.desktop().screenGeometry().height() - taskbar_height, screen_width, taskbar_height)
        self.setFixedHeight(taskbar_height)
        os.system('cls')
        print("---------------YOU CAN NOW CLOSE THIS TERMINAL!!---------------")

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

        docks = DockApp(dock_layout)

        self.trash_button(trash_layout)

        dock_layout.addStretch()

        time_layout = QHBoxLayout()
        self.time_label = QLabel("")
        time_layout.addWidget(self.time_label)

        battery_layout = QHBoxLayout()
        # self.battery_widget = QWidget()
        self.battery_icon = QSvgWidget()
        self.battery_icon.setFixedSize(20, 20)
        battery_layout.addWidget(self.battery_icon)


        wifi_layout = QHBoxLayout()
        self.wifi_widget = QWidget()
        wifi_layout.addWidget(self.wifi_widget)
        self.wifi_icon = QSvgWidget()
        self.wifi_icon.setFixedSize(20, 20)
        wifi_layout.addWidget(self.wifi_icon)

        if self.trash_layout == 0:
            self.layout3(main_layout, sys_info_layout, dock_layout, time_layout, wifi_layout, battery_layout)
        elif self.trash_layout == 2:
            self.layout2(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout)
        else:
            self.layout1(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout)

        self.updateSystemInfo()
        timer = QTimer(self)
        timer.timeout.connect(self.updateSystemInfo)
        timer.start(1000)


        self.updateTime()
        time_timer = QTimer(self)
        time_timer.timeout.connect(self.updateTime)
        time_timer.start(1000)

        self.updateWifiLabel()
        wifi_timer = QTimer(self)
        wifi_timer.timeout.connect(self.updateWifiLabel)
        self.wifi_icon.enterEvent = self.show_tooltip_above_wifi
        self.wifi_icon.leaveEvent = self.hide_tooltip
        wifi_timer.start(1000)

        self.updateBattery()
        update_battery = QTimer(self)
        update_battery.timeout.connect(self.updateBattery)
        self.battery_icon.enterEvent = self.show_tooltip_above_battery
        self.battery_icon.leaveEvent = self.hide_tooltip
        update_battery.start(1000)

        self.sys_info_label.installEventFilter(self)


    def delete_temp_files(self):
        temp_paths = [r"C:\Windows\Temp\*", fr"C:\Users\{username}\AppData\Local\Temp\*", "C:\Windows\Prefetch\*"]

        for temp_path in temp_paths:
            files = glob.glob(temp_path)

            for file in files:
                try:
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                        print(f"Deleted directory: {file}")
                    else:
                        os.remove(file)
                except PermissionError as e:
                    print(f"Permission error deleting {file}: {e}. Skipping.")
                except OSError as e:
                    print(f"Error deleting {file}: {e}. Skipping.")

    def trash_button(self, layout):
        self.button = QPushButton()
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

        self.button.setToolTip("This button deletes all the temporary files which are stored in your system!")
        self.button.clicked.connect(self.delete_temp_files)

        icon_layout = QHBoxLayout(self.button)
        icon_layout.setContentsMargins(5, 1, 5, 5)

        svg_icon = QSvgWidget()
        svg_icon.load("svgs/trash.svg")
        svg_icon.setFixedSize(20, 20)
        icon_layout.addWidget(svg_icon)

        layout.addWidget(self.button)

        self.button.enterEvent = self.show_tooltip_above_trash
        self.button.leaveEvent = self.hide_tooltip


    def updateWifiLabel(self):
        is_connected = ConnectedToWifi.is_connectToInternet()

        show_ssid = ConnectedToWifi.get_connected_wifi_ssid()

        if is_connected:
            self.wifi_icon.load('svgs/wifi_on.svg')
            self.wifi_icon.setToolTip(f"Connected to {show_ssid}")
        else:
            self.wifi_icon.load('svgs/wifi_off.svg')
            self.wifi_icon.setToolTip("No Wi-Fi connection")


    def show_tooltip_above_wifi(self, event):
        tooltip_position = self.wifi_icon.mapToGlobal(QPoint(0, -self.wifi_icon.height() - 40))
        QToolTip.showText(tooltip_position, self.wifi_icon.toolTip(), self.wifi_icon)
        event.accept()

    def show_tooltip_above_battery(self, event):
        tooltip_position = self.battery_icon.mapToGlobal(QPoint(0, -self.battery_icon.height() - 40))
        QToolTip.showText(tooltip_position, self.battery_icon.toolTip(), self.battery_icon)
        event.accept()

    def show_tooltip_above_trash(self, event):
        tooltip_position = self.button.mapToGlobal(QPoint(0, -self.button.height() - 40))
        QToolTip.showText(tooltip_position, self.button.toolTip(), self.button)
        event.accept()

    def hide_tooltip(self, event):
        QToolTip.hideText()
        event.accept()

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
        self.handle = None
        self.has_nvidia_gpu = False
        
        try:
            pynvml.nvmlInit()
            self.num_gpus = pynvml.nvmlDeviceGetCount()
            if self.num_gpus > 0:
                self.has_nvidia_gpu = True
                self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                vram_used = pynvml.nvmlDeviceGetMemoryInfo(self.handle).used
            vram_used_gb = vram_used / (1024 ** 3)
            return vram_used_gb
        except pynvml.NVMLError as e:
            print(f"Error initializing pynvml: {e}")
            return 0

    def get_nvidia_gpu_usage(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                                    stdout=subprocess.PIPE, text=True)
            usage = result.stdout.strip()
            return f"{usage}"
        except FileNotFoundError:
            return ''


    def get_nvidia_gpu_temperature(self):
        self.gpu_test = ""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                                    stdout=subprocess.PIPE, text=True)
            temperature = result.stdout.strip()
            return f"{temperature}"
        except FileNotFoundError:
            self.gpu_test = ""
            return f"{self.gpu_test}"


    def get_tot_vram(self):
        if not self.has_nvidia_gpu:
            return "No NVIDIA GPU detected"
        
        try:
            vram_total = pynvml.nvmlDeviceGetMemoryInfo(self.handle).total
            vram_total_gb = vram_total / (1024 ** 3)
            return vram_total_gb
        except pynvml.NVMLError as e:
            print(f"Error getting total VRAM: {e}")
            return 0

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
        gpu_text = "| GPU: "
        if self.has_nvidia_gpu == False:
            self.gpu_tooltip = ""
            gpu_usage = ""
            gpu_text = ""
        self.gpu_tooltip = f"GPU Temperature: {gpu_temp}°C\nGPU Usage: {gpu_usage}%\nGPU VRAM Used: {used_vram:.2f} GB / {tot_vram} GB"
        self.sys_info_label.setText(f"CPU: {cpu_usage}% | RAM: {ram_usage}% {gpu_text}{gpu_usage}%")


    def batteryLevel(self):
        pass

    def updateBattery(self):
        try:
            battery = psutil.sensors_battery()[0]
            battery_plugged = psutil.sensors_battery()[2]

        except TypeError:
            battery = -1
            battery_plugged = ''

        if battery is None:
            battery = -1

        if battery != -1 and battery_plugged:
            self.battery_icon.load('svgs/battery-charging.svg')

        elif battery != -1 and battery == 100:
            self.battery_icon.load('svgs/battery-full.svg')

        elif battery != -1 and battery >= 60 and battery < 100:
            self.battery_icon.load('svgs/battery-high.svg')

        elif battery != -1 and battery < 60 and battery >= 40:
            self.battery_icon.load('svgs/battery-half.svg')

        elif battery != -1 and battery <= 59 and battery >= 40:
           self.battery_icon.load('svgs/battery-half.svg')

        elif battery != -1 and battery <= 39 and battery >= 10:
            self.battery_icon.load('svgs/battery-medium.svg')

        elif battery != -1 and battery < 10:
            self.battery_icon.load('svgs/battery-low.svg')

        if battery >= 0:
            self.battery_icon.setToolTip(f"Battery Level: {battery}%")


    def updateTime(self):
        today = date.today()
        today = today.strftime("%d %B %Y")

        current_time = time.strftime("%H:%M")
        self.time_label.setText(f"{current_time} | {today}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    taskbar = CustomTaskbar()
    taskbar.show()

    sys.exit(app.exec_())