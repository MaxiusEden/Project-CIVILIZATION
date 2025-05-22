from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                           QListWidget, QListWidgetItem, QSplitter, QTextBrowser,
                           QMessageBox)
from PyQt5.QtCore import Qt

class LoadGameDialog(QDialog):
    """Diálogo para carregar um jogo salvo."""
    
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        self.setWindowTitle("Load Game")
        self.selected_save = ""
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        layout = QVBoxLayout()
        
        # Instruções
        layout.addWidget(QLabel("Select a saved game to load:"))
        
        # Splitter para lista e detalhes
        splitter = QSplitter(Qt.Horizontal)
        
        # Lista de salvamentos
        self.saves_list = QListWidget()
        splitter.addWidget(self.saves_list)
        
        # Painel de detalhes
        self.details_browser = QTextBrowser()
        splitter.addWidget(self.details_browser)
        
        # Definir proporções do splitter
        splitter.setSizes([200, 200])
        
        layout.addWidget(splitter)
        
        # Carregar salvamentos existentes
        self.load_existing_saves()
        
        # Conectar seleção da lista à exibição de detalhes
        self.saves_list.itemClicked.connect(self.on_save_selected)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.on_load)
        self.load_button.setEnabled(False)  # Desabilitado até que um salvamento seja selecionado
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setEnabled(False)  # Desabilitado até que um salvamento seja selecionado
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.resize(600, 400)
    
    def load_existing_saves(self):
        """Carrega a lista de salvamentos existentes."""
        self.saves_list.clear()
        saves = self.game_controller.save_manager.list_saves()
        
        if not saves:
            self.details_browser.setText("No saved games found.")
            return
        
        for save in saves:
            item = QListWidgetItem(save['name'])
            item.setData(Qt.UserRole, save['filename'])
            # Armazenar todos os detalhes do salvamento
            item.setData(Qt.UserRole + 1, save)
            self.saves_list.addItem(item)
    
    def on_save_selected(self, item):
        """
        Manipulador para seleção de um salvamento.
        
        Args:
            item: Item selecionado
        """
        self.selected_save = item.data(Qt.UserRole)
        save_details = item.data(Qt.UserRole + 1)
        
        # Habilitar botões
        self.load_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Exibir detalhes
        details_html = f"""
        <h3>{save_details['name']}</h3>
        <p><b>Date:</b> {save_details['timestamp']}</p>
        <p><b>Version:</b> {save_details['version']}</p>
        <p><b>File:</b> {save_details['filename']}</p>
        """
        
        self.details_browser.setHtml(details_html)
    
    def on_load(self):
        """Manipulador para botão de carregar."""
        if self.selected_save:
            self.accept()
    
    def on_delete(self):
        """Manipulador para botão de excluir."""
        if not self.selected_save:
            return
        
        reply = QMessageBox.question(
            self, 'Delete Save',
            f'Are you sure you want to delete "{self.saves_list.currentItem().text()}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Excluir o salvamento
            if self.game_controller.save_manager.delete_save(self.selected_save):
                # Recarregar a lista
                self.load_existing_saves()
                # Limpar seleção
                self.selected_save = ""
                self.load_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.details_browser.setText("Save deleted successfully.")
            else:
                QMessageBox.warning(self, "Delete Save", "Failed to delete the save file.")
    
    def get_selected_save(self):
        """
        Obtém o nome do salvamento selecionado.
        
        Returns:
            str: Nome do arquivo de salvamento
        """
        return self.selected_save