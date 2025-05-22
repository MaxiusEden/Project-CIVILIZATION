from PyQt5.QtWidgets import (QMainWindow, QDockWidget, QAction, QMenuBar, 
                            QStatusBar, QFileDialog, QMessageBox, QDialog, 
                            QLineEdit, QListWidget, QListWidgetItem, QSplitter, QTextBrowser)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
import config

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
from game.utils.i18n import I18n


class GUIFactory:
    """
    Factory para criar componentes da GUI.
    Implementa o padrão Factory para desacoplar a criação de componentes.
    """
    
    @staticmethod
    def create_dock_widget(title, widget, parent, area=Qt.RightDockWidgetArea):
        """
        Cria um widget de dock com configurações padrão.
        
        Args:
            title: Título do dock
            widget: Widget a ser colocado no dock
            parent: Widget pai
            area: Área permitida para o dock
            
        Returns:
            QDockWidget: O dock widget criado
        """
        dock = QDockWidget(title, parent)
        dock.setWidget(widget)
        dock.setAllowedAreas(area)
        return dock
    
    @staticmethod
    def create_action(parent, text, slot=None, shortcut=None, icon=None, 
                     tip=None, checkable=False, checked=False):
        """
        Cria uma ação para menus ou barras de ferramentas.
        
        Args:
            parent: Widget pai
            text: Texto da ação
            slot: Função a ser chamada quando a ação for acionada
            shortcut: Atalho de teclado
            icon: Ícone da ação
            tip: Texto de dica
            checkable: Se a ação pode ser marcada
            checked: Estado inicial da ação
            
        Returns:
            QAction: A ação criada
        """
        action = QAction(text, parent)
        
        if icon:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(shortcut)
        if tip:
            action.setStatusTip(tip)
            action.setToolTip(tip)
        if slot:
            action.triggered.connect(slot)
        
        action.setCheckable(checkable)
        if checkable:
            action.setChecked(checked)
            
        return action
    
    @staticmethod
    def create_dialog(dialog_class, game_controller, parent=None, *args, **kwargs):
        """
        Cria e exibe um diálogo.
        
        Args:
            dialog_class: Classe do diálogo a ser criado
            game_controller: Controlador do jogo
            parent: Widget pai
            *args, **kwargs: Argumentos adicionais para o diálogo
            
        Returns:
            O resultado da execução do diálogo
        """
        dialog = dialog_class(game_controller, parent, *args, **kwargs)
        return dialog.exec_()


