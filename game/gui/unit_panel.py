from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class UnitPanel(QWidget):
    """Panel displaying information about the selected unit."""
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        layout = QVBoxLayout(self)
        self.label = QLabel("Unit Info")
        layout.addWidget(self.label)

    def update_unit(self, unit=None):
        # Atualize as informações do painel conforme necessário
        pass