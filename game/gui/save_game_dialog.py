from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                           QLineEdit, QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt

class SaveGameDialog(QDialog):
    """Diálogo para salvar um jogo."""
    
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        self.setWindowTitle("Save Game")
        self.save_name = ""
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        
        # Instruções
        layout.addWidget(QLabel("Enter a name for your save or select an existing save to overwrite:"))
        
        # Campo de nome
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Lista de salvamentos existentes
        layout.addWidget(QLabel("Existing Saves:"))
        self.saves_list = QListWidget()
        layout.addWidget(self.saves_list)
        
        # Carregar salvamentos existentes
        self.load_existing_saves()
        
        # Conectar seleção da lista ao campo de nome
        self.saves_list.itemClicked.connect(self.on_save_selected)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.resize(400, 300)
    
    def load_existing_saves(self):
        """Carrega a lista de salvamentos existentes."""
        saves = self.game_controller.save_manager.list_saves()
        for save in saves:
            item = QListWidgetItem(save['name'])
            item.setData(Qt.UserRole, save['filename'])
            self.saves_list.addItem(item)
    
    def on_save_selected(self, item):
        """
        Manipulador para seleção de um salvamento existente.
        
        Args:
            item: Item selecionado
        """
        self.name_edit.setText(item.text())
    
    def on_save(self):
        """Manipulador para botão de salvar."""
        self.save_name = self.name_edit.text().strip()
        if not self.save_name:
            QMessageBox.warning(self, "Save Game", "Please enter a name for your save.")
            return
        
        self.accept()
    
    def get_save_name(self):
        """
        Obtém o nome do salvamento.
        
        Returns:
            str: Nome do salvamento
        """
        return self.save_name