class MainWindowMenuManager:
    """
    Gerencia os menus da janela principal.
    Responsável por criar e gerenciar os menus da aplicação.
    """
    
    def __init__(self, main_window, game_controller):
        """
        Inicializa o gerenciador de menus.
        
        Args:
            main_window: Referência à janela principal
            game_controller: Controlador do jogo
        """
        self.main_window = main_window
        self.game_controller = game_controller
        self.actions = {}
        
        # Criar menus
        self.setup_game_menu()
        self.setup_view_menu()
        self.setup_civilization_menu()
        self.setup_help_menu()
    
    def setup_game_menu(self):
        """Configura o menu Game."""
        game_menu = self.main_window.menuBar().addMenu("Game")
        
        # New Game
        self.actions['new_game'] = GUIFactory.create_action(
            self.main_window, "New Game", 
            self.main_window.on_new_game,
            shortcut="Ctrl+N",
            tip="Start a new game"
        )
        game_menu.addAction(self.actions['new_game'])
        
        # Load Game
        self.actions['load_game'] = GUIFactory.create_action(
            self.main_window, "Load Game", 
            self.main_window.on_load_game,
            shortcut="Ctrl+L",
            tip="Load a saved game"
        )
        game_menu.addAction(self.actions['load_game'])
        
        # Save Game
        self.actions['save_game'] = GUIFactory.create_action(
            self.main_window, "Save Game", 
            self.main_window.on_save_game,
            shortcut="Ctrl+S",
            tip="Save the current game"
        )
        game_menu.addAction(self.actions['save_game'])
        
        # Save Game As
        self.actions['save_game_as'] = GUIFactory.create_action(
            self.main_window, "Save Game As...", 
            self.main_window.on_save_game_as,
            shortcut="Ctrl+Shift+S",
            tip="Save the current game with a new name"
        )
        game_menu.addAction(self.actions['save_game_as'])
        
        game_menu.addSeparator()
        
        # Options
        self.actions['options'] = GUIFactory.create_action(
            self.main_window, "Options", 
            self.main_window.on_options,
            tip="Configure game options"
        )
        game_menu.addAction(self.actions['options'])
        
        game_menu.addSeparator()
        
        # Exit
        self.actions['exit'] = GUIFactory.create_action(
            self.main_window, "Exit", 
            self.main_window.close,
            shortcut="Alt+F4",
            tip="Exit the application"
        )
        game_menu.addAction(self.actions['exit'])
    
    def setup_view_menu(self):
        """Configura o menu View."""
        view_menu = self.main_window.menuBar().addMenu("View")
        
        # Toggle Minimap
        self.actions['toggle_minimap'] = GUIFactory.create_action(
            self.main_window, "Toggle Minimap", 
            self.main_window.on_toggle_minimap,
            shortcut="M",
            tip="Show or hide the minimap",
            checkable=True,
            checked=True
        )
        view_menu.addAction(self.actions['toggle_minimap'])
        
        # Toggle Grid
        self.actions['toggle_grid'] = GUIFactory.create_action(
            self.main_window, "Toggle Grid", 
            self.main_window.on_toggle_grid,
            shortcut="G",
            tip="Show or hide the grid",
            checkable=True,
            checked=True
        )
        view_menu.addAction(self.actions['toggle_grid'])
        
        # Toggle Resources
        self.actions['toggle_resources'] = GUIFactory.create_action(
            self.main_window, "Toggle Resources", 
            self.main_window.on_toggle_resources,
            shortcut="R",
            tip="Show or hide resources",
            checkable=True,
            checked=True
        )
        view_menu.addAction(self.actions['toggle_resources'])
        
        # Toggle Improvements
        self.actions['toggle_improvements'] = GUIFactory.create_action(
            self.main_window, "Toggle Improvements", 
            self.main_window.on_toggle_improvements,
            shortcut="I",
            tip="Show or hide tile improvements",
            checkable=True,
            checked=True
        )
        view_menu.addAction(self.actions['toggle_improvements'])
        
        view_menu.addSeparator()
        
        # Fullscreen
        self.actions['fullscreen'] = GUIFactory.create_action(
            self.main_window, "Fullscreen", 
            self.main_window.on_toggle_fullscreen,
            shortcut="F11",
            tip="Toggle fullscreen mode",
            checkable=True,
            checked=config.FULLSCREEN
        )
        view_menu.addAction(self.actions['fullscreen'])
    
    def setup_civilization_menu(self):
        """Configura o menu Civilization."""
        civ_menu = self.main_window.menuBar().addMenu("Civilization")
        
        # Technology Tree
        self.actions['tech_tree'] = GUIFactory.create_action(
            self.main_window, "Technology Tree", 
            self.main_window.on_tech_tree,
            shortcut="T",
            tip="View the technology tree"
        )
        civ_menu.addAction(self.actions['tech_tree'])
        
        # Diplomacy
        self.actions['diplomacy'] = GUIFactory.create_action(
            self.main_window, "Diplomacy", 
            self.main_window.on_diplomacy,
            shortcut="D",
            tip="Manage diplomatic relations"
        )
        civ_menu.addAction(self.actions['diplomacy'])
        
        # Economy
        self.actions['economy'] = GUIFactory.create_action(
            self.main_window, "Economy", 
            self.main_window.on_economy,
            shortcut="E",
            tip="View economic information"
        )
        civ_menu.addAction(self.actions['economy'])
        
        # Military
        self.actions['military'] = GUIFactory.create_action(
            self.main_window, "Military", 
            self.main_window.on_military,
            shortcut="Shift+M",
            tip="View military information"
        )
        civ_menu.addAction(self.actions['military'])
        
        # End Turn
        civ_menu.addSeparator()
        self.actions['end_turn'] = GUIFactory.create_action(
            self.main_window, "End Turn", 
            self.main_window.on_end_turn,
            shortcut="Enter",
            tip="End the current turn"
        )
        civ_menu.addAction(self.actions['end_turn'])
    
    def setup_help_menu(self):
        """Configura o menu Help."""
        help_menu = self.main_window.menuBar().addMenu("Help")
        
        # Game Manual
        self.actions['manual'] = GUIFactory.create_action(
            self.main_window, "Game Manual", 
            self.main_window.on_manual,
            shortcut="F1",
            tip="View the game manual"
        )
        help_menu.addAction(self.actions['manual'])
        
        # About
        self.actions['about'] = GUIFactory.create_action(
            self.main_window, "About", 
            self.main_window.on_about,
            tip="About this game"
        )
        help_menu.addAction(self.actions['about'])
    
    def get_action(self, action_name):
        """
        Obtém uma ação pelo nome.
        
        Args:
            action_name: Nome da ação
            
        Returns:
            QAction: A ação correspondente ou None se não encontrada
        """
        return self.actions.get(action_name)
    
    def update_actions(self):
        """Atualiza o estado das ações com base no estado do jogo."""
        game_state = self.game_controller.get_game_state()
        
        # Ações que dependem de um jogo em andamento
        game_running = game_state is not None
        self.actions['save_game'].setEnabled(game_running)
        self.actions['save_game_as'].setEnabled(game_running)
        self.actions['end_turn'].setEnabled(game_running)
        
        # Ações que dependem de um jogo em andamento e uma civilização ativa
        player_civ = self.game_controller.get_current_civilization() if game_running else None
        civ_actions_enabled = game_running and player_civ is not None
        
        self.actions['tech_tree'].setEnabled(civ_actions_enabled)
        self.actions['diplomacy'].setEnabled(civ_actions_enabled)
        self.actions['economy'].setEnabled(civ_actions_enabled)
        self.actions['military'].setEnabled(civ_actions_enabled)


