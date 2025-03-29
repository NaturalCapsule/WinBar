import os
import keyboard
import time
import configparser
import subprocess
import speech_recognition as sr
import asyncio
from PyQt5.QtCore import  Qt, QTimer, QPropertyAnimation, QThread, pyqtSignal, QTimer, QRect, QEasingCurve, QPoint, QSize
from PyQt5.QtGui import QColor, QPainter, QRegion, QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsBlurEffect, QApplication, QWidget, QLabel, QPushButton, QMenu, QAction, QLineEdit
from weather import Weather
from windows_modes import Modes
from configparser import ConfigParser
from exit import Exit
from threading import Thread
from message import Message
from clipboard import ClipBoard
from rich.console import Console
from rich.text import Text

from updates import *
from date import get_calendar_html
from screenshot import take_screenshot, take_shot
from widgets import load_panel_widgets_from_json
from media import *


class MediaWorker(QThread):
    media_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)

    async def fetch_media(self):
        session_manager = await MediaManager.request_async()
        current_session = session_manager.get_current_session()

        try:
            info = await current_session.try_get_media_properties_async()
            title = info.title
            artist = info.artist
            output = f"{title}\n By\n{artist}"
            return output
        except Exception:
            return "No active media session to control."

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.fetch_media())
        self.media_signal.emit(result)


class VoiceCommandThread(QThread):
    command_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            command = self.listen_command()
            if command:
                self.command_signal.emit(command)

    def listen_command(self):
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command.lower()
            
        except sr.UnknownValueError:
            print("did not understand that.")
            return ""
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return ""

username = os.getlogin()

