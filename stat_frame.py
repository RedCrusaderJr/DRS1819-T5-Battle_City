from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

class StatFrame(QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.label = QLabel("My text")

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)