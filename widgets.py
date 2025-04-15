import json
from updates import *
from functools import partial
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import QTimer
from docks import DockApp
from utils import Utils
from nvidia import Nvidia
import subprocess

def cmd(command):
    subprocess.Popen(command, shell=True)

def load_bar_widgets_from_json(file_path, left_layout, right_layout, middle_layout, buttons, labels, progress_bar, get_window, timers):
    try:
        # timers = []
        with open(file_path, "r") as file:
            widgets = json.load(file)

            for widget in widgets['bar widgets']:
                layout_target = widget.get("layout", "SELECT A LAYOUT")
                widget_item = None


                if "battery" in widget:
                    if widget['battery'].lower() == "true":
                        widget_item = progress_bar

                # if "wifi" in widget:
                elif "wifi" in widget:
                    if widget['wifi'].lower() == 'true':
                        wifi_con = labels.wifi_icon
                        if widget.get("onlineIcon") and widget.get("offlineIcon"):
                            labels.offline_icon = widget["offlineIcon"]
                            labels.online_icon = widget["onlineIcon"]
                            wifi_con = labels.wifi_icon
                        widget_item = wifi_con

                elif "time" in widget:
                    if widget['time'].lower() == 'true':
                        widget_item = labels.time_label

                elif "window title" in widget:
                    if widget['window title'].lower() == 'true':
                        widget_item = get_window

                elif "system info" in widget:
                    if widget['system info'].lower() == 'true':
                        widget_item = labels.sys_info_label

                elif "menu" in widget:
                    if widget['menu'].lower() == 'true':
                        menu_ico = buttons.menu
                        if widget.get("icon"):
                            buttons.custom_menu.setText(widget["icon"])
                            buttons.isEnabled_ = True
                            menu_ico = buttons.custom_menu
                        widget_item = menu_ico

                elif "trash" in widget:
                    if widget['trash'].lower() == 'true':
                        trash_ico = buttons.trash_button_
                        if widget.get("icon"):
                            buttons.custom_trash.setText(widget["icon"])
                            buttons.trash_enabled = True
                            trash_ico = buttons.custom_trash
                        widget_item = trash_ico

                elif "launcher" in widget:
                    if widget['launcher'].lower() == 'true':
                        launcher_ico = buttons.launcher_button_
                        if widget.get("icon"):
                            buttons.custom_launcher.setText(widget["icon"])
                            buttons.launcher_enabled = True
                            launcher_ico = buttons.custom_launcher
                        widget_item = launcher_ico

                elif "type" in widget:
                    if widget["type"] == "label":

                        if 'cputemp' in widget['text']:
                            text = widget['text'].replace('cputemp', Utils.get_cpu_temperature())

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                            def update_cpu_temp_(label = widget_item, template_text = widget['text']):
                                temp = Utils.get_cpu_temperature()
                                new_text = template_text.replace("cputemp", temp)
                                label.setText(new_text)


                            cpu_temp_timer = QTimer()
                            cpu_temp_timer.timeout.connect(update_cpu_temp_)
                            cpu_temp_timer.start(1000)
                            timers.append(cpu_temp_timer)

                            # widget_item = label
                        elif 'cpuUsage' in widget['text']:
                            usage_ = Utils.get_cpu_usage()
                            text = widget['text'].replace('cpuUsage', str(usage_))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                            def update_cpu_usage_(label = widget_item, template_text = widget['text']):
                                usage = Utils.get_cpu_usage()
                                new_text = template_text.replace("cpuUsage", str(usage))
                                label.setText(new_text)


                            cpu_usage_timer = QTimer()
                            cpu_usage_timer.timeout.connect(update_cpu_usage_)
                            cpu_usage_timer.start(1000)
                            timers.append(cpu_usage_timer)

                        elif 'ramusage' in widget['text']:
                            usage_ = Utils.ram_usage()
                            text = widget['text'].replace('ramusage', str(usage_))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                            def update_ram_usage__(label = widget_item, template_text = widget['text']):
                                usage = Utils.ram_usage()
                                new_text = template_text.replace("ramusage", str(usage))
                                label.setText(new_text)


                            ram_usage_timer = QTimer()
                            ram_usage_timer.timeout.connect(update_ram_usage__)
                            ram_usage_timer.start(1000)
                            timers.append(ram_usage_timer)

                        elif 'ramtotalGB' in widget['text']:
                            pass

                        elif 'ramusedGB' in widget['text']:
                            used = Utils.get_used_ram_gb()
                            text = widget['text'].replace('ramusedGB', str(used))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                            def update_ram_used__(label = widget_item, template_text = widget['text']):
                                usage = Utils.get_used_ram_gb()
                                new_text = template_text.replace("ramusedGB", str(usage))
                                label.setText(new_text)


                            ram_used_timer = QTimer()
                            ram_used_timer.timeout.connect(update_ram_used__)
                            ram_used_timer.start(1000)
                            timers.append(ram_used_timer)

                        elif 'nvidiatemp' in widget['text']:
                            temp = Nvidia.get_nvidia_gpu_temperature(None)
                            text = widget['text'].replace('nvidiatemp', str(temp))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                            def update_nvidia_temp__(label = widget_item, template_text = widget['text']):
                                usage = Nvidia.get_nvidia_gpu_temperature(None)
                                new_text = template_text.replace("nvidiatemp", str(usage))
                                label.setText(new_text)

                            nvidia_temp_timer = QTimer()
                            nvidia_temp_timer.timeout.connect(update_nvidia_temp__)
                            nvidia_temp_timer.start(1000)
                            timers.append(nvidia_temp_timer)

                        elif 'nvidiausage' in widget['text']:
                            temp = Nvidia.get_nvidia_gpu_usage(None)
                            text = widget['text'].replace('nvidiausage', str(temp))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                            def update_nvidia_usage__(label = widget_item, template_text = widget['text']):
                                usage = Nvidia.get_nvidia_gpu_usage(None)
                                new_text = template_text.replace("nvidiausage", str(usage))
                                label.setText(new_text)

                            nvidia_usage_timer = QTimer()
                            nvidia_usage_timer.timeout.connect(update_nvidia_usage__)
                            nvidia_usage_timer.start(1000)
                            timers.append(nvidia_usage_timer)

                        elif 'nvidiaTOTVram' in widget['text']:
                            vram = Nvidia.get_nvidia_total_vram()
                            text = widget['text'].replace('nvidiaTOTVram', str(vram))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                        elif 'nvidiaName' in widget['text']:
                            vram = Nvidia.get_nvidia_name()
                            text = widget['text'].replace('nvidiaName', str(vram))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])



                        elif 'nvidiaUSEDVram' in widget['text']:
                            temp = Nvidia.get_nvidia_used_vram()
                            text = widget['text'].replace('nvidiaUSEDVram', str(temp))

                            widget_item = QLabel(text)
                            widget_item.setObjectName(widget["name"])

                            def update_nvidia_vram__(label = widget_item, template_text = widget['text']):
                                usage = Nvidia.get_nvidia_used_vram()
                                new_text = template_text.replace("nvidiaUSEDVram", str(usage))
                                label.setText(new_text)

                            nvidia_used_timer = QTimer()
                            nvidia_used_timer.timeout.connect(update_nvidia_vram__)
                            nvidia_used_timer.start(1000)
                            timers.append(nvidia_used_timer)


                        else:
                            widget_item = QLabel(widget["text"])
                        widget_item.setObjectName(widget["name"])
                        
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

        for widget in widgets['bar widgets']:
            if widget.get('docks') == "true":
                print("showing dock")
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

def load_panel_widgets_from_json(file_path, parent):
    try:
        with open(file_path, "r") as file:
            widgets = json.load(file)

            for widget in widgets['panel widgets']:
                # widget_item = None
            
                if "type" in widget:
                    if widget["type"] == "button":
                        button = QPushButton(parent = parent, text = widget['text'])
                        button.setObjectName(widget['name'])
                        if 'action' in widget:
                            button.clicked.connect(partial(cmd, widget["action"]))
                        button.move(int(widget['x']), int(widget['y']))

                    elif widget['type'] == 'label':
                        label = QLabel(parent = parent, text = widget['text'])
                        label.setObjectName(widget['name'])
                        label.move(int(widget['x']), int(widget['y']))


    except Exception as e:
        print("Error:", e)