from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                           QComboBox, QGroupBox, QGridLayout, QCheckBox)
from PyQt5.QtCore import Qt

class NewGameDialog(QDialog):
    """Diálogo para configurar um novo jogo."""
    
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        self.setWindowTitle("New Game")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        
        # Grupo de configurações do mapa
        map_group = QGroupBox("Map Settings")
        map_layout = QGridLayout()
        
        # Tipo de mapa
        map_layout.addWidget(QLabel("Map Type:"), 0, 0)
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItems(["Continents", "Pangaea", "Archipelago", "Inland Sea", "Fractal"])
        map_layout.addWidget(self.map_type_combo, 0, 1)
        
        # Tamanho do mapa
        map_layout.addWidget(QLabel("Map Size:"), 1, 0)
        self.map_size_combo = QComboBox()
        self.map_size_combo.addItems(["Duel", "Tiny", "Small", "Standard", "Large", "Huge"])
        self.map_size_combo.setCurrentText("Standard")
        map_layout.addWidget(self.map_size_combo, 1, 1)
        
        map_group.setLayout(map_layout)
        layout.addWidget(map_group)
        
        # Grupo de configurações do jogo
        game_group = QGroupBox("Game Settings")
        game_layout = QGridLayout()
        
        # Dificuldade
        game_layout.addWidget(QLabel("Difficulty:"), 0, 0)
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Settler", "Chieftain", "Warlord", "Prince", "King", "Emperor", "Immortal", "Deity"])
        self.difficulty_combo.setCurrentText("Prince")
        game_layout.addWidget(self.difficulty_combo, 0, 1)
        
        # Velocidade do jogo
        game_layout.addWidget(QLabel("Game Speed:"), 1, 0)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Quick", "Standard", "Epic", "Marathon"])
        self.speed_combo.setCurrentText("Standard")
        game_layout.addWidget(self.speed_combo, 1, 1)
        
        # Número de civilizações
        game_layout.addWidget(QLabel("Number of Civilizations:"), 2, 0)
        self.num_civs_combo = QComboBox()
        self.num_civs_combo.addItems([str(i) for i in range(2, 13)])
        self.num_civs_combo.setCurrentText("8")
        game_layout.addWidget(self.num_civs_combo, 2, 1)
        
        game_group.setLayout(game_layout)
        layout.addWidget(game_group)
        
        # Grupo de condições de vitória
        victory_group = QGroupBox("Victory Conditions")
        victory_layout = QVBoxLayout()
        
        self.domination_check = QCheckBox("Domination")
        self.domination_check.setChecked(True)
        victory_layout.addWidget(self.domination_check)
        
        self.cultural_check = QCheckBox("Cultural")
        self.cultural_check.setChecked(True)
        victory_layout.addWidget(self.cultural_check)
        
        self.scientific_check = QCheckBox("Scientific")
        self.scientific_check.setChecked(True)
        victory_layout.addWidget(self.scientific_check)
        
        self.diplomatic_check = QCheckBox("Diplomatic")
        self.diplomatic_check.setChecked(True)
        victory_layout.addWidget(self.diplomatic_check)
        
        self.time_check = QCheckBox("Time (Score)")
        self.time_check.setChecked(True)
        victory_layout.addWidget(self.time_check)
        
        victory_group.setLayout(victory_layout)
        layout.addWidget(victory_group)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.resize(500, 400)
    
    def get_game_config(self):
        """
        Obtém a configuração do jogo a partir das seleções do usuário.
        
        Returns:
            dict: Configuração do jogo
        """
        # Mapear nomes de exibição para valores internos
        map_type_map = {
            "Continents": "continents",
            "Pangaea": "pangaea",
            "Archipelago": "archipelago",
            "Inland Sea": "inland_sea",
            "Fractal": "fractal"
        }
        
        map_size_map = {
            "Duel": "duel",
            "Tiny": "tiny",
            "Small": "small",
            "Standard": "standard",
            "Large": "large",
            "Huge": "huge"
        }
        
        difficulty_map = {
            "Settler": "settler",
            "Chieftain": "chieftain",
            "Warlord": "warlord",
            "Prince": "prince",
            "King": "king",
            "Emperor": "emperor",
            "Immortal": "immortal",
            "Deity": "deity"
        }
        
        speed_map = {
            "Quick": "quick",
            "Standard": "standard",
            "Epic": "epic",
            "Marathon": "marathon"
        }
        
        # Construir configuração
        config = {
            "world_type": map_type_map[self.map_type_combo.currentText()],
            "world_size": map_size_map[self.map_size_combo.currentText()],
            "difficulty": difficulty_map[self.difficulty_combo.currentText()],
            "game_speed": speed_map[self.speed_combo.currentText()],
            "num_civs": int(self.num_civs_combo.currentText()),
            "victory_conditions": {
                "domination": self.domination_check.isChecked(),
                "cultural": self.cultural_check.isChecked(),
                "scientific": self.scientific_check.isChecked(),
                "diplomatic": self.diplomatic_check.isChecked(),
                "time": self.time_check.isChecked()
            }
        }
        
        return config