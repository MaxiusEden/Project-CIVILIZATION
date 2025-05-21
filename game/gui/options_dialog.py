from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class OptionsDialog(QDialog):
    """Dialog for game options/settings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Options (em construção)"))