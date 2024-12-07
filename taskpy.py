import sys
import psutil
import time
from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget, QToolTip, QPushButton
from PyQt5.QtCore import Qt, QTimer, QEvent, QPoint, QThread, pyqtSignal
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QSurfaceFormat
import configparser
import os
from docks import DockApp
from wifi import ConnectedToWifi
from datetime import date
from nvidia import Nvidia 
from utils import Utils
from message import Message
from exit import Exit
from threading import Thread
from menu import Menu

class CustomTaskbar(QWidget):
    def __init__(self):
        super().__init__()
        self.loadConfig()
        self.initUI()
        self.open_apps = {}
        self.monitor_exit_thread = Thread(target=self.exit_function, daemon=True)
        self.monitor_exit_thread.start()

    def loadConfig(self):
        config = configparser.ConfigParser(interpolation = None)
        config.read('config/config.ini')

        self.taskbar_height_warning = config.getboolean('Appearance', 'taskbarHeightWarning')
        self.taskbar_height = config.getint('Appearance', 'taskbarHeight')
        self.transparent = config.getboolean('Appearance', 'transparency')
        if self.transparent == True:
            self.setAttribute(Qt.WA_TranslucentBackground)

        self.trash_layout: int = config.getint('Appearance', 'trashLayout')
        self.show_battery = config.getboolean('Appearance', 'showBattery')
        self.display_time_layout = config.get('Appearance', 'timeLayout')

    def taskbar_warning(self):
        if self.taskbar_height > 80:
            Message.messagebox(self)
            sys.exit()

    def layout1(self, main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addLayout(trash_layout)
        main_layout.addLayout(menu_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(wifi_layout)
        if self.show_battery:
            main_layout.addLayout(battery_layout)
        main_layout.addLayout(time_layout)

    def layout2(self, main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addLayout(menu_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(trash_layout)
        main_layout.addLayout(wifi_layout)
        if self.show_battery:
            main_layout.addLayout(battery_layout)
        main_layout.addLayout(time_layout)

    def layout3(self, main_layout, sys_info_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout):
        main_layout.addLayout(sys_info_layout)
        main_layout.addLayout(menu_layout)
        main_layout.addStretch()
        main_layout.addLayout(dock_layout)
        main_layout.addStretch()
        main_layout.addLayout(wifi_layout)
        if self.show_battery:
            main_layout.addLayout(battery_layout)
        main_layout.addLayout(time_layout)

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
        self.setGeometry(0, QApplication.desktop().screenGeometry().height() - taskbar_height, screen_width, taskbar_height)
        self.setFixedHeight(taskbar_height)
        os.system('cls')
        print("---------------YOU CAN NOW CLOSE THIS TERMINAL!!---------------")

        if self.taskbar_height_warning:
            self.taskbar_warning()

        self.setObjectName('window')

        with open('config/style.css', 'r') as f:
            self.css = f.read()
        self.setStyleSheet(self.css)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        trash_layout = QHBoxLayout()

        sys_info_layout = QHBoxLayout()
        self.sys_info_label = QLabel("Loading...")
        self.sys_info_label.setObjectName('window')
        sys_info_layout.addWidget(self.sys_info_label)

        self.tooltip_timer = QTimer(self)
        self.tooltip_timer.timeout.connect(self.updateTooltip)
        self.tooltip_timer.setInterval(1000)

        dock_layout = QHBoxLayout()

        docks = DockApp(dock_layout)

        self.trash_button(trash_layout)

        menu_layout = QHBoxLayout()
        self.menu_button(menu_layout)

        time_layout = QHBoxLayout()
        self.time_label = QLabel("")
        self.time_label.setObjectName('window')
        time_layout.addWidget(self.time_label)

        battery_layout = QHBoxLayout()
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
            self.layout3(main_layout, sys_info_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout)
        elif self.trash_layout == 2:
            self.layout2(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout)
        else:
            self.layout1(main_layout, sys_info_layout, trash_layout, dock_layout, time_layout, wifi_layout, battery_layout, menu_layout)

        self.updateSystemInfo()
        timer = QTimer(self)
        timer.timeout.connect(self.updateSystemInfo)
        # timer.start(1000)


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


    def menu_button(self, layout):
        self.menu = QPushButton("")
        self.menu.setObjectName('menuButton')
        self.menu.setStyleSheet(self.css)
        
        self.menu_ = Menu(self.menu)
        
        self.menu.clicked.connect(self.menu_.open_menu)
        
        icon_layout = QHBoxLayout(self.menu)
        icon_layout.setContentsMargins(5, 0, 5, 0)

        svg_icon = QSvgWidget()
        svg_icon.load("svgs/menu.svg")
        svg_icon.setFixedSize(20, 20)
        icon_layout.addWidget(svg_icon)

        layout.addWidget(self.menu)


    def trash_button(self, layout):
        self.button = QPushButton()
        self.button.setObjectName('trashButton')
        self.button.setStyleSheet(self.css)

        self.button.setToolTip("This button deletes all the temporary files which are stored in your system!")
        self.button.clicked.connect(Utils.delete_temp_files)

        icon_layout = QHBoxLayout(self.button)
        icon_layout.setContentsMargins(5, 0, 5, 0)

        svg_icon = QSvgWidget()
        svg_icon.load("svgs/trash.svg")
        svg_icon.setFixedSize(20, 20)
        icon_layout.addWidget(svg_icon)


        layout.addWidget(self.button)

        self.button.enterEvent = self.show_tooltip_above_trash
        self.button.leaveEvent = self.hide_tooltip


    def updateWifiLabel(self):
        is_connected = ConnectedToWifi.is_wifi_connected()
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
        self.gpu_tooltip = f"GPU Temperature: {gpu_temp}°C\nGPU Usage: {gpu_usage}%\nGPU VRAM Used: {used_vram:.2f} GB / {tot_vram} GB"
        self.sys_info_label.setText(f"CPU: {cpu_usage}% | RAM: {ram_usage}% {gpu_text}{gpu_usage}%")

    def updateBattery(self):
        try:
            battery = psutil.sensors_battery()[0]
            battery_plugged = psutil.sensors_battery()[2]

        except (IndexError, TypeError):
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

        self.battery_icon.setToolTip(f"Battery Level: {battery}%")


    def updateTime(self):
        today = date.today()
        today = today.strftime("%d %b %Y")
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
    app = QApplication(sys.argv)
    taskbar = CustomTaskbar()
    taskbar.show()

    sys.exit(app.exec_())