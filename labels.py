from PyQt5.QtWidgets import QLabel
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt


class Labels:
    def __init__(self, css):
        self.sys_info_label = QLabel("Loading...")
        # self.sys_info_label.setAlignment(Qt.AlignCenter)
        self.sys_info_label.setObjectName('infoLabel')
        self.sys_info_label.setStyleSheet(css)


        self.time_label = QLabel("")
        # self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setObjectName('timeLabel')
        self.time_label.setStyleSheet(css)

        self.cpu_temp_label = QLabel()
        self.cpu_usage_label = QLabel()
        self.ram_usage_label = QLabel()
        self.ram_usedgb_label = QLabel()
        self.ram_usedtotalgb_label = QLabel()
        self.nvidia_temp_label = QLabel()
        self.nvidia_usedvram_label = QLabel()
        self.nvidia_totvram_label = QLabel()
        self.nvidia_usage_label = QLabel()

        self.wifi_label()

    def wifi_label(self):
        self.wifi_ico = QLabel()
        self.wifi_ico.setObjectName('WifiLabel')
        self.offline_icon = ""
        self.online_icon = ""
        self.wifi_icon = QSvgWidget()
        self.wifi_icon.setFixedSize(20, 20)