import subprocess
import pynvml


class Nvidia:
    def __init__(self):
        self.handle = None
        self.has_nvidia_gpu = False
        try:
            pynvml.nvmlInit()
            self.num_gpus = pynvml.nvmlDeviceGetCount()
            if self.num_gpus > 0:
                self.has_nvidia_gpu = True
                self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except pynvml.NVMLError:
              print('')
              return 0


        # self.get_used_vram()


    def get_used_vram(self):
            # self.has_nvidia_gpu = self.test_1()
            # try:
            #     pynvml.nvmlInit()
            #     self.num_gpus = pynvml.nvmlDeviceGetCount()
            #     if self.num_gpus > 0:
            #         self.has_nvidia_gpu = True
            #         self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        vram_used = pynvml.nvmlDeviceGetMemoryInfo(self.handle).used
        vram_used_gb = vram_used / (1024 ** 3)
        return f"{vram_used_gb:.2f}GB"
            # except pynvml.NVMLError as e:
            #     print(f"Error initializing pynvml: {e}")
            #     return 0

    def get_nvidia_used_vram():
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits']
    ,
                                    stdout=subprocess.PIPE, text=True)
            used_vram = result.stdout.strip()
            return f"{used_vram}"
        except FileNotFoundError:
            return ''

    def get_nvidia_gpu_usage(self):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                                    stdout=subprocess.PIPE, text=True)
            usage = result.stdout.strip()
            return f"{usage}%"
        except FileNotFoundError:
            return ''


    def get_nvidia_gpu_temperature(self):
        # self.gpu_test = ""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                                    stdout=subprocess.PIPE, text=True)
            temperature = result.stdout.strip()
            return f"{temperature}"
        except FileNotFoundError:
            self.gpu_test = ""
            # return f"{self.gpu_test}"
            return ""


    def get_tot_vram(self):
        if not self.has_nvidia_gpu:
            return "No NVIDIA GPU detected"
        
        try:
            # handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            vram_total = pynvml.nvmlDeviceGetMemoryInfo(self.handle).total
            vram_total_gb = vram_total / (1024 ** 3)
            return f"{vram_total_gb:.2f}GB"
        except pynvml.NVMLError as e:
            print(f"Error getting total VRAM: {e}")
            return 0

    def get_nvidia_total_vram():
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits']
    ,
                                    stdout=subprocess.PIPE, text=True)
            vram = result.stdout.strip()
            return f"{vram:.1}"
        except FileNotFoundError:
            return ''

    def get_nvidia_name():
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits']
    ,
                                    stdout=subprocess.PIPE, text=True)
            name = result.stdout.strip()
            return f"{name}"
        except FileNotFoundError:
            return ''