class MainWindowDockManager:
    """
    Gerencia os painéis de dock da janela principal.
    Responsável por criar e gerenciar os painéis laterais e inferiores.
    """
    
    def __init__(self, main_window, game_controller):
        """
        Inicializa o gerenciador de docks.
        
        Args:
            main_window: Referência à janela principal
            game_controller: Controlador do jogo
        """
        self.main_window = main_window
        self.game_controller = game_controller
        self.docks = {}
        self.panels = {}
        
        # Criar painéis
        self.setup_info_panel()
        self.setup_minimap_panel()
        self.setup_unit_panel()
        self.setup_city_panel()
    
    def setup_info_panel(self):
        """Configura o painel de informações."""
        self.panels['info'] = InfoPanel(self.game_controller)
        self.docks['info'] = GUIFactory.create_dock_widget(
            "Game Info", 
            self.panels['info'], 
            self.main_window, 
            Qt.TopDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.TopDockWidgetArea, self.docks['info'])
    
    def setup_minimap_panel(self):
        """Configura o painel do minimapa."""
        self.panels['minimap'] = MinimapPanel(self.game_controller)
        self.docks['minimap'] = GUIFactory.create_dock_widget(
            "Minimap", 
            self.panels['minimap'], 
            self.main_window, 
            Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.BottomDockWidgetArea, self.docks['minimap'])
    
    def setup_unit_panel(self):
        """Configura o painel de unidades."""
        self.panels['unit'] = UnitPanel(self.game_controller)
        self.docks['unit'] = GUIFactory.create_dock_widget(
            "Unit Info", 
            self.panels['unit'], 
            self.main_window, 
            Qt.RightDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.docks['unit'])
    
    def setup_city_panel(self):
        """Configura o painel de cidades."""
        self.panels['city'] = CityPanel(self.game_controller)
        self.docks['city'] = GUIFactory.create_dock_widget(
            "City Info", 
            self.panels['city'], 
            self.main_window, 
            Qt.RightDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.docks['city'])
    
    def get_panel(self, panel_name):
        """
        Obtém um painel pelo nome.
        
        Args:
            panel_name: Nome do painel
            
        Returns:
            O painel correspondente ou None se não encontrado
        """
        return self.panels.get(panel_name)
    
    def get_dock(self, dock_name):
        """
        Obtém um dock pelo nome.
        
        Args:
            dock_name: Nome do dock
            
        Returns:
            QDockWidget: O dock correspondente ou None se não encontrado
        """
        return self.docks.get(dock_name)
    
    def toggle_dock(self, dock_name):
        """
        Alterna a visibilidade de um dock.
        
        Args:
            dock_name: Nome do dock
            
        Returns:
            bool: True se o dock está visível após a operação, False caso contrário
        """
        dock = self.docks.get(dock_name)
        if dock:
            dock.setVisible(not dock.isVisible())
            return dock.isVisible()
        return False
    
    def update_panels(self):
        """Atualiza todos os painéis com base no estado do jogo."""
        for panel in self.panels.values():
            if hasattr(panel, 'update_panel'):
                panel.update_panel()


