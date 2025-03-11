from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

class Layouts:
    def __init__(self, position):
        if position == 'left' or position == 'right':
            self.main_layout = QVBoxLayout()
            self.right_layout = QVBoxLayout()
            self.middle_layout = QVBoxLayout()
            self.left_layout = QVBoxLayout()
            
        elif position == 'bottom' or position == 'top':
            self.main_layout = QHBoxLayout()
            self.right_layout = QHBoxLayout()
            self.middle_layout = QHBoxLayout()
            self.left_layout = QHBoxLayout()

        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.middle_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.right_layout)
