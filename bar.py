#Main bar file.
import sys
import time
import os
import pyuac
import elevate
import configparser
import subprocess
import json
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip
from PyQt5.QtCore import Qt, QTimer, QEvent, QPoint
from labels import Labels
from layouts import Layouts
from message import Message
from buttons import Buttons
from exit import Exit
from threading import Thread
from active_window import WindowName
from rich.console import Console
from rich.text import Text
from battery_bar import Battery
from updates import *
from shrink_desktop import register_as_taskbar
from widgets import load_bar_widgets_from_json
from BlurWindow.blurWindow import blur

class Bar(QWidget):
    def __init__(self):
        super().__init__()
        self.loadConfig()
        self.initUI()
        if self.shrink_desktop:
            register_as_taskbar(QApplication, self.taskbar_height, self.widthGap, self.winId, self.bar_position)
        self.custom_timer = []
        load_bar_widgets_from_json('config/config.json', self.layouts.left_layout, self.layouts.right_layout, self.layouts.middle_layout, self.buttons, self.labels, self.progress_bar, self.get_window, self.custom_timer)


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
        self.bar_position = config.get('Bar', 'BarPosition')
        self.use_blur = config.getboolean('Bar', 'UseBlur')
        self.shrink_desktop = config.getboolean('Bar', 'ShrinkDekstop')



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
        self.layouts = Layouts(self.bar_position)
        self.SetupUI()

        self.buttons = Buttons(css = self.css, trash_tooltip = self.show_tooltip_above_trash, hide_tooltip = self.hide_tooltip, launch_laucher = self.launch_laucher)
        self.buttons.menu_button()

        self.buttons.trash_button()
        self.buttons.launcher_button()
        
        self.labels = Labels(self.css)

        self.progress_bar = Battery(css = self.css)

        self.get_window = WindowName(self)


        self.runTimers()

        os.system('cls')
        self.rainbow_text("---------------YOU CAN NOW CLOSE THIS TERMINAL!!---------------")        


        self.labels.sys_info_label.installEventFilter(self)

    def runTimers(self):
        with open('config/config.json', "r") as file:
            widgets = json.load(file)

            for widget in widgets['bar widgets']:
                if 'system info' in widget:
                    use_system_info = widget['system info'].lower()
                
                if 'battery' in widget:
                    use_battery = widget['battery'].lower()
                
                if 'time' in widget:
                    use_time = widget['time'].lower()
                
                if 'wifi' in widget:
                    use_wifi = widget['wifi'].lower()

        if use_system_info == 'true':
            self.tooltip_timer = QTimer(self)
            self.tooltip_timer.timeout.connect(lambda: updateTooltip(self.labels, self.bar_position))
            self.tooltip_timer.setInterval(1000)
            
            timer = QTimer(self)
            timer.timeout.connect(lambda: updateSystemInfo(self.labels, self.bar_position))
            timer.start(1000)

        if use_battery == 'true':
            update_battery = QTimer(self)
            update_battery.timeout.connect(lambda: updateBattery(self.progress_bar))
            self.progress_bar.enterEvent = self.show_tooltip_above_battery
            self.progress_bar.leaveEvent = self.hide_tooltip
            update_battery.start(1000)


        if use_time == 'true':
            time_timer = QTimer(self)
            time_timer.timeout.connect(lambda: updateTime(self.labels, self.display_date_layout, self.display_time_layout))
            time_timer.start(1000)

        
        updateWifiLabel(self.labels)
        if use_wifi == 'true':
            wifi_timer = QTimer(self)
            wifi_timer.timeout.connect(lambda: updateWifiLabel(self.labels))
            self.labels.wifi_icon.enterEvent = self.show_tooltip_above_wifi
            self.labels.wifi_icon.leaveEvent = self.hide_tooltip
            wifi_timer.start(1000)
            print("Using Wifi")

    def SetupUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        screen_width = QApplication.desktop().screenGeometry().width()
        screen_height = QApplication.desktop().screenGeometry().height()

        taskbar_height = self.taskbar_height
        width_gap = self.widthGap
        height_gap = self.heightGap

        if self.bar_position == 'top':
            self.setGeometry(
                width_gap,
                height_gap,
                screen_width - (2 * width_gap),
                taskbar_height
            )
            self.setFixedHeight(taskbar_height)
        
        elif self.bar_position == 'left':
            self.setGeometry(
                height_gap,
                width_gap,
                taskbar_height,
                screen_height - (2 * width_gap)
            )
            self.setFixedWidth(taskbar_height)

        elif self.bar_position == 'right':
            self.setGeometry(
                screen_width - taskbar_height - width_gap,
                height_gap,
                taskbar_height,
                screen_height - (2 * width_gap)
            )
            self.setFixedWidth(taskbar_height)

        elif self.bar_position == 'bottom':
            self.setGeometry(
                width_gap,
                QApplication.desktop().screenGeometry().height() - taskbar_height - height_gap,
                screen_width - (2 * width_gap),
                taskbar_height
            )
            self.setFixedHeight(taskbar_height)


        if self.taskbar_height_warning:
            self.taskbar_warning()
        
        self.setObjectName('window')

        with open('config/style.css', 'r') as f:
            self.css = f.read()
        self.setStyleSheet(self.css)



        if self.use_blur:
            blur(self.winId(), Dark = True, Acrylic = True)

        self.setLayout(self.layouts.main_layout)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        alpha = int(self.color[-1])
        
        painter.setBrush(QColor(int(self.color[0]), int(self.color[1]), int(self.color[2]), alpha = alpha))
        painter.drawRoundedRect(self.rect(), int(self.border_radius1), int(self.border_radius2))

    def launch_laucher(self):
        subprocess.Popen(['python', 'app_launcher.py'])


    def show_tooltip_above_wifi(self, event):
        tooltip_position = self.labels.wifi_icon.mapToGlobal(QPoint(0, -self.labels.wifi_icon.height() - 40))
        QToolTip.showText(tooltip_position, self.labels.wifi_icon.toolTip(), self.labels.wifi_icon)
        event.accept()

    def show_tooltip_above_battery(self, event):
        tooltip_position = self.progress_bar.mapToGlobal(QPoint(0, -self.progress_bar.height() - 40))
        QToolTip.showText(tooltip_position, self.progress_bar.toolTip(), self.progress_bar)
        event.accept()


    def show_tooltip_above_trash(self, event):
        if self.buttons.trash_enabled:
            tooltip_position = self.buttons.custom_trash.mapToGlobal(QPoint(0, -self.buttons.custom_trash.height() - 40))
            QToolTip.showText(tooltip_position, self.buttons.custom_trash.toolTip(), self.buttons.custom_trash)
        else:
            tooltip_position = self.buttons.trash_button_.mapToGlobal(QPoint(0, -self.buttons.trash_button_.height() - 40))
            QToolTip.showText(tooltip_position, self.buttons.trash_button_.toolTip(), self.buttons.trash_button_)
        event.accept()

    def hide_tooltip(self, event):
        QToolTip.hideText()
        event.accept()


    def eventFilter(self, obj, event):
        if obj == self.labels.sys_info_label:
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
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
        app = QApplication(sys.argv)

        fluxbar = Bar()
        fluxbar.setWindowTitle("WinBar")
        fluxbar.show()
        sys.exit(app.exec_())

    except OSError as e:
        print("Error", e)
