"""
Janela principal do jogo com arquitetura melhorada.

Esta versão implementa melhorias de design e arquitetura sugeridas,
com maior modularização e desacoplamento de componentes.
"""
from PyQt5.QtWidgets import (QMainWindow, QDockWidget, QAction, QMenuBar, 
                            QStatusBar, QMessageBox, QDialog, QToolBar)
from PyQt5.QtCore import Qt, QSize, pyqtSignal

import config
from typing import Dict, Any, Optional, List, Union

from game.gui.map_view import MapGLWidget
from game.gui.info_panel import InfoPanel
from game.gui.minimap_panel import MinimapPanel
from game.gui.unit_panel import UnitPanel
from game.gui.city_panel import CityPanel
from game.gui.tech_dialog import TechDialog
from game.gui.diplomacy_dialog import DiplomacyDialog
from game.gui.options_dialog import OptionsDialog
from game.gui.about_dialog import AboutDialog
from game.gui.new_game_dialog import NewGameDialog
from game.gui.save_game_dialog import SaveGameDialog
from game.gui.load_game_dialog import LoadGameDialog

# Usar as versões melhoradas dos gerenciadores
from game.gui.gui_factory import GUIFactory
from game.gui.menu_manager import MenuManager
from game.gui.dock_manager import DockManager


