from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class CityPanel(QWidget):
    """Panel displaying information about the selected city."""
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        layout = QVBoxLayout(self)
        self.label = QLabel("City Info")
        layout.addWidget(self.label)

    def update_city(self, city=None):
        # Atualize as informações do painel conforme necessário
        pass