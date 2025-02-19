#Main bar file.
import sys
import psutil
import time
import os
import pyuac
import elevate
import configparser
import subprocess
import json
import ctypes
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QProgressBar, QHBoxLayout, QLabel, QWidget, QToolTip, QPushButton
from PyQt5.QtCore import Qt, QTimer, QEvent, QPoint
from PyQt5.QtSvg import QSvgWidget
from docks import DockApp
from wifi import ConnectedToWifi
from datetime import date
from nvidia import Nvidia
from utils import Utils
from message import Message
from exit import Exit
from threading import Thread
from menu import Menu
from functools import partial
from active_window import ScrollingLabel
from rich.console import Console
from rich.text import Text
from ctypes import wintypes

ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_TOP = 1
ABE_BOTTOM = 3

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]

class Bar(QWidget):
    def __init__(self):
        super().__init__()
        self.loadConfig()
        self.initUI()
        self.register_as_taskbar()
        self.load_widgets_from_json('config/config.json', self.left_layout, self.right_layout, self.middle_layout)

        subprocess.Popen(["python", "panel.py"])
        self.monitor_exit_thread = Thread(target=self.exit_function, daemon=True)
        self.monitor_exit_thread.start()

    def loadConfig(self):
        config = configparser.ConfigParser(interpolation = None)
        config.read('config/config.ini')

        self.taskbar_height_warning = config.getboolean('Bar', 'BarHeightWarning')
        self.taskbar_height = config.getint('Bar', 'BarHeight')
    
        self.display_time_layout = config.get('Bar', 'timeLayout')
        self.display_date_layout = config.get('Bar', 'dateLayout')

        border_radius = config.get('Bar', 'BarBorderRadius')
        self.border_radius1, self.border_radius2 = border_radius.split(', ')[0], border_radius.split(', ')[1]
        if int(self.border_radius1) > 0 or int(self.border_radius2) > 0:
            self.setAttribute(Qt.WA_TranslucentBackground)

        self.colors = config.get('Bar', 'BarColor')

        self.color = self.colors.split(',')

        self.heightGap = config.getint('Bar', 'HeightGap')
        self.widthGap = config.getint('Bar', 'WidthGap')

        os.system('cls')
        self.rainbow_text("---------------YOU CAN NOW CLOSE THIS TERMINAL!!---------------")

    def rainbow_text(self, text):
        console = Console()
        colors = ["red", "orange1", "yellow", "green", "cyan", "blue", "magenta", 'black', 'cyan']
        styled_text = Text()
        
        for i, char in enumerate(text):
            styled_text.append(char, style=colors[i % len(colors)])
        
        console.print(styled_text)


    def taskbar_warning(self):
        if self.taskbar_height > 80:
            Message.messagebox(self)
            sys.exit()


    def exit_function(self):
        while True:
            if Exit.exit():
                print("Exiting application...")
                QApplication.quit()
                break
            time.sleep(0.1) 

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        screen_width = QApplication.desktop().screenGeometry().width()

        taskbar_height = self.taskbar_height
        width_gap = self.widthGap
        height_gap = self.heightGap

        self.setGeometry(
            width_gap,
            QApplication.desktop().screenGeometry().height() - taskbar_height - height_gap,
            screen_width - (2 * width_gap),
            taskbar_height
        )
        
        self.setFixedHeight(taskbar_height)

        self.isEnabled_ = False
        self.trash_enabled = False
        self.launcher_enabled = False


        if self.taskbar_height_warning:
            self.taskbar_warning()
        
        self.setObjectName('window')

        with open('config/style.css', 'r') as f:
            self.css = f.read()
        self.setStyleSheet(self.css)

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        self.right_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.left_layout = QHBoxLayout()

        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.middle_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.right_layout)

        self.setLayout(self.main_layout)

        self.sys_info_label = QLabel("Loading...")
        self.sys_info_label.setObjectName('infoLabel')
        self.sys_info_label.setStyleSheet(self.css)

        
        self.tooltip_timer = QTimer(self)
        self.tooltip_timer.timeout.connect(self.updateTooltip)
        self.tooltip_timer.setInterval(1000)
        
        self.menu_button()
        self.trash_button()
        self.launcher_button()

        self.time_label = QLabel("")
        self.time_label.setObjectName('timeLabel')
        self.time_label.setStyleSheet(self.css)

        self.cpu_temp_label = QLabel()
        self.cpu_usage_label = QLabel()
        self.ram_usage_label = QLabel()
        self.ram_usedgb_label = QLabel()
        self.ram_usedtotalgb_label = QLabel()
        self.nvidia_temp_label = QLabel()
        self.nvidia_usedvram_label = QLabel()
        self.nvidia_totvram_label = QLabel()
        self.nvidia_usage_label = QLabel()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setFixedSize(40, 18)
        self.progress_bar.setObjectName("Battery")
        self.progress_bar.setStyleSheet(self.css)

        self.get_window = ScrollingLabel(self)

        self.wifi_ico = QLabel()
        self.wifi_ico.setObjectName('WifiLabel')
        self.offline_icon = ""
        self.online_icon = ""
        self.wifi_icon = QSvgWidget()
        self.wifi_icon.setFixedSize(20, 20)


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
        self.progress_bar.enterEvent = self.show_tooltip_above_battery
        self.progress_bar.leaveEvent = self.hide_tooltip
        update_battery.start(1000)
        

        self.sys_info_label.installEventFilter(self)


    def register_as_taskbar(self):
        self.appbar_data = APPBARDATA()
        self.appbar_data.cbSize = ctypes.sizeof(APPBARDATA)
        self.appbar_data.hWnd = int(self.winId())
        self.appbar_data.uEdge = ABE_BOTTOM  # Change to ABE_TOP if at top!. top bar will be added soon! (maybe...)

        screen_width = QApplication.desktop().screenGeometry().width()
        screen_height = QApplication.desktop().screenGeometry().height()
        taskbar_height = self.taskbar_height
        width_gap = self.widthGap

        self.appbar_data.rc = wintypes.RECT(
            width_gap, 
            screen_height - taskbar_height, 
            screen_width - width_gap, 
            screen_height
        )

        ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(self.appbar_data))
        ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(self.appbar_data))

    def closeEvent(self, event):
        ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(self.appbar_data))
        event.accept()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        alpha = int(self.color[-1])
        painter.setBrush(QColor(int(self.color[0]), int(self.color[1]), int(self.color[2]), alpha = alpha))
        painter.drawRoundedRect(self.rect(), int(self.border_radius1), int(self.border_radius2))


    def menu_button(self):
        self.custom_menu = QPushButton("")
        self.custom_menu.setObjectName('menuButton')
        self.custom_menu.setStyleSheet(self.css)
        self.menu_custom = Menu(self.custom_menu)
        self.custom_menu.clicked.connect(self.menu_custom.open_menu)

        self.menu = QPushButton("")
        self.menu.setObjectName('menuButton')
        self.menu.setStyleSheet(self.css)
        self.menu_ = Menu(self.menu)
        self.menu.clicked.connect(self.menu_.open_menu)


        if not self.isEnabled_:
            icon_layout = QHBoxLayout(self.menu)
            icon_layout.setContentsMargins(5, 0, 5, 0)

            svg_icon = QSvgWidget()
            svg_icon.load("svgs/menu.svg")
            svg_icon.setFixedSize(20, 20)
            icon_layout.addWidget(svg_icon)

    def trash_button(self):
        self.custom_trash = QPushButton()
        self.custom_trash.setObjectName('trashButton')
        self.custom_trash.setStyleSheet(self.css)
        self.custom_trash.setToolTip("Delets all temp files")
        self.custom_trash.clicked.connect(Utils.delete_temp_files)
        self.custom_trash.enterEvent = self.show_tooltip_above_trash
        self.custom_trash.leaveEvent = self.hide_tooltip


        self.trash_button_ = QPushButton()
        self.trash_button_.setObjectName('trashButton')
        self.trash_button_.setStyleSheet(self.css)
        self.trash_button_.setToolTip("Delets all temp files")
        self.trash_button_.clicked.connect(Utils.delete_temp_files)
        self.trash_button_.enterEvent = self.show_tooltip_above_trash
        self.trash_button_.leaveEvent = self.hide_tooltip


        if not self.trash_enabled:
            icon_layout = QHBoxLayout(self.trash_button_)
            icon_layout.setContentsMargins(5, 0, 5, 0)

            svg_icon = QSvgWidget()
            svg_icon.load("svgs/trash.svg")
            svg_icon.setFixedSize(20, 20)
            icon_layout.addWidget(svg_icon)

    def launcher_button(self):
        self.custom_launcher = QPushButton()
        self.custom_launcher.setObjectName('launcherButton')
        self.custom_launcher.setStyleSheet(self.css)
        self.custom_launcher.clicked.connect(self.launch_laucher)

        self.launcher_button_ = QPushButton()
        self.launcher_button_.setObjectName('launcherButton')
        self.launcher_button_.setStyleSheet(self.css)
        self.launcher_button_.clicked.connect(self.launch_laucher)


        if not self.launcher_enabled:
            icon_layout = QHBoxLayout(self.launcher_button_)
            icon_layout.setContentsMargins(5, 0, 5, 0)

            svg_icon = QSvgWidget()
            svg_icon.load("svgs/launcher.svg")
            svg_icon.setFixedSize(20, 20)
            icon_layout.addWidget(svg_icon)        

    def launch_laucher(self):
        subprocess.run(['python', 'app_launcher.py'])

    def cmd(self, command):
        subprocess.Popen(command, shell=True)

    def load_widgets_from_json(self, file_path, left_layout, right_layout, middle_layout):
        try:
            with open(file_path, "r") as file:
                widgets = json.load(file)

                for self.widget in widgets['widgets']:
                    layout_target = self.widget.get("layout", "SELECT A LAYOUT")
                    widget_item = None


                    if "battery" in self.widget:
                        widget_item = self.progress_bar

                    elif "wifi" in self.widget:
                        wifi_con = self.wifi_icon
                        if self.widget.get("onlineIcon") and self.widget.get("offlineIcon"):
                            self.offline_icon = self.widget["offlineIcon"]
                            self.online_icon = self.widget["onlineIcon"]
                            wifi_con = self.wifi_icon
                        widget_item = wifi_con

                    elif "time" in self.widget:
                        widget_item = self.time_label

                    elif "window title" in self.widget:
                        widget_item = self.get_window

                    elif "system info" in self.widget:
                        widget_item = self.sys_info_label

                    elif "menu" in self.widget:
                        menu_ico = self.menu
                        if self.widget.get("icon"):
                            self.custom_menu.setText(self.widget["icon"])
                            self.isEnabled_ = True
                            menu_ico = self.custom_menu
                        widget_item = menu_ico

                    elif "trash" in self.widget:
                        trash_ico = self.trash_button_
                        if self.widget.get("icon"):
                            self.custom_trash.setText(self.widget["icon"])
                            self.trash_enabled = True
                            trash_ico = self.custom_trash
                        widget_item = trash_ico

                    elif "launcher" in self.widget:
                        launcher_ico = self.launcher_button_
                        if self.widget.get("icon"):
                            self.custom_launcher.setText(self.widget["icon"])
                            self.launcher_enabled = True
                            launcher_ico = self.custom_launcher
                        widget_item = launcher_ico

                    elif "type" in self.widget:
                        if self.widget["type"] == "label":
                            if self.widget['text'] == 'cputemp':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_cpu_temp)
                                timer.start(1000)

                                widget_item = self.cpu_temp_label
                            elif self.widget['text'] == 'cpuUsage':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_cpu_usage)
                                timer.start(1000)

                                widget_item = self.cpu_usage_label

                            elif self.widget['text'] == 'ramusage':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_ram_usage)
                                timer.start(1000)

                                widget_item = self.ram_usage_label

                            elif self.widget['text'] == 'ramtotalGB':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_ram_totalGB)
                                timer.start(1000)

                                widget_item = self.ram_usedtotalgb_label

                            elif self.widget['text'] == 'ramusedGB':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_ram_usedGB)
                                timer.start(1000)

                                widget_item = self.ram_usedgb_label

                            elif self.widget['text'] == 'ramusage':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_ram_usage)
                                timer.start(1000)

                                widget_item = self.ram_usage_label

                            elif self.widget['text'] == 'nvidiatemp':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_nvidia_temp)
                                timer.start(1000)

                                widget_item = self.nvidia_temp_label

                            elif self.widget['text'] == 'nvidiausage':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_nvidia_usage)
                                timer.start(1000)

                                widget_item = self.nvidia_usage_label

                            elif self.widget['text'] == 'nvidiaTOTVram':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_nvidia_totVram)
                                timer.start(1000)

                                widget_item = self.nvidia_totvram_label

                            elif self.widget['text'] == 'nvidiaUSEDVram':
                                timer = QTimer(self)
                                timer.timeout.connect(self.update_nvidia_usedVram)
                                timer.start(1000)

                                widget_item = self.nvidia_usedvram_label

                            else:
                                widget_item = QLabel(self.widget["text"])
                            widget_item.setObjectName(self.widget["name"])
                            
                        elif self.widget["type"] == "button":
                            widget_item = QPushButton(self.widget["text"])
                            widget_item.setObjectName(self.widget["name"])
                            if "action" in self.widget:
                                widget_item.clicked.connect(partial(self.cmd, self.widget["action"]))

                    if widget_item:
                        if layout_target == "left":
                            left_layout.addWidget(widget_item)
                        elif layout_target == "right":
                            right_layout.addWidget(widget_item)
                        elif layout_target == "middle":
                            middle_layout.addWidget(widget_item)

            self.docks = DockApp().dock_buttons

            for widget in widgets['widgets']:
                if widget.get('docks') == "show docks":
                    for dock_button in self.docks:
                        layout_target = widget['layout']
                        if layout_target == 'left':
                            left_layout.addWidget(dock_button)
                        elif layout_target == 'right':
                            right_layout.addWidget(dock_button)
                        elif layout_target == 'middle':
                            middle_layout.addSpacing(20)
                            middle_layout.addWidget(dock_button)

        except Exception as e:
            print(f"Error loading widgets: {e}")

    def update_cpu_temp(self):
        cpu_temp = Utils.get_cpu_temperature()
        self.cpu_temp_label.setText(str(cpu_temp))

    def update_cpu_usage(self):
        cpu_usage = Utils.get_cpu_usage()
        self.cpu_usage_label.setText(str(cpu_usage))

    def update_ram_usage(self):
        ram_usage = Utils.ram_usage()
        self.ram_usage_label.setText(str(ram_usage))

    def update_ram_totalGB(self):
        ram_tot_gb = Utils.get_total_ram_gb()
        self.ram_usedtotalgb_label.setText(f"{ram_tot_gb:.2f}")

    def update_ram_usedGB(self):
        ram_used = Utils.get_used_ram_gb()
        self.ram_usedgb_label.setText(f"{ram_used:.2f}")

    def update_nvidia_temp(self):
        nvidia_temp = Nvidia.get_nvidia_gpu_temperature(self)
        self.nvidia_temp_label.setText(f"{nvidia_temp}°C")
    
    def update_nvidia_usedVram(self):
        nvidia_vram = Nvidia.get_used_vram(self)
        self.nvidia_usedvram_label.setText(nvidia_vram)
    
    def update_nvidia_usage(self):
        nvidia_usage = Nvidia.get_nvidia_gpu_usage(self)
        self.nvidia_usage_label.setText(nvidia_usage)
    
    def update_nvidia_totVram(self):
        nvidia_totVram = Nvidia.get_tot_vram(self)
        self.nvidia_totvram_label.setText(nvidia_totVram)


    def updateWifiLabel(self):
        self.is_connected = ConnectedToWifi.is_wifi_connected()
        show_ssid = ConnectedToWifi.get_connected_wifi_ssid()

        if self.is_connected:
            self.wifi_icon.load('svgs/wifi_on.svg')
            self.wifi_ico.setText(self.online_icon)
            self.wifi_icon.setToolTip(f"Connected to {show_ssid}")
        else:
            self.wifi_icon.load('svgs/wifi_off.svg')
            self.wifi_ico.setText(self.offline_icon)
            self.wifi_icon.setToolTip("No Wi-Fi connection")

    def show_tooltip_above_wifi(self, event):
        tooltip_position = self.wifi_icon.mapToGlobal(QPoint(0, -self.wifi_icon.height() - 40))
        QToolTip.showText(tooltip_position, self.wifi_icon.toolTip(), self.wifi_icon)
        event.accept()

    def show_tooltip_above_battery(self, event):
        tooltip_position = self.progress_bar.mapToGlobal(QPoint(0, -self.progress_bar.height() - 40))
        QToolTip.showText(tooltip_position, self.progress_bar.toolTip(), self.progress_bar)
        event.accept()


    def show_tooltip_above_trash(self, event):
        if self.trash_enabled:
            tooltip_position = self.custom_trash.mapToGlobal(QPoint(0, -self.custom_trash.height() - 40))
            QToolTip.showText(tooltip_position, self.custom_trash.toolTip(), self.custom_trash)
        else:
            tooltip_position = self.trash_button_.mapToGlobal(QPoint(0, -self.trash_button_.height() - 40))
            QToolTip.showText(tooltip_position, self.trash_button_.toolTip(), self.trash_button_)
        event.accept()

    def hide_tooltip(self, event):
        QToolTip.hideText()
        event.accept()

    def updateSystemInfo(self):
        cpu_usage = Utils.get_cpu_usage()
        cpu_temp = Utils.get_cpu_temperature()
        cpu_freq = Utils.get_cpu_freq()


        gpu_usage = Nvidia.get_nvidia_gpu_usage(self)
        gpu_temp = Nvidia.get_nvidia_gpu_temperature(self)
        used_vram = Nvidia.get_used_vram(self)
        tot_vram = Nvidia.get_tot_vram(self)

        ram_usage = Utils.ram_usage()
        ram_used_gb = Utils.get_used_ram_gb()
        ram_total_gb = Utils.get_total_ram_gb()

        self.cpu_tooltip = f"CPU Frequency: {cpu_freq:.2f} MHz\nCPU Usage: {cpu_usage}%\nCPU Temp: {cpu_temp}"
        self.ram_tooltip = f"RAM Used: {ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB\nRAM Usage: {ram_usage}%"
        gpu_text = "| GPU: "
        if self.has_nvidia_gpu == False:
            self.gpu_tooltip = ""
            gpu_usage = ""
            gpu_text = ""
        self.gpu_tooltip = f"GPU Temperature: {gpu_temp}°C\nGPU Usage: {gpu_usage}\nGPU VRAM Used: {used_vram} GB / {tot_vram} GB"
        self.sys_info_label.setText(f"CPU: {cpu_usage}% | RAM: {ram_usage}% {gpu_text}{gpu_usage}")

    def updateBattery(self):
        try:
            battery = psutil.sensors_battery()[0]
            battery_plugged = psutil.sensors_battery()[2]

        except (IndexError, TypeError):
            battery = -1
            battery_plugged = ''

        if battery is None:
            battery = -1

        self.progress_bar.setValue(battery)


        if battery_plugged:
            self.progress_bar.setToolTip(f"Plugged")
        else:
            self.progress_bar.setToolTip(f"Not Plugged")


    def updateTime(self):
        today = date.today()
        today = today.strftime(self.display_date_layout)
        current_time = time.strftime(self.display_time_layout)
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
    try:
        # if not pyuac.isUserAdmin():
        #     elevate.elevate(show_console = False)
        #     sys.exit(0)
        app = QApplication(sys.argv)
        fluxbar = Bar()
        fluxbar.setWindowTitle("FluxBar")
        fluxbar.show()
        sys.exit(app.exec_())

    except OSError as e:
        print("Error", e)