class MainWindow(QMainWindow):
    """Main application window for the Civilization game."""
    
    # Sinais para comunicação com outros componentes
    game_started = pyqtSignal()
    game_loaded = pyqtSignal(str)
    game_saved = pyqtSignal(str)
    turn_ended = pyqtSignal()
    
    def __init__(self, game_controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_controller = game_controller
        
        # Carregar idioma do usuário ou padrão
        self.i18n = I18n(
            'data/game_text.json',
            'data/game_text.user.json',
            lang=getattr(config, 'LANG', 'pt-BR')
        )
        # Exemplo de uso: self.i18n.t('main_menu.title', default='Civilization Clone')
        self.setWindowTitle(self.i18n.t('main_menu.title', default='Civilization Clone'))
        # Integrar i18n em menus principais
        self.menuBar().clear()
        self.menuBar().addMenu(self.i18n.t('main_menu.title', default='Game'))
        # Para cada menu, use self.i18n.t('main_menu.new_game'), etc.
        # Exemplo para botões:
        # self.new_game_button.setText(self.i18n.t('main_menu.new_game'))
        # ...continue integrando i18n nos demais componentes conforme necessário...
        
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Estado da janela
        self.is_fullscreen = config.FULLSCREEN
        self.normal_geometry = None
        
        # Configurar componentes da GUI
        self.setup_central_widget()
        self.menu_manager = MainWindowMenuManager(self, game_controller)
        self.dock_manager = MainWindowDockManager(self, game_controller)
        
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
        self.dock_manager.get_panel('info').update_turn()
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
        self.dock_manager.get_panel('city').update_city()
    
    def on_map_updated(self):
        """Manipulador para atualização do mapa."""
        self.map_widget.update_map()
        self.dock_manager.get_panel('minimap').update_minimap()
    
    def on_game_started(self):
        """Manipulador para início de jogo."""
        self.game_started.emit()
        self.menu_manager.update_actions()
        self.dock_manager.update_panels()
        self.status_bar.showMessage("Game started")
    
    def on_game_loaded(self):
        """Manipulador para carregamento de jogo."""
        self.game_loaded.emit(self.game_controller.get_game_state().id)
        self.menu_manager.update_actions()
        self.dock_manager.update_panels()
        self.status_bar.showMessage("Game loaded")
    
    def on_game_saved(self):
        """Manipulador para salvamento de jogo."""
        self.game_saved.emit(self.game_controller.get_game_state().id)
        self.status_bar.showMessage("Game saved")
    
    def on_tile_clicked(self, x, y):
        """
        Manipulador para clique em um tile do mapa.
        
        Args:
            x, y: Coordenadas do tile
        """
        # Obter informações do tile
        world = self.game_controller.get_world()
        if not world:
            return
        
        tile = world.get_tile(x, y)
        if not tile:
            return
        
        # Verificar se há unidades no tile
        units = self.game_controller.get_units_at(x, y)
        if units:
            # Selecionar a primeira unidade
            self.dock_manager.get_panel('unit').set_unit(units[0])
        
        # Verificar se há cidade no tile
        city = self.game_controller.get_city_at(x, y)
        if city:
            self.dock_manager.get_panel('city').set_city(city)
        
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
        if not self.game_controller.get_game_state():
            QMessageBox.warning(self, "Save Game", "No game in progress to save.")
            return
        
        # Se o jogo já foi salvo, usar o mesmo nome
        game_state = self.game_controller.get_game_state()
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
            QMessageBox.warning(self, "Save Game", "No game in progress to save.")
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
    
    def apply_settings(self, settings):
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
            reply = QMessageBox.question(
                self, 'Exit Game',
                'The current game is not saved. Do you want to save before exiting?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
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


# Implementação dos diálogos mencionados

class AboutDialog(QDialog):
    """Diálogo 'Sobre' com informações sobre o jogo."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Project CIVILIZATION")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PyQt5.QtGui import QPixmap, QFont
        from PyQt5.QtCore import Qt
        
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


class NewGameDialog(QDialog):
    """Diálogo para configurar um novo jogo."""
    
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        self.setWindowTitle("New Game")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                                    QComboBox, QGroupBox, QGridLayout, QCheckBox)
        
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
        from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                                    QLineEdit, QListWidget, QListWidgetItem)
        
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
            from PyQt5.QtWidgets import QMessageBox
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
        from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                                    QListWidget, QListWidgetItem, QSplitter, QTextBrowser)
        from PyQt5.QtCore import Qt
        
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
        
        from PyQt5.QtWidgets import QMessageBox
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


class OptionsDialog(QDialog):
    """Diálogo de opções do jogo."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        self.settings = {}
        self.load_current_settings()
        self.setup_ui()
    
    def load_current_settings(self):
        """Carrega as configurações atuais."""
        import config
        
        # Configurações de exibição
        self.settings['fullscreen'] = config.FULLSCREEN
        self.settings['window_width'] = config.WINDOW_WIDTH
        self.settings['window_height'] = config.WINDOW_HEIGHT
        
        # Configurações gráficas
        self.settings['enable_3d'] = config.ENABLE_3D
        self.settings['render_quality'] = config.RENDER_QUALITY
        self.settings['animation_speed'] = config.ANIMATION_SPEED
        self.settings['vsync'] = config.VSYNC
        
        # Configurações de câmera
        self.settings['camera_start_height'] = config.CAMERA_START_HEIGHT
        self.settings['camera_min_height'] = config.CAMERA_MIN_HEIGHT
        self.settings['camera_max_height'] = config.CAMERA_MAX_HEIGHT
        self.settings['camera_rotation_speed'] = config.CAMERA_ROTATION_SPEED
        self.settings['camera_zoom_speed'] = config.CAMERA_ZOOM_SPEED
        
        # Configurações de UI
        self.settings['ui_scale'] = config.UI_SCALE
        self.settings['font_size'] = config.FONT_SIZE
        self.settings['show_tooltips'] = config.SHOW_TOOLTIPS
        self.settings['tooltip_delay'] = config.TOOLTIP_DELAY
        
        # Configurações de som
        self.settings['enable_sound'] = config.ENABLE_SOUND
        self.settings['music_volume'] = config.MUSIC_VOLUME
        self.settings['sfx_volume'] = config.SFX_VOLUME
        
        # Configurações de visualização do mapa
        self.settings['show_grid'] = True  # Valor padrão
        self.settings['show_resources'] = True  # Valor padrão
        self.settings['show_improvements'] = True  # Valor padrão
    
    def setup_ui(self):
        """Configura a interface do diálogo."""
        from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                                    QTabWidget, QWidget, QGridLayout, QCheckBox,
                                    QComboBox, QSlider, QSpinBox, QDoubleSpinBox)
        from PyQt5.QtCore import Qt
        
        layout = QVBoxLayout()
        
        # Criar abas
        tab_widget = QTabWidget()
        
        # Aba de exibição
        display_tab = QWidget()
        display_layout = QGridLayout()
        
        # Modo de tela cheia
        display_layout.addWidget(QLabel("Fullscreen:"), 0, 0)
        self.fullscreen_check = QCheckBox()
        self.fullscreen_check.setChecked(self.settings['fullscreen'])
        display_layout.addWidget(self.fullscreen_check, 0, 1)
        
        # Resolução
        display_layout.addWidget(QLabel("Resolution:"), 1, 0)
        resolution_layout = QHBoxLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(800, 3840)
        self.width_spin.setValue(self.settings['window_width'])
        resolution_layout.addWidget(self.width_spin)
        
        resolution_layout.addWidget(QLabel("x"))
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(600, 2160)
        self.height_spin.setValue(self.settings['window_height'])
        resolution_layout.addWidget(self.height_spin)
        
        display_layout.addLayout(resolution_layout, 1, 1)
        
        # VSync
        display_layout.addWidget(QLabel("VSync:"), 2, 0)
        self.vsync_check = QCheckBox()
        self.vsync_check.setChecked(self.settings['vsync'])
        display_layout.addWidget(self.vsync_check, 2, 1)
        
        display_tab.setLayout(display_layout)
        tab_widget.addTab(display_tab, "Display")
        
        # Aba de gráficos
        graphics_tab = QWidget()
        graphics_layout = QGridLayout()
        
        # Qualidade de renderização
        graphics_layout.addWidget(QLabel("Render Quality:"), 0, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High"])
        self.quality_combo.setCurrentText(self.settings['render_quality'])
        graphics_layout.addWidget(self.quality_combo, 0, 1)
        
        # Velocidade de animação
        graphics_layout.addWidget(QLabel("Animation Speed:"), 1, 0)
        self.animation_slider = QSlider(Qt.Horizontal)
        self.animation_slider.setRange(0, 20)
        self.animation_slider.setValue(int(self.settings['animation_speed'] * 10))
        graphics_layout.addWidget(self.animation_slider, 1, 1)
        
        # Mostrar grade
        graphics_layout.addWidget(QLabel("Show Grid:"), 2, 0)
        self.grid_check = QCheckBox()
        self.grid_check.setChecked(self.settings['show_grid'])
        graphics_layout.addWidget(self.grid_check, 2, 1)
        
        # Mostrar recursos
        graphics_layout.addWidget(QLabel("Show Resources:"), 3, 0)
        self.resources_check = QCheckBox()
        self.resources_check.setChecked(self.settings['show_resources'])
        graphics_layout.addWidget(self.resources_check, 3, 1)
        
        # Mostrar melhorias
        graphics_layout.addWidget(QLabel("Show Improvements:"), 4, 0)
        self.improvements_check = QCheckBox()
        self.improvements_check.setChecked(self.settings['show_improvements'])
        graphics_layout.addWidget(self.improvements_check, 4, 1)
        
        graphics_tab.setLayout(graphics_layout)
        tab_widget.addTab(graphics_tab, "Graphics")
        
        # Aba de som
        sound_tab = QWidget()
        sound_layout = QGridLayout()
        
        # Habilitar som
        sound_layout.addWidget(QLabel("Enable Sound:"), 0, 0)
        self.sound_check = QCheckBox()
        self.sound_check.setChecked(self.settings['enable_sound'])
        sound_layout.addWidget(self.sound_check, 0, 1)
        
        # Volume de música
        sound_layout.addWidget(QLabel("Music Volume:"), 1, 0)
        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(int(self.settings['music_volume'] * 100))
        sound_layout.addWidget(self.music_slider, 1, 1)
        
        # Volume de efeitos sonoros
        sound_layout.addWidget(QLabel("SFX Volume:"), 2, 0)
        self.sfx_slider = QSlider(Qt.Horizontal)
        self.sfx_slider.setRange(0, 100)
        self.sfx_slider.setValue(int(self.settings['sfx_volume'] * 100))
        sound_layout.addWidget(self.sfx_slider, 2, 1)
        
        sound_tab.setLayout(sound_layout)
        tab_widget.addTab(sound_tab, "Sound")
        
        # Aba de interface
        ui_tab = QWidget()
        ui_layout = QGridLayout()
        
        # Escala da UI
        ui_layout.addWidget(QLabel("UI Scale:"), 0, 0)
        self.ui_scale_spin = QDoubleSpinBox()
        self.ui_scale_spin.setRange(0.5, 2.0)
        self.ui_scale_spin.setSingleStep(0.1)
        self.ui_scale_spin.setValue(self.settings['ui_scale'])
        ui_layout.addWidget(self.ui_scale_spin, 0, 1)
        
        # Tamanho da fonte
        ui_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.settings['font_size'])
        ui_layout.addWidget(self.font_size_spin, 1, 1)
        
        # Mostrar tooltips
        ui_layout.addWidget(QLabel("Show Tooltips:"), 2, 0)
        self.tooltips_check = QCheckBox()
        self.tooltips_check.setChecked(self.settings['show_tooltips'])
        ui_layout.addWidget(self.tooltips_check, 2, 1)
        
        ui_tab.setLayout(ui_layout)
        tab_widget.addTab(ui_tab, "Interface")
        
        layout.addWidget(tab_widget)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.on_apply)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.on_reset)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.resize(500, 400)
    
    def on_apply(self):
        """Manipulador para botão de aplicar."""
        self.update_settings()
        
        # Emitir sinal para aplicar configurações
        if hasattr(self.parent(), 'apply_settings'):
            self.parent().apply_settings(self.settings)
    
    def on_ok(self):
        """Manipulador para botão OK."""
        self.update_settings()
        self.accept()
    
    def on_reset(self):
        """Manipulador para botão de redefinir."""
        # Recarregar configurações padrão
        import config
        
        # Configurações de exibição
        self.fullscreen_check.setChecked(config.FULLSCREEN)
        self.width_spin.setValue(config.WINDOW_WIDTH)
        self.height_spin.setValue(config.WINDOW_HEIGHT)
        self.vsync_check.setChecked(config.VSYNC)
        
        # Configurações gráficas
        self.quality_combo.setCurrentText(config.RENDER_QUALITY)
        self.animation_slider.setValue(int(config.ANIMATION_SPEED * 10))
        self.grid_check.setChecked(True)
        self.resources_check.setChecked(True)
        self.improvements_check.setChecked(True)
        
        # Configurações de som
        self.sound_check.setChecked(config.ENABLE_SOUND)
        self.music_slider.setValue(int(config.MUSIC_VOLUME * 100))
        self.sfx_slider.setValue(int(config.SFX_VOLUME * 100))
        
        # Configurações de interface
        self.ui_scale_spin.setValue(config.UI_SCALE)
        self.font_size_spin.setValue(config.FONT_SIZE)
        self.tooltips_check.setChecked(config.SHOW_TOOLTIPS)
    
    def update_settings(self):
        """Atualiza as configurações com base nos valores da interface."""
        # Configurações de exibição
        self.settings['fullscreen'] = self.fullscreen_check.isChecked()
        self.settings['window_width'] = self.width_spin.value()
        self.settings['window_height'] = self.height_spin.value()
        self.settings['vsync'] = self.vsync_check.isChecked()
        
        # Configurações gráficas
        self.settings['render_quality'] = self.quality_combo.currentText()
        self.settings['animation_speed'] = self.animation_slider.value() / 10.0
        self.settings['show_grid'] = self.grid_check.isChecked()
        self.settings['show_resources'] = self.resources_check.isChecked()
        self.settings['show_improvements'] = self.improvements_check.isChecked()
        
        # Configurações de som
        self.settings['enable_sound'] = self.sound_check.isChecked()
        self.settings['music_volume'] = self.music_slider.value() / 100.0
        self.settings['sfx_volume'] = self.sfx_slider.value() / 100.0
        
        # Configurações de interface
        self.settings['ui_scale'] = self.ui_scale_spin.value()
        self.settings['font_size'] = self.font_size_spin.value()
        self.settings['show_tooltips'] = self.tooltips_check.isChecked()
    
    def get_settings(self):
        """
        Obtém as configurações atuais.
        
        Returns:
            dict: Configurações atuais
        """
        return self.settings
