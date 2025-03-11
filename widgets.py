import json
from updates import *
from functools import partial
from PyQt5.QtWidgets import QLabel, QPushButton
from docks import DockApp
import subprocess

def cmd(command):
    subprocess.Popen(command, shell=True)

def load_widgets_from_json(file_path, left_layout, right_layout, middle_layout, buttons, labels, progress_bar, get_window):
    try:
        with open(file_path, "r") as file:
            widgets = json.load(file)

            for widget in widgets['widgets']:
                layout_target = widget.get("layout", "SELECT A LAYOUT")
                widget_item = None


                if "battery" in widget:
                    widget_item = progress_bar

                # if "wifi" in widget:
                elif "wifi" in widget:
                    wifi_con = labels.wifi_icon
                    if widget.get("onlineIcon") and widget.get("offlineIcon"):
                        labels.offline_icon = widget["offlineIcon"]
                        labels.online_icon = widget["onlineIcon"]
                        wifi_con = labels.wifi_icon
                    widget_item = wifi_con

                elif "time" in widget:
                    widget_item = labels.time_label

                elif "window title" in widget:
                    widget_item = get_window

                elif "system info" in widget:
                    widget_item = labels.sys_info_label

                elif "menu" in widget:
                    menu_ico = buttons.menu
                    if widget.get("icon"):
                        buttons.custom_menu.setText(widget["icon"])
                        buttons.isEnabled_ = True
                        menu_ico = buttons.custom_menu
                    widget_item = menu_ico

                elif "trash" in widget:
                    trash_ico = buttons.trash_button_
                    if widget.get("icon"):
                        buttons.custom_trash.setText(widget["icon"])
                        buttons.trash_enabled = True
                        trash_ico = buttons.custom_trash
                    widget_item = trash_ico

                elif "launcher" in widget:
                    launcher_ico = buttons.launcher_button_
                    if widget.get("icon"):
                        buttons.custom_launcher.setText(widget["icon"])
                        buttons.launcher_enabled = True
                        launcher_ico = buttons.custom_launcher
                    widget_item = launcher_ico

                elif "type" in widget:
                    if widget["type"] == "label":
                        widget_item = QLabel(widget["text"])
                        widget_item.setObjectName(widget["name"])
                        # if widget['text'] == 'cputemp':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_cpu_temp)
                #             timer.start(1000)

                #             widget_item = self.cpu_temp_label
                #         elif widget['text'] == 'cpuUsage':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_cpu_usage)
                #             timer.start(1000)

                #             widget_item = labels.cpu_usage_label

                #         elif widget['text'] == 'ramusage':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_ram_usage)
                #             timer.start(1000)

                #             widget_item = labels.ram_usage_label

                #         elif widget['text'] == 'ramtotalGB':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_ram_totalGB)
                #             timer.start(1000)

                #             widget_item = labels.ram_usedtotalgb_label

                #         elif widget['text'] == 'ramusedGB':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_ram_usedGB)
                #             timer.start(1000)

                #             widget_item = labels.ram_usedgb_label

                #         elif widget['text'] == 'ramusage':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_ram_usage)
                #             timer.start(1000)

                #             widget_item = labels.ram_usage_label

                #         elif widget['text'] == 'nvidiatemp':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_nvidia_temp)
                #             timer.start(1000)

                #             widget_item = labels.nvidia_temp_label

                #         elif widget['text'] == 'nvidiausage':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_nvidia_usage)
                #             timer.start(1000)

                #             widget_item = labels.nvidia_usage_label

                #         elif widget['text'] == 'nvidiaTOTVram':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_nvidia_totVram)
                #             timer.start(1000)

                #             widget_item = labels.nvidia_totvram_label

                #         elif widget['text'] == 'nvidiaUSEDVram':
                #             timer = QTimer(self)
                #             timer.timeout.connect(self.update_nvidia_usedVram)
                #             timer.start(1000)

                #             widget_item = labels.nvidia_usedvram_label

                        # else:
                        #     widget_item = QLabel(widget["text"])
                        # widget_item.setObjectName(widget["name"])
                        
                    elif widget["type"] == "button":
                        widget_item = QPushButton(widget["text"])
                        widget_item.setObjectName(widget["name"])
                        if "action" in widget:
                            widget_item.clicked.connect(partial(cmd, widget["action"]))

                if widget_item:
                    if layout_target == "left":
                        left_layout.addWidget(widget_item)
                    elif layout_target == "right":
                        right_layout.addWidget(widget_item)
                    elif layout_target == "middle":
                        middle_layout.addWidget(widget_item)

        docks = DockApp().dock_buttons

        for widget in widgets['widgets']:
            if widget.get('docks') == "show docks":
                for dock_button in docks:
                    layout_target = widget['layout']
                    if layout_target == 'left':
                        left_layout.addWidget(dock_button)
                    elif layout_target == 'right':
                        right_layout.addWidget(dock_button)
                    elif layout_target == 'middle':
                        middle_layout.addSpacing(20)
                        middle_layout.addWidget(dock_button)
    except Exception as e:
        print("Error Loading Widget", e)