import WinTmp
import psutil
import shutil
import os
import glob


class Utils:
    def get_cpu_temperature():
        cpu = WinTmp.CPU_Temp()
        if cpu == 0.0 or cpu is None:
            return "Please make sure you have ran this program as an Administrator"

        return f"{cpu:.2f}°C"

    def get_cpu_freq():
        cpu_freq = psutil.cpu_freq().current
        return cpu_freq

    def get_used_ram_gb():
        ram_info = psutil.virtual_memory()
        used_ram_gb = ram_info.used / (1024 ** 3)
        return used_ram_gb
    
    def get_total_ram_gb():
        ram_info = psutil.virtual_memory()
        ram_total_gb = ram_info.total / (1024 ** 3)
        return ram_total_gb

    def ram_usage():
        ram_info = psutil.virtual_memory()
        ram_usage = ram_info.percent
        return ram_usage

    def get_cpu_usage():
        cpu_usage = psutil.cpu_percent()
        return cpu_usage

    def delete_temp_files():
        username = os.getlogin()
        temp_paths = [r"C:\Windows\Temp\*", fr"C:\Users\{username}\AppData\Local\Temp\*", "C:\Windows\Prefetch\*"]

        for temp_path in temp_paths:
            files = glob.glob(temp_path)

            for file in files:
                try:
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                        print(f"Deleted directory: {file}")
                    else:
                        os.remove(file)
                except PermissionError as e:
                    print(f"Permission error deleting {file}: {e}. Skipping.")
                except OSError as e:
                    print(f"Error deleting {file}: {e}. Skipping.")
