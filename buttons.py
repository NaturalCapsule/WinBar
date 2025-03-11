from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from PyQt5.QtSvg import QSvgWidget
from utils import Utils
from menu import Menu


class Buttons:
    def __init__(self, css, trash_tooltip, hide_tooltip, launch_laucher):
        self.isEnabled_ = False
        self.trash_enabled = False
        self.launcher_enabled = False
        self.css = css
        self.trash_tooltip = trash_tooltip
        self.hide_tooltip = hide_tooltip
        self.launch_laucher = launch_laucher
    
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
        self.custom_trash.enterEvent = self.trash_tooltip
        self.custom_trash.leaveEvent = self.hide_tooltip


        self.trash_button_ = QPushButton()
        self.trash_button_.setObjectName('trashButton')
        self.trash_button_.setStyleSheet(self.css)
        self.trash_button_.setToolTip("Delets all temp files")
        self.trash_button_.clicked.connect(Utils.delete_temp_files)
        self.trash_button_.enterEvent = self.trash_tooltip
        self.trash_button_.leaveEvent = self.hide_tooltip
        # self.trash_button_.

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