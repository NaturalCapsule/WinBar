from utils import Utils
from nvidia import Nvidia
from wifi import ConnectedToWifi
import psutil
from datetime import date
import time
from PyQt5.QtWidgets import QToolTip
import keyboard


cpu_tooltip = ''
gpu_tooltip = ''
ram_tooltip = ''


def update_cpu_temp():
    cpu_temp = Utils.get_cpu_temperature()
    return cpu_temp

def update_cpu_usage():
    cpu_usage = Utils.get_cpu_usage()
    # labels.cpu_usage_label.setText(str(cpu_usage))
    return cpu_usage

def update_ram_usage():
    ram_usage = Utils.ram_usage()
    # labels.ram_usage_label.setText(str(ram_usage))
    return ram_usage

def update_ram_totalGB():
    ram_tot_gb = Utils.get_total_ram_gb()
    # labels.ram_usedtotalgb_label.setText(f"{ram_tot_gb:.2f}")
    return f"{ram_tot_gb:.2f}"

def update_ram_usedGB():
    ram_used = Utils.get_used_ram_gb()
    # labels.ram_usedgb_label.setText(f"{ram_used:.2f}")
    return f"{ram_used:.2f}"

def update_nvidia_temp():
    nvidia_temp = Nvidia.get_nvidia_gpu_temperature()
    # labels.nvidia_temp_label.setText(f"{nvidia_temp}°C")
    return str(nvidia_temp)

def update_nvidia_usedVram():
    nvidia_vram = Nvidia.get_used_vram()
    # labels.nvidia_usedvram_label.setText(nvidia_vram)
    return nvidia_vram

def update_nvidia_usage():
    nvidia_usage = Nvidia.get_nvidia_gpu_usage()
    # labels.nvidia_usage_label.setText(nvidia_usage)
    return nvidia_usage

def update_nvidia_totVram():
    nvidia_totVram = Nvidia.get_tot_vram()
    # labels.nvidia_totvram_label.setText(nvidia_totVram)
    return nvidia_totVram


def updateWifiLabel(labels):
    is_connected = ConnectedToWifi.is_wifi_connected()
    show_ssid = ConnectedToWifi.get_connected_wifi_ssid()

    if is_connected:
        labels.wifi_icon.load('svgs/wifi_on.svg')
        labels.wifi_ico.setText(labels.online_icon)
        labels.wifi_icon.setToolTip(f"Connected to {show_ssid}")
    else:
        labels.wifi_icon.load('svgs/wifi_off.svg')
        labels.wifi_ico.setText(labels.offline_icon)
        labels.wifi_icon.setToolTip("No Wi-Fi connection")

def updateSystemInfo(labels, position):
    cpu_usage = Utils.get_cpu_usage()
    cpu_temp = Utils.get_cpu_temperature()
    cpu_freq = Utils.get_cpu_freq()

    # test_code = Nvidia()
    # gpu__ = test_code.has_nvidia_gpu

    gpu_usage = Nvidia().get_nvidia_gpu_usage()
    gpu_temp = Nvidia().get_nvidia_gpu_temperature()
    used_vram = Nvidia().get_used_vram()
    tot_vram = Nvidia().get_tot_vram()

    ram_usage = Utils.ram_usage()
    ram_used_gb = Utils.get_used_ram_gb()
    ram_total_gb = Utils.get_total_ram_gb()

    global gpu_tooltip, cpu_tooltip, ram_tooltip
    cpu_tooltip = f"CPU Frequency: {cpu_freq:.2f} MHz\nCPU Usage: {cpu_usage}%\nCPU Temp: {cpu_temp}"
    ram_tooltip = f"RAM Used: {ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB\nRAM Usage: {ram_usage}%"
    gpu_text = "| GPU: "
    if Nvidia().has_nvidia_gpu == False:
        gpu_tooltip = ""
        gpu_usage = ""
        gpu_text = ""
    gpu_tooltip = f"GPU Temperature: {gpu_temp}°C\nGPU Usage: {gpu_usage}\nGPU VRAM Used: {used_vram} GB / {tot_vram} GB"

    if position == 'right' or position == 'left':
        labels.sys_info_label.setText("Sys Info")
    else:
        labels.sys_info_label.setText(f"CPU: {cpu_usage}% | RAM: {ram_usage}% {gpu_text}{gpu_usage}")

def updateBattery(progress_bar):
    try:
        battery = psutil.sensors_battery()[0]
        battery_plugged = psutil.sensors_battery()[2]

    except (IndexError, TypeError):
        battery = -1
        battery_plugged = ''

    if battery is None:
        battery = -1

    progress_bar.setValue(battery)


    if battery_plugged:
        progress_bar.setToolTip(f"Plugged")
    else:
        progress_bar.setToolTip(f"Not Plugged")


def updateTime(labels, display_date_layout, display_time_layout):
    today = date.today()
    today = today.strftime(display_date_layout)
    current_time = time.strftime(display_time_layout)
    labels.time_label.setText(f"{current_time}{today}")

def updateTooltip(labels, pos):
    updateSystemInfo(labels, pos)
    QToolTip.showText(labels.sys_info_label.mapToGlobal(labels.sys_info_label.rect().center()),
                        f"{cpu_tooltip}\n\n{ram_tooltip}\n\n{gpu_tooltip}",
                        labels.sys_info_label)



# def update_media_label(title, media_label):
#     media_label.setText(title)
#     media_label.adjustSize()
#     media_label.repaint()

# def update_media(MediaWorker):
#     worker = MediaWorker()
#     worker.media_signal.connect(update_media_label)
#     worker.start()

def update_date(get_calendar_html, date_label):
    date = get_calendar_html()
    date_label.setText(date)

def update_weather(Weather, temp_label, sky_label):
    weather = Weather()
    temp_label.setText(weather.get_temp())
    sky_label.setText(weather.get_sky())
    
def check_keys(toggle_side_panel):
    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('y'):
        toggle_side_panel()