class MainWindow(QMainWindow):
    """
    Janela principal do jogo Civilization.
    
    Esta classe representa a janela principal da aplicação, responsável por
    hospedar os componentes visuais e gerenciar as interações do usuário
    com a interface.
    """
    
    # Sinais para comunicação com outros componentes
    game_started = pyqtSignal()
    game_loaded = pyqtSignal(str)
    game_saved = pyqtSignal(str)
    turn_ended = pyqtSignal()
    
    def __init__(self, game_controller):
        """
        Inicializa a janela principal.
        
        Args:
            game_controller: Controlador do jogo
        """
        super().__init__()
        self.game_controller = game_controller
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Estado da janela
        self.is_fullscreen = config.FULLSCREEN
        self.normal_geometry = None
        
        # Configurar componentes da GUI
        self.setup_central_widget()
        self.menu_manager = MenuManager(self, game_controller)
        self.dock_manager = DockManager(self, game_controller)
        
        # Criar barra de ferramentas
        self.setup_toolbar()
        
        # Criar barra de status
        self.setup_status_bar()
        
        # Conectar sinais
        self.connect_signals()
        
        # Aplicar configurações iniciais
        self.apply_initial_settings()
    
    def setup_central_widget(self):
        """Configura o widget central (mapa 3D)."""
        self.map_widget = MapGLWidget(self.game_controller)
        self.setCentralWidget(self.map_widget)
    
    def setup_toolbar(self):
        """Configura a barra de ferramentas principal."""
        self.toolbar = self.menu_manager.create_toolbar()
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
    
    def setup_status_bar(self):
        """Configura a barra de status."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def connect_signals(self):
        """Conecta sinais entre componentes."""
        # Conectar sinais do controlador do jogo
        self.game_controller.turn_changed.connect(self.on_turn_changed)
        self.game_controller.turn_ended.connect(self.on_turn_ended)
        self.game_controller.active_city_changed.connect(self.on_active_city_changed)
        self.game_controller.map_updated.connect(self.on_map_updated)
        self.game_controller.game_started.connect(self.on_game_started)
        self.game_controller.game_loaded.connect(self.on_game_loaded)
        self.game_controller.game_saved.connect(self.on_game_saved)
        
        # Conectar sinais do mapa
        self.map_widget.tile_clicked.connect(self.on_tile_clicked)
    
    def apply_initial_settings(self):
        """Aplica configurações iniciais da interface."""
        # Aplicar modo de tela cheia se configurado
        if self.is_fullscreen:
            self.on_toggle_fullscreen()
    
    # Manipuladores de eventos do jogo
    def on_turn_changed(self):
        """Manipulador para mudança de turno."""
        # Atualizar painéis
        self.dock_manager.update_info_panel()
        self.dock_manager.update_panels()
        
        # Atualizar barra de status
        turn = self.game_controller.get_game_state().current_turn
        self.status_bar.showMessage(f"Turn {turn}")
    
    def on_turn_ended(self):
        """Manipulador para fim de turno."""
        self.turn_ended.emit()
        self.on_turn_changed()
    
    def on_active_city_changed(self):
        """Manipulador para mudança de cidade ativa."""
        self.dock_manager.update_city_panel()
    
    def on_map_updated(self):
        """Manipulador para atualização do mapa."""
        self.map_widget.update_map()
        minimap_panel = self.dock_manager.get_panel('minimap')
        if minimap_panel and hasattr(minimap_panel, 'update_minimap'):
            minimap_panel.update_minimap()
    
    def on_game_started(self):
        """Manipulador para início de jogo."""
        self.game_started.emit()
        self.menu_manager.update_game_actions(True)
        self.dock_manager.update_panels()
        self.status_bar.showMessage("Game started")
    
    def on_game_loaded(self):
        """Manipulador para carregamento de jogo."""
        game_state = self.game_controller.get_game_state()
        self.game_loaded.emit(game_state.id if game_state else "")
        self.menu_manager.update_game_actions(game_state is not None)
        self.dock_manager.update_panels()
        self.status_bar.showMessage("Game loaded")
    
    def on_game_saved(self):
        """Manipulador para salvamento de jogo."""
        game_state = self.game_controller.get_game_state()
        self.game_saved.emit(game_state.id if game_state else "")
        self.status_bar.showMessage("Game saved")
    
    def on_tile_clicked(self, x, y):
        """
        Manipulador para clique em um tile do mapa.
        
        Args:
            x: Coordenada X do tile
            y: Coordenada Y do tile
        """
        # Obter informações do tile
        world = self.game_controller.get_world()
        if not world:
            return
        
        tile = world.get_tile(x, y)
        if not tile:
            return
        
        # Verificar se há unidades no tile
        units = world.get_units_at(x, y)
        if units:
            # Selecionar a primeira unidade
            self.dock_manager.update_unit_panel(units[0])
        
        # Verificar se há cidade no tile
        city = world.get_city_at(x, y)
        if city:
            self.dock_manager.update_city_panel(city)
        
        # Atualizar barra de status
        terrain = tile.terrain_type.capitalize()
        resource = f", {tile.resource.capitalize()}" if tile.resource else ""
        self.status_bar.showMessage(f"Tile ({x}, {y}): {terrain}{resource}")
    
    # Manipuladores de ações do menu
    def on_new_game(self):
        """Manipulador para ação de novo jogo."""
        dialog = NewGameDialog(self.game_controller, self)
        if dialog.exec_() == QDialog.Accepted:
            # Iniciar novo jogo com as configurações selecionadas
            config = dialog.get_game_config()
            self.game_controller.new_game(config)
            self.status_bar.showMessage("Starting new game...")
    
    def on_load_game(self):
        """Manipulador para ação de carregar jogo."""
        dialog = LoadGameDialog(self.game_controller, self)
        if dialog.exec_() == QDialog.Accepted:
            # Carregar o jogo selecionado
            save_name = dialog.get_selected_save()
            if save_name:
                self.game_controller.load_game(save_name)
                self.status_bar.showMessage(f"Loading game: {save_name}")
    
    def on_save_game(self):
        """Manipulador para ação de salvar jogo."""
        # Verificar se há um jogo em andamento
        game_state = self.game_controller.get_game_state()
        if not game_state:
            GUIFactory.create_message_box(
                self, "Save Game", "No game in progress to save.",
                QMessageBox.Warning
            )
            return
        
        # Se o jogo já foi salvo, usar o mesmo nome
        if hasattr(game_state, 'save_name') and game_state.save_name:
            self.game_controller.save_game(game_state.save_name)
            self.status_bar.showMessage(f"Game saved as: {game_state.save_name}")
        else:
            # Se não, usar "Salvar como..."
            self.on_save_game_as()
    
    def on_save_game_as(self):
        """Manipulador para ação de salvar jogo como."""
        # Verificar se há um jogo em andamento
        if not self.game_controller.get_game_state():
            GUIFactory.create_message_box(
                self, "Save Game", "No game in progress to save.",
                QMessageBox.Warning
            )
            return
        
        dialog = SaveGameDialog(self.game_controller, self)
        if dialog.exec_() == QDialog.Accepted:
            # Salvar o jogo com o nome especificado
            save_name = dialog.get_save_name()
            if save_name:
                self.game_controller.save_game(save_name)
                # Armazenar o nome do salvamento no estado do jogo
                self.game_controller.get_game_state().save_name = save_name
                self.status_bar.showMessage(f"Game saved as: {save_name}")
    
    def on_options(self):
        """Manipulador para ação de opções."""
        dialog = OptionsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Aplicar novas configurações
            self.apply_settings(dialog.get_settings())
            self.status_bar.showMessage("Settings updated")
    
    def on_toggle_minimap(self):
        """Manipulador para ação de alternar minimapa."""
        visible = self.dock_manager.toggle_dock('minimap')
        self.menu_manager.get_action('toggle_minimap').setChecked(visible)
        self.status_bar.showMessage(f"Minimap {'shown' if visible else 'hidden'}")
    
    def on_toggle_panel(self, panel_name):
        """
        Manipulador para ação de alternar a visibilidade de um painel.
        
        Args:
            panel_name: Nome do painel
        """
        visible = self.dock_manager.toggle_dock(panel_name)
        action_name = f'toggle_{panel_name}'
        if action_name in self.menu_manager.actions:
            self.menu_manager.get_action(action_name).setChecked(visible)
        self.status_bar.showMessage(f"{panel_name.capitalize()} panel {'shown' if visible else 'hidden'}")
    
    def on_restore_layout(self):
        """Manipulador para ação de restaurar layout padrão."""
        self.dock_manager.restore_default_layout()
        self.status_bar.showMessage("Default layout restored")
    
    def on_toggle_grid(self):
        """Manipulador para ação de alternar grade."""
        self.map_widget.toggle_grid()
        self.status_bar.showMessage(f"Grid {'shown' if self.map_widget.show_grid else 'hidden'}")
    
    def on_toggle_resources(self):
        """Manipulador para ação de alternar recursos."""
        self.map_widget.show_resources = not self.map_widget.show_resources
        self.map_widget.update()
        self.status_bar.showMessage(f"Resources {'shown' if self.map_widget.show_resources else 'hidden'}")
    
    def on_toggle_improvements(self):
        """Manipulador para ação de alternar melhorias."""
        self.map_widget.show_improvements = not self.map_widget.show_improvements
        self.map_widget.update()
        self.status_bar.showMessage(f"Improvements {'shown' if self.map_widget.show_improvements else 'hidden'}")
    
    def on_toggle_units(self):
        """Manipulador para ação de alternar unidades no mapa."""
        self.map_widget.show_units = not self.map_widget.show_units
        self.map_widget.update()
        self.status_bar.showMessage(f"Units {'shown' if self.map_widget.show_units else 'hidden'}")
    
    def on_set_render_quality(self, quality):
        """
        Manipulador para ação de definir qualidade de renderização.
        
        Args:
            quality: Nível de qualidade ("Low", "Medium", "High")
        """
        if hasattr(self.map_widget, 'set_render_quality'):
            self.map_widget.set_render_quality(quality)
            self.status_bar.showMessage(f"Render quality set to {quality}")
    
    def on_toggle_fullscreen(self):
        """Manipulador para ação de alternar tela cheia."""
        if not self.is_fullscreen:
            # Salvar geometria atual e entrar em tela cheia
            self.normal_geometry = self.geometry()
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            # Restaurar geometria normal
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_fullscreen = False
        
        # Atualizar estado da ação
        self.menu_manager.get_action('fullscreen').setChecked(self.is_fullscreen)
    
    def on_tech_tree(self):
        """Manipulador para ação de árvore tecnológica."""
        dialog = TechDialog(self.game_controller, self)
        dialog.exec_()
    
    def on_diplomacy(self):
        """Manipulador para ação de diplomacia."""
        dialog = DiplomacyDialog(self.game_controller, self)
        dialog.exec_()
    
    def on_economy(self):
        """Manipulador para ação de economia."""
        # Implementação futura
        self.status_bar.showMessage("Economy view not implemented yet")
    
    def on_military(self):
        """Manipulador para ação de militar."""
        # Implementação futura
        self.status_bar.showMessage("Military view not implemented yet")
    
    def on_end_turn(self):
        """Manipulador para ação de finalizar turno."""
        self.game_controller.end_turn()
        self.status_bar.showMessage("Turn ended")
    
    def on_manual(self):
        """Manipulador para ação de manual do jogo."""
        # Implementação futura - abrir manual em HTML ou PDF
        self.status_bar.showMessage("Game manual not implemented yet")
    
    def on_about(self):
        """Manipulador para ação de sobre."""
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def apply_settings(self, settings: Dict[str, Any]):
        """
        Aplica configurações da interface.
        
        Args:
            settings: Dicionário com as configurações
        """
        # Aplicar configurações de exibição
        if 'fullscreen' in settings and settings['fullscreen'] != self.is_fullscreen:
            self.on_toggle_fullscreen()
        
        # Aplicar configurações de renderização
        if 'show_grid' in settings:
            self.map_widget.show_grid = settings['show_grid']
            self.menu_manager.get_action('toggle_grid').setChecked(settings['show_grid'])
        
        if 'show_resources' in settings:
            self.map_widget.show_resources = settings['show_resources']
            self.menu_manager.get_action('toggle_resources').setChecked(settings['show_resources'])
        
        if 'show_improvements' in settings:
            self.map_widget.show_improvements = settings['show_improvements']
            self.menu_manager.get_action('toggle_improvements').setChecked(settings['show_improvements'])
        
        if 'render_quality' in settings and hasattr(self.map_widget, 'set_render_quality'):
            self.map_widget.set_render_quality(settings['render_quality'])
            quality_action = self.menu_manager.get_action(f"render_{settings['render_quality'].lower()}")
            if quality_action:
                quality_action.setChecked(True)
        
        # Atualizar o mapa com as novas configurações
        self.map_widget.update()
    
    def closeEvent(self, event):
        """
        Manipulador para evento de fechamento da janela.
        
        Args:
            event: Evento de fechamento
        """
        # Verificar se há um jogo em andamento e não salvo
        game_state = self.game_controller.get_game_state()
        if game_state and not hasattr(game_state, 'save_name'):
            reply = GUIFactory.create_message_box(
                self, 'Exit Game',
                'The current game is not saved. Do you want to save before exiting?',
                QMessageBox.Question,
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.on_save_game()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def keyPressEvent(self, event):
        """
        Manipulador para eventos de tecla pressionada.
        
        Args:
            event: Evento de tecla
        """
        # Delegar para o widget do mapa se estiver focado
        if self.centralWidget().hasFocus():
            self.centralWidget().keyPressEvent(event)
        else:
            super().keyPressEvent(event)