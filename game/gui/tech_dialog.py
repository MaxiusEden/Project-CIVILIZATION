from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class TechDialog(QDialog):
    """Dialog for displaying the technology tree."""
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Technology Tree")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Technology Tree (em construção)"))