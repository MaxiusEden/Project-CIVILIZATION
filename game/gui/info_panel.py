from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont, QIcon


class InfoPanel(QWidget):
    """Panel displaying general game information and controls."""
    
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        self.setup_ui()
        self.update_info()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Turn information
        turn_layout = QVBoxLayout()
        
        self.turn_label = QLabel("Turn: 1")
        self.turn_label.setFont(QFont("Arial", 12, QFont.Bold))
        turn_layout.addWidget(self.turn_label)
        
        self.year_label = QLabel("4000 BC")
        self.year_label.setFont(QFont("Arial", 10))
        turn_layout.addWidget(self.year_label)
        
        main_layout.addLayout(turn_layout)
        
        # Current civilization information
        civ_layout = QVBoxLayout()
        
        self.civ_label = QLabel("Civilization: Rome")
        self.civ_label.setFont(QFont("Arial", 12, QFont.Bold))
        civ_layout.addWidget(self.civ_label)
        
        self.leader_label = QLabel("Leader: Caesar")
        self.leader_label.setFont(QFont("Arial", 10))
        civ_layout.addWidget(self.leader_label)
        
        main_layout.addLayout(civ_layout)
        
        # Resources
        resources_layout = QVBoxLayout()
        
        self.gold_label = QLabel("Gold: 100")
        self.gold_label.setFont(QFont("Arial", 10))
        resources_layout.addWidget(self.gold_label)
        
        self.science_label = QLabel("Science: 5 per turn")
        self.science_label.setFont(QFont("Arial", 10))
        resources_layout.addWidget(self.science_label)
        
        main_layout.addLayout(resources_layout)
        
        # Current research
        research_layout = QVBoxLayout()
        
        self.research_label = QLabel("Researching:")
        self.research_label.setFont(QFont("Arial", 10))
        research_layout.addWidget(self.research_label)
        
        self.tech_label = QLabel("Agriculture (5 turns)")
        self.tech_label.setFont(QFont("Arial", 10, QFont.Bold))
        research_layout.addWidget(self.tech_label)
        
        main_layout.addLayout(research_layout)
        
        # Spacer to push buttons to the right
        main_layout.addStretch(1)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.tech_button = QPushButton("Technology")
        self.tech_button.clicked.connect(self.on_tech_clicked)
        buttons_layout.addWidget(self.tech_button)
        
        self.diplomacy_button = QPushButton("Diplomacy")
        self.diplomacy_button.clicked.connect(self.on_diplomacy_clicked)
        buttons_layout.addWidget(self.diplomacy_button)
        
        self.end_turn_button = QPushButton("End Turn")
        self.end_turn_button.clicked.connect(self.on_end_turn_clicked)
        self.end_turn_button.setFont(QFont("Arial", 10, QFont.Bold))
        buttons_layout.addWidget(self.end_turn_button)
        
        main_layout.addLayout(buttons_layout)
    
    def update_info(self):
        """Update all information displayed in the panel."""
        # Get current game state
        game_state = self.game_controller.get_game_state()
        if not game_state:
            return
        
        # Update turn information
        self.turn_label.setText(f"Turn: {game_state.turn}")
        self.year_label.setText(self.get_year_string(game_state.turn))
        
        # Update civilization information
        current_civ = self.game_controller.get_current_civilization()
        if current_civ:
            self.civ_label.setText(f"Civilization: {current_civ.name}")
            self.leader_label.setText(f"Leader: {current_civ.leader}")
            
            # Update resources
            self.gold_label.setText(f"Gold: {current_civ.gold}")
            self.science_label.setText(f"Science: {current_civ.science_per_turn} per turn")
            
            # Update research
            current_research = current_civ.current_research
            if current_research:
                self.research_label.setText("Researching:")
                turns_left = current_civ.get_turns_to_complete_research()
                self.tech_label.setText(f"{current_research.name} ({turns_left} turns)")
            else:
                self.research_label.setText("Not researching")
                self.tech_label.setText("Choose technology")
    
    def get_year_string(self, turn):
        """Convert turn number to year string (BC/AD)."""
        # Simple conversion: each turn is 25 years, starting at 4000 BC
        year = 4000 - (turn - 1) * 25
        
        if year <= 0:
            # Convert to AD
            return f"{abs(year) + 1} AD"
        else:
            return f"{year} BC"
    
    @pyqtSlot()
    def update_turn(self):
        """Update the turn information."""
        self.update_info()
    
    @pyqtSlot()
    def on_tech_clicked(self):
        """Handle technology button click."""
        # Open technology tree dialog
        from game.gui.tech_dialog import TechDialog
        dialog = TechDialog(self.game_controller, self.window())
        dialog.exec_()
        self.update_info()
    
    @pyqtSlot()
    def on_diplomacy_clicked(self):
        """Handle diplomacy button click."""
        # Open diplomacy dialog
        from game.gui.diplomacy_dialog import DiplomacyDialog
        dialog = DiplomacyDialog(self.game_controller, self.window())
        dialog.exec_()
        self.update_info()
    
    @pyqtSlot()
    def on_end_turn_clicked(self):
        """Handle end turn button click."""
        self.game_controller.end_turn()
        self.update_info()
