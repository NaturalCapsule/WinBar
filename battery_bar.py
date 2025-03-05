from PyQt5.QtWidgets import QProgressBar


class Battery(QProgressBar):
    def __init__(self, css):
        super().__init__()
        self.setMaximum(100)
        self.setMinimum(0)
        self.setFixedSize(40, 18)
        self.setObjectName("Battery")
        self.setStyleSheet(css)
        # self.progress_bar.setValue()
        # return self.progress_bar