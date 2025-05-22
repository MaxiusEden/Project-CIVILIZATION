from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    """Diálogo 'Sobre' com informações sobre o jogo."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Project CIVILIZATION")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Project CIVILIZATION")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Versão
        version_label = QLabel("Version 0.1")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Descrição
        description = (
            "Project CIVILIZATION is an open-source strategy game inspired by "
            "the Civilization series. Build an empire to stand the test of time!"
        )
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Créditos
        credits = (
            "Created by: Project CIVILIZATION Team\n"
            "Graphics: OpenGL\n"
            "UI Framework: PyQt5\n"
            "License: MIT"
        )
        credits_label = QLabel(credits)
        credits_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits_label)
        
        # Botão de fechar
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.resize(400, 300)