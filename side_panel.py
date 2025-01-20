from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMenu, QAction, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, QPoint
from PyQt5.QtGui import QColor, QPainter, QRegion
import os
import keyboard
from weather import Weather
import configparser
from windows_mods import Mods
from configparser import ConfigParser
import time
from exit import Exit
from threading import Thread
import subprocess
# import tkinter.messagebox as message
from message import Message
from date import get_calendar

import pyuac
import elevate

class SidePanel(QWidget):
    def __init__(self):
        super().__init__()

        self.config = ConfigParser()
        self.config.read('config/config.ini')
        
        self.panel_color = self.config.get('Panel', 'panelColor')
        self.colors = self.panel_color.split(',')
        

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        self.username = os.getlogin()

        screen = QApplication.primaryScreen().availableGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.panel_width = int(self.screen_width * 0.3)

        self.setGeometry(-self.panel_width, 0, self.panel_width, self.screen_height)

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMask(QRegion(self.rect(), QRegion.Rectangle))
        
        self.setObjectName("SidePanel")
        
        with open('config/style.css', 'r') as f:
            self.css = f.read()
        self.setStyleSheet(self.css)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_keys)
        self.timer.start(100)

        self.calendar = get_calendar()

        self.date_timer = QTimer(self)
        self.date_timer.timeout.connect(self.update_date)
        self.date_timer.start(1000)

        self.weather = Weather()
        self.temp = self.weather.get_temp()
        self.sky = self.weather.get_sky()

        self.temp_timer = QTimer(self)
        self.temp_timer.timeout.connect(self.update_weather)
        self.temp_timer.start(10000)

        self.setup_side_panel()
        self.search_bar()
        self.animation = QPropertyAnimation(self, b"geometry")

        os.system('cls')
        print("---------------YOU CAN NOW CLOSE THIS TERMINAL!!---------------")

        self.monitor_exit_thread = Thread(target=self.exit_function, daemon=True)
        self.monitor_exit_thread.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(int(self.colors[0]), int(self.colors[1]), int(self.colors[2])))
        painter.drawRoundedRect(self.rect(), 20, 20)

    def animate_panel(self, show):
        self.animation.setDuration(300)
        self.gap = 10
        self.top_gap = 25

        if show:
            self.animation.setStartValue(QRect(-self.panel_width, self.top_gap, self.panel_width, self.screen_height - self.top_gap))
            self.animation.setEndValue(QRect(self.gap, self.top_gap, self.panel_width, self.screen_height - self.top_gap))
        else:
            self.animation.setStartValue(QRect(self.gap, self.top_gap, self.panel_width, self.screen_height - self.top_gap))
            self.animation.setEndValue(QRect(-self.panel_width, self.top_gap, self.panel_width, self.screen_height - self.top_gap))

        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def setup_side_panel(self):
        self.welcome_label = QLabel(f"Hi, {self.username}!", self)
        self.welcome_label.setObjectName("SideWelcome")
        self.welcome_label.setStyleSheet(self.css)

        self.city_label = QLabel(f"Your Current City: {self.weather.get_city()}", self)
        self.city_label.setObjectName("SideCity")
        self.city_label.setStyleSheet(self.css)

        self.sky_label = QLabel(self.sky, self)
        self.sky_label.setObjectName("SideSky")
        self.sky_label.setStyleSheet(self.css)

        self.temp_label = QLabel(self.temp, self)
        self.temp_label.setObjectName("SideTemp")
        self.temp_label.setStyleSheet(self.css)

        self.date_label = QLabel(self.calendar, self)
        self.date_label.setObjectName("SideDate")
        self.date_label.setStyleSheet(self.css)

        self.menu_button = QPushButton("Performance", self)
        self.menu_button.clicked.connect(self.menu)
        self.menu_button.setObjectName("SideButtons")

        self.close_button = QPushButton("Close Panel", self)
        self.close_button.clicked.connect(self.closePanel_button)
        self.close_button.setObjectName("SideButtons")

        self.load_widget_positions()
        self.apply_widget_positions()

    def closePanel_button(self):
        self.animation.setStartValue(QRect(self.gap, self.top_gap, self.panel_width, self.screen_height - self.top_gap))
        self.animation.setEndValue(QRect(-self.panel_width, self.top_gap, self.panel_width, self.screen_height - self.top_gap))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()


    def menu(self):
        mods = Mods()

        self._menu = QMenu(self)
        self._menu.setObjectName("SideMenu")
        self._menu.setStyleSheet(self.css)

        ultimate = QAction("Ultimate Performance")
        ultimate.triggered.connect(mods.ultimate_mod)
        self._menu.addAction(ultimate)

        high = QAction("High Performance")
        high.triggered.connect(mods.high_mod)
        self._menu.addAction(high)

        balanced = QAction("Balanced Performance")
        balanced.triggered.connect(mods.balanced_mod)
        self._menu.addAction(balanced)

        low = QAction("Power Saver (Low Performance)")
        low.triggered.connect(mods.low_mod)
        self._menu.addAction(low)

        button_pos = self.menu_button.mapToGlobal(QPoint(0, 0))
        menu_pos = QPoint(button_pos.x(), button_pos.y() - self._menu.height())
        self._menu.exec_(menu_pos)

    def search_bar(self):

        self.searchbar = QLineEdit(self)
        self.searchbar.setPlaceholderText("Search the net here...")
        self.searchbar.returnPressed.connect(self.perform_search)

        self.searchbar.setObjectName("SideSearch")

        self.load_widget_positions()
        self.apply_widget_positions()

    def perform_search(self):
        query = self.searchbar.text()

        firefox_path = r"C:/Program Files/Mozilla Firefox/firefox.exe"
        chrome_path = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

        firefox = self.config.getboolean("Panel", "useFirefox")
        chrome = self.config.getboolean("Panel", "useChrome")


        if firefox and chrome:
            Message.idk_what_to_call()

        
        if firefox:
            web_engine = "firefox"
            if os.path.exists(firefox_path):
                subprocess.run([firefox_path, "--search", query])
            else:
                Message.message(web_engine = web_engine)

        if chrome:
            web_engine = "chrome"
            if os.path.exists(chrome_path):
                subprocess.run(f"start chrome https://www.google.com/search?q={query}", shell = True)
            else:
                Message.message(web_engine = web_engine)

        self.searchbar.clear()

    def load_widget_positions(self):
        config = configparser.ConfigParser()
        config.read("config/config.ini")
        self.widget_positions = {}
        if "WidgetPositions" in config:
            for key, value in config["WidgetPositions"].items():
                try:
                    x, y = map(float, value.split(","))
                    self.widget_positions[key] = (x, y)
                except ValueError:
                    print(f"Invalid position format for {key}: {value}")
        else:
            print("No [WidgetPositions] section in config.ini")

    def apply_widget_positions(self):
        for widget_name, position in self.widget_positions.items():
            widget = getattr(self, widget_name, None)
            if widget:
                x = int(self.width() * position[0])
                y = int(self.height() * position[1])

                widget.move(x, y)
            else:
                print(f"Widget '{widget_name}' not found")

    def exit_function(self):
        while True:
            if Exit.exit():
                print("Exiting application...")
                QApplication.quit()
                break
            time.sleep(0.1) 

    def update_date(self):
        date = get_calendar()
        self.date_label.setText(date)

    def update_weather(self):
        weather = Weather()
        self.temp_label.setText(weather.get_temp())
        self.sky_label.setText(weather.get_sky())

    def check_keys(self):
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('y'):
            self.toggle_side_panel()

    def toggle_side_panel(self):
        if self.x() < 0:
            self.show()
            self.animate_panel(show=True)
        else:
            self.animate_panel(show=False)


app = QApplication([])
side = SidePanel()
side.show()
app.exec_()