from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class DiplomacyDialog(QDialog):
    """Dialog for managing diplomacy."""
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diplomacy")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Diplomacy (em construção)"))