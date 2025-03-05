from PyQt5.QtWidgets import QHBoxLayout

class Layouts:
    def __init__(self):
        self.main_layout = QHBoxLayout()
        self.right_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.left_layout = QHBoxLayout()

        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.middle_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.right_layout)