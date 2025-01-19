import subprocess

class Mods:
    def __init__(self):
        pass

    def ultimate_mod(self):
        subprocess.run(["powercfg", "/setactive", "044f5d09-046b-40b4-ad74-0e7ab465d05c"], check=True)
        self.print_active_scheme()

    def high_mod(self):
        subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], check=True)
        self.print_active_scheme()

    def balanced_mod(self):
        subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], check=True)
        self.print_active_scheme()

    def low_mod(self):
        subprocess.run(["powercfg", "/setactive", "a1841308-3541-4fab-bc81-f71556f20b4a"], check=True)
        self.print_active_scheme()

    def print_active_scheme(self):
        """Print the current active power scheme for debugging."""
        result = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
        print("Current Active Power Scheme:")
        print(result.stdout)