class SidePanel(QWidget):
    def __init__(self):
        super().__init__()


        self.load_config()

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

        self.calendar = get_calendar_html()

        self.weather = Weather()
        self.temp = self.weather.get_temp()
        self.sky = self.weather.get_sky()

        self.timers()

        self.clipboard = ClipBoard()
        self.setup_side_panel()
        load_panel_widgets_from_json('config/config.json', self)
        self.search_bar()


        self.animation = QPropertyAnimation(self, b"geometry")

        os.system('cls')
        self.rainbow_text("---------------YOU CAN NOW CLOSE THIS TERMINAL!!---------------")

        self.monitor_exit_thread = Thread(target=self.exit_function, daemon=True)
        self.monitor_exit_thread.start()

    def rainbow_text(self, text):
        console = Console()
        colors = ["red", "orange1", "yellow", "green", "cyan", "blue", "magenta", 'black', 'cyan']
        styled_text = Text()
        
        for i, char in enumerate(text):
            styled_text.append(char, style=colors[i % len(colors)])
        
        console.print(styled_text)

    def load_config(self):
        self.config = ConfigParser()
        self.config.read('config/config.ini')

        self.panel_color = self.config.get('Panel', 'panelColor')
        self.colors = self.panel_color.split(',')

        self.pix_radius = self.config.get('Panel', 'mediaBorderRadius')
        self.pix_radius = self.pix_radius.split(', ')
        self.rad1 = self.pix_radius[0]
        self.rad2 = self.pix_radius[1]

        self.panel_radius = self.config.get('Panel', 'panelBorderRadius')
        self.panel_rad1, self.panel_rad2 = self.panel_radius.split(', ')[0], self.panel_radius.split(', ')[1]

        self.media_icon = self.config.get('Panel', 'mediaIconSize')
        self.media_icon1, self.media_icon2 = self.media_icon.split(', ')[0], self.media_icon.split(', ')[1]
        self.media_icon1, self.media_icon2 = int(self.media_icon1), int(self.media_icon2)



    def timers(self):
        self.voice_thread = VoiceCommandThread()
        self.voice_thread.command_signal.connect(self.execute_command)
        self.voice_thread.start()

        keys_timer = QTimer(self)
        keys_timer.timeout.connect(lambda: check_keys(self.toggle_side_panel))
        keys_timer.start(100)

        date_timer = QTimer(self)
        date_timer.timeout.connect(lambda: update_date(get_calendar_html, self.date_label))
        date_timer.start(1000)
        
        screenshot_timer = QTimer(self)
        screenshot_timer.timeout.connect(take_screenshot)
        screenshot_timer.start(100)

        media_timer = QTimer(self)
        media_timer.timeout.connect(self.update_media)
        media_timer.start(1000)
        
        image_timer = QTimer(self)
        image_timer.timeout.connect(self.pix)
        image_timer.start(1000)

        image_timer2 = QTimer(self)
        image_timer2.timeout.connect(self.pix_)
        image_timer2.start(1000)

        save_timer = QTimer(self)
        save_timer.timeout.connect(get_image)
        save_timer.start(100)

        button_timer = QTimer(self)
        button_timer.timeout.connect(self.change_button)
        button_timer.start(100)

        temp_timer = QTimer(self)
        temp_timer.timeout.connect(lambda: update_weather(Weather, self.temp_label, self.sky_label))
        temp_timer.start(10000)

    def rewind_action(self):
        async def rewind_action_():
            await rewind()

        return asyncio.run(rewind_action_())
    
    def fast_forward_action(self):
        async def fast_forward_action_():
            await fast_forward()

        return asyncio.run(fast_forward_action_())

    def update_media(self):
        self.worker = MediaWorker()
        self.worker.media_signal.connect(self.update_media_label)
        self.worker.start()

    def update_media_label(self, title):
        self.media_label.setText(title)
        self.media_label.adjustSize()
        self.media_label.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        alpha = max(0, min(int(self.colors[-1]), 255))

        painter.setBrush(QColor(int(self.colors[0]), int(self.colors[1]), int(self.colors[2]), alpha = alpha))
        painter.drawRoundedRect(self.rect(), int(self.panel_rad1), int(self.panel_rad2))


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

    def change_button(self):
        async def get_session():
            try:
                session_manager = await MediaManager.request_async()
                current_session = session_manager.get_current_session()
                playback_status = current_session.get_playback_info().playback_status
                if playback_status == 5:
                    self.media_button.setIcon(QIcon("svgs/play.svg"))

                else:
                    self.media_button.setIcon(QIcon("svgs/pause.svg"))
            except AttributeError:
                pass

        pause_play = asyncio.run(get_session())
        return pause_play

    def play_pause(self):
        async def get_session():
            try:
                session_manager = await MediaManager.request_async()
                current_session = session_manager.get_current_session()

                return await current_session.try_toggle_play_pause_async()
            except AttributeError:
                pass

        pause_play = asyncio.run(get_session())
        return pause_play

    def setup_side_panel(self):
        try:
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

            self.media_label = QLabel("Checking...", self)
            self.media_label.setObjectName("SideMedia")
            self.media_label.setStyleSheet(self.css)
            self.media_label.setWordWrap(True)

            self.media_image = QLabel(self)
            self.media_image.setPixmap(self.pix())
            self.media_image.setScaledContents(True)
            self.media_image.setFixedSize(self.panel_width - 30, int(self.screen_height * 0.2))
            self.blur_image = QGraphicsBlurEffect()
            self.blur_image.setBlurRadius(15)
            self.media_image.setGraphicsEffect(self.blur_image)
            
            self.media_image2 = QLabel(self)
            self.media_image2.setPixmap(self.pix_())
            self.media_image2.setScaledContents(True)
            self.media_image2.setFixedSize(250, 150)
            x, y = self.move_widget([0.35, .52])
            self.media_image2.move(x, y)


            self.media_button = QPushButton(self)
            self.media_button.setIcon(QIcon('svgs/play.svg'))
            self.media_button.setObjectName("MediaButton")
            self.media_button.setStyleSheet(self.css)
            self.media_button.clicked.connect(self.play_pause)
            self.media_button.setFixedSize(self.media_icon1, self.media_icon2)
            self.media_button.setIconSize(QSize(self.media_icon1, self.media_icon2))

            self.clipboard_button = QPushButton(self)
            self.clipboard_button.setIcon(QIcon("svgs/clipboard.svg"))
            self.clipboard_button.clicked.connect(self.clip_board)
            self.clipboard_button.setObjectName("ClipButton")
            self.clipboard_button.setStyleSheet(self.css)

            self.mini_game = QPushButton(self)
            self.mini_game.setIcon(QIcon("svgs/rocket.svg"))
            self.mini_game.clicked.connect(self.run_miniGame)
            self.mini_game.setObjectName("MiniGameButton")
            self.mini_game.setStyleSheet(self.css)

            self.menu_button = QPushButton("Performance", self)
            self.menu_button.clicked.connect(self.menu)
            self.menu_button.setObjectName("PerformanceButton")
            self.menu_button.setStyleSheet(self.css)

            self.close_button = QPushButton("Close Panel", self)
            self.close_button.clicked.connect(self.closePanel_button)
            self.close_button.setObjectName("CloseButton")
            self.close_button.setStyleSheet(self.css)

            self.forward_button = QPushButton("", self)
            self.forward_button.setIcon(QIcon('svgs/fast-forward.svg'))
            self.forward_button.clicked.connect(self.fast_forward_action)
            self.forward_button.setObjectName('forwardButton')
            self.forward_button.setStyleSheet(self.css)
            self.forward_button.setFixedSize(self.media_icon1, self.media_icon2)
            self.forward_button.setIconSize(QSize(self.media_icon1, self.media_icon2))

            self.rewind_button = QPushButton("", self)
            self.rewind_button.setIcon(QIcon('svgs/rewind.svg'))
            self.rewind_button.clicked.connect(self.rewind_action)
            self.rewind_button.setObjectName('rewindButton')
            self.rewind_button.setStyleSheet(self.css)
            self.rewind_button.setFixedSize(self.media_icon1, self.media_icon2)
            self.rewind_button.setIconSize(QSize(self.media_icon1, self.media_icon2))

            self.load_widget_positions()
            self.apply_widget_positions()
        except Exception as e:
            print(e)


    def pix(self):
        path = fr"c:\Users\{self.username}\AppData\Local\Temp\thumbnail.jpg"
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Pixmap is null!")
            return

        pixmap = pixmap.scaled(self.panel_width - 30, int(self.screen_height * 0.2), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # pixmap = pixmap.scaled(250, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        mask = QPixmap(pixmap.size())
        mask.fill(Qt.transparent)

        painter = QPainter(mask)
        if painter.isActive():
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.white)
            painter.setPen(Qt.transparent)
            rect = QRect(0, 0, pixmap.width(), pixmap.height())
            painter.drawRoundedRect(rect, int(self.rad1), int(self.rad2))
            painter.end()

        pixmap.setMask(mask.createHeuristicMask())

        current_session = c_session_info()
        if current_session != "No active media session to control.":
            self.media_image.setPixmap(pixmap)
            # self.media_image2.setPixmap(pixmap)
        else:
            blank_pixmap = QPixmap(self.media_image.size())
            if blank_pixmap.isNull() or blank_pixmap.size().isEmpty():
                print("Invalid media_image size")
                return
            
            blank_pixmap.fill(Qt.transparent)
            painter = QPainter(blank_pixmap)
            if painter.isActive():
                painter.setPen(QColor("gray"))
                painter.drawText(blank_pixmap.rect(), Qt.AlignCenter, "No Media")
                painter.end()

            self.media_image.setPixmap(blank_pixmap)
            # self.media_image2.setPixmap(blank_pixmap)

        return pixmap

    def pix_(self):
        path = fr"c:\Users\{self.username}\AppData\Local\Temp\thumbnail.jpg"
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Pixmap is null!")
            return

        pixmap = pixmap.scaled(250, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # pixmap = pixmap.scaled(250, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        mask = QPixmap(pixmap.size())
        mask.fill(Qt.transparent)

        painter = QPainter(mask)
        if painter.isActive():
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.white)
            painter.setPen(Qt.transparent)
            rect = QRect(0, 0, pixmap.width(), pixmap.height())
            painter.drawRoundedRect(rect, int(self.rad1), int(self.rad2))
            painter.end()

        pixmap.setMask(mask.createHeuristicMask())

        current_session = c_session_info()
        if current_session != "No active media session to control.":
            self.media_image2.setPixmap(pixmap)
        else:
            blank_pixmap = QPixmap(self.media_image2.size())
            if blank_pixmap.isNull() or blank_pixmap.size().isEmpty():
                print("Invalid media_image size")
                return
            
            blank_pixmap.fill(Qt.transparent)
            painter = QPainter(blank_pixmap)
            if painter.isActive():
                painter.setPen(QColor("gray"))
                painter.drawText(blank_pixmap.rect(), Qt.AlignCenter, "No Media")
                painter.end()

            self.media_image2.setPixmap(blank_pixmap)

        return pixmap

    def clip_board(self):
        self.clipboard.toggle_side_clipboard()

    def closePanel_button(self):
        self.animation.setStartValue(QRect(self.gap, self.top_gap, self.panel_width, self.screen_height - self.top_gap))
        self.animation.setEndValue(QRect(-self.panel_width, self.top_gap, self.panel_width, self.screen_height - self.top_gap))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def run_miniGame(self):
        game_dir = os.path.join(os.getcwd(), "space-invaders")
        subprocess.run(["python", "main.py"], cwd = game_dir)

    def menu(self):
        modes = Modes()

        self._menu = QMenu(self)
        self._menu.setObjectName("SideMenu")
        self._menu.setStyleSheet(self.css)

        ultimate = QAction("Ultimate Performance")
        ultimate.triggered.connect(modes.ultimate_mod)
        self._menu.addAction(ultimate)

        high = QAction("High Performance")
        high.triggered.connect(modes.high_mod)
        self._menu.addAction(high)

        balanced = QAction("Balanced Performance")
        balanced.triggered.connect(modes.balanced_mod)
        self._menu.addAction(balanced)

        low = QAction("Power Saver (Low Performance)")
        low.triggered.connect(modes.low_mod)
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

        if not firefox and not chrome:
            Message.uhhh()

        if firefox:
            web_engine = "firefox"
            if os.path.exists(firefox_path):
                subprocess.run([firefox_path, "--search", query])
            else:
                Message.message(web_engine = web_engine)

        if chrome:
            web_engine = "chrome"
            new_query = query.split(" ")
            chrome_query = "+".join(new_query)
            if os.path.exists(chrome_path):
                subprocess.run(f"start chrome https://www.google.com/search?q={chrome_query}", shell = True)
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

    def move_widget(self, position):
        x = int(self.width() * position[0])
        y = int(self.height() * position[1])
        return x, y

    def exit_function(self):
        while True:
            if Exit.exit():
                print("Exiting application...")
                QApplication.quit()
                break
            time.sleep(0.1) 

    def execute_command(self, command):
        if "open panel" in command:
            if self.x() < 0:
                self.show()
                self.animate_panel(show=True)

        elif "close panel" in command:
            self.animate_panel(show = False)

        elif "search" in command:
            command = command.split(" ")
            command = command[1:]

            self.new_command = " ".join(command)
            firefox_path = r"C:/Program Files/Mozilla Firefox/firefox.exe"
            chrome_path = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

            firefox = self.config.getboolean("Panel", "useFirefox")
            chrome = self.config.getboolean("Panel", "useChrome")


            if firefox:
                if os.path.exists(firefox_path):
                    subprocess.run([firefox_path, "--search", self.new_command])

            if chrome:
                new_query = self.new_command.split(" ")
                chrome_query = "+".join(new_query)
                if os.path.exists(chrome_path):
                    subprocess.run(f"start chrome https://www.google.com/search?q={chrome_query}", shell = True)

        elif "open clipboard" in command:
            if self.clipboard.x() < 0:
                self.clipboard.show()
                self.clipboard.animate_app(show = True)

        elif "close clipboard" in command:
            self.clipboard.animate_app(show = False)

        elif "take a screenshot" in command:
            take_shot()

    def toggle_side_panel(self):
        if self.x() < 0:
            self.show()
            self.animate_panel(show=True)
        else:
            self.animate_panel(show=False)


def run_loop():
    app = QApplication([])

    _side = SidePanel()
    _side.setWindowTitle("WinBar")
    
    Thread(target=start_asyncio_loop, args=(_side,), daemon=True).start()

    _side.show()
    app.exec_()

run_loop()