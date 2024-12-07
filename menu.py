from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import QPoint
import os


class Menu:
    def __init__(self, parent) -> None:
        os.system('powercfg -h off')
        self.parent = parent

    def open_menu(self):
        menu = QMenu(self.parent)
        menu.setObjectName('menu')

        with open('config/style.css', 'r') as f:
            css = f.read()

        menu.setStyleSheet(css)

        # Sleep action
        sleep = QAction("Sleep", self.parent)
        sleep.setIcon(QIcon('svgs/sleep.svg'))
        sleep.triggered.connect(lambda: self.sleep())
        menu.addAction(sleep)

        # Reset action
        reset = QAction("Reset", self.parent)
        reset.setIcon(QIcon('svgs/reset.svg'))
        reset.triggered.connect(lambda: self.reset())
        menu.addAction(reset)

        # Shutdown action
        turn_off = QAction("Turn Off", self.parent)
        turn_off.setIcon(QIcon('svgs/power.svg'))
        turn_off.triggered.connect(lambda: self.shutdown())
        menu.addAction(turn_off)

        lock = QAction("Lock", self.parent)
        lock.setIcon(QIcon('svgs/lock.svg'))
        lock.triggered.connect(lambda: self.lock())
        menu.addAction(lock)

        menu.exec_(self.parent.mapToGlobal(QPoint(0, -self.parent.height() - 100)))

    def shutdown(self):
        os.system('shutdown /s /t 0')

    def reset(self):
        os.system('shutdown /r /t 0')

    def sleep(self):
        os.system('rundll32.exe powrprof.dll,SetSuspendState Sleep')

    def lock(self):
        lock = os.system('rundll32.exe user32.dll,LockWorkStation')
        return lock