from PyQt5.QtWidgets import QMenuBar, QAction, QMenu, QActionGroup, QToolBar
from PyQt5.QtCore import Qt
from typing import Dict, Any, Optional, List, Callable, Union

from game.gui.gui_factory import GUIFactory

class MenuManager:
    """
    Gerenciador de menus para a janela principal.
    
    Esta classe é responsável por criar e gerenciar todos os menus
    e ações da janela principal, fornecendo uma interface unificada
    para acessar e atualizar o estado das ações.
    """
    
    def __init__(self, main_window, game_controller):
        """
        Inicializa o gerenciador de menus.
        
        Args:
            main_window: A janela principal
            game_controller: O controlador do jogo
        """
        self.main_window = main_window
        self.game_controller = game_controller
        self.actions: Dict[str, QAction] = {}
        self.menus: Dict[str, QMenu] = {}
        self.action_groups: Dict[str, QActionGroup] = {}
        
        # Criar menus
        self._setup_menus()
    def _setup_menus(self):
        """Configura todos os menus da aplicação."""
        self._setup_game_menu()
        self._setup_view_menu()
        self._setup_civilization_menu()
        self._setup_help_menu()

    def _setup_game_menu(self):
        """Configura o menu Jogo."""
        # Criar ações
        self.actions['new_game'] = GUIFactory.create_action(
            self.main_window, "New Game", 
            self.main_window.on_new_game, "Ctrl+N",
            tip="Start a new game"
        )
        
        self.actions['load_game'] = GUIFactory.create_action(
            self.main_window, "Load Game", 
            self.main_window.on_load_game, "Ctrl+L",
            tip="Load a saved game"
        )
        
        self.actions['save_game'] = GUIFactory.create_action(
            self.main_window, "Save Game", 
            self.main_window.on_save_game, "Ctrl+S",
            tip="Save the current game",
            enabled=False  # Desabilitado inicialmente
        )
        
        self.actions['save_game_as'] = GUIFactory.create_action(
            self.main_window, "Save Game As...", 
            self.main_window.on_save_game_as, "Ctrl+Shift+S",
            tip="Save the current game with a new name",
            enabled=False  # Desabilitado inicialmente
        )
        
        self.actions['options'] = GUIFactory.create_action(
            self.main_window, "Options", 
            self.main_window.on_options,
            tip="Configure game options"
        )
        
        self.actions['exit'] = GUIFactory.create_action(
            self.main_window, "Exit", 
            self.main_window.close, "Alt+F4",
            tip="Exit the game"
        )
        
        # Criar menu
        game_menu = self.main_window.menuBar().addMenu("Game")
        game_menu.addAction(self.actions['new_game'])
        game_menu.addAction(self.actions['load_game'])
        game_menu.addAction(self.actions['save_game'])
        game_menu.addAction(self.actions['save_game_as'])
        game_menu.addSeparator()
        game_menu.addAction(self.actions['options'])
        game_menu.addSeparator()
        game_menu.addAction(self.actions['exit'])
        
        self.menus['game'] = game_menu
    
    def _setup_view_menu(self):
        """Configura o menu Visualização."""
        # Criar menu
        view_menu = self.main_window.menuBar().addMenu("View")
        self.menus['view'] = view_menu
    
        # Submenu de painéis
        panels_menu = view_menu.addMenu("Panels")
        self.menus['panels'] = panels_menu

        # Criar ações para painéis
        self.actions['toggle_minimap'] = GUIFactory.create_action(
            self.main_window, "Minimap",
            self.main_window.on_toggle_minimap, "M",
            tip="Show or hide the minimap",
            checkable=True, checked=True
        )
        panels_menu.addAction(self.actions['toggle_minimap'])
        
        self.actions['toggle_info'] = GUIFactory.create_action(
            self.main_window, "Info Panel",
            lambda: self.main_window.on_toggle_panel('info'), "I",
            tip="Show or hide the information panel",
            checkable=True, checked=True
        )
        panels_menu.addAction(self.actions['toggle_info'])
        
        self.actions['toggle_unit'] = GUIFactory.create_action(
            self.main_window, "Unit Panel",
            lambda: self.main_window.on_toggle_panel('unit'), "U",
            tip="Show or hide the unit panel",
            checkable=True, checked=True
        )
        panels_menu.addAction(self.actions['toggle_unit'])
        
        self.actions['toggle_city'] = GUIFactory.create_action(
            self.main_window, "City Panel",
            lambda: self.main_window.on_toggle_panel('city'), "C",
            tip="Show or hide the city panel",
            checkable=True, checked=True
        )
        panels_menu.addAction(self.actions['toggle_city'])
        
        # Restaurar layout
        panels_menu.addSeparator()
        self.actions['restore_layout'] = GUIFactory.create_action(
            self.main_window, "Restore Default Layout",
            self.main_window.on_restore_layout,
            tip="Restore the default panel layout"
        )
        panels_menu.addAction(self.actions['restore_layout'])

        # Submenu de visualização do mapa
        view_menu.addSeparator()
        map_menu = view_menu.addMenu("Map View")
        self.menus['map_view'] = map_menu
    
        # Ações para visualização do mapa
        self.actions['toggle_grid'] = GUIFactory.create_action(
            self.main_window, "Grid",
            self.main_window.on_toggle_grid, "G",
            tip="Show or hide the grid",
            checkable=True, checked=True
        )
        map_menu.addAction(self.actions['toggle_grid'])
        
        self.actions['toggle_resources'] = GUIFactory.create_action(
            self.main_window, "Resources",
            self.main_window.on_toggle_resources, "R",
            tip="Show or hide resources",
            checkable=True, checked=True
        )
        map_menu.addAction(self.actions['toggle_resources'])

        self.actions['toggle_improvements'] = GUIFactory.create_action(
            self.main_window, "Improvements",
            self.main_window.on_toggle_improvements, "Shift+I",
            tip="Show or hide improvements",
            checkable=True, checked=True
        )
        map_menu.addAction(self.actions['toggle_improvements'])
        
        self.actions['toggle_units'] = GUIFactory.create_action(
            self.main_window, "Units",
            self.main_window.on_toggle_units, "Shift+U",
            tip="Show or hide units on the map",
            checkable=True, checked=True
        )
        map_menu.addAction(self.actions['toggle_units'])

        # Qualidade de renderização
        view_menu.addSeparator()
        render_menu = view_menu.addMenu("Render Quality")
        self.menus['render_quality'] = render_menu

        # Grupo de ações para qualidade de renderização
        render_group = QActionGroup(self.main_window)
        render_group.setExclusive(True)
        self.action_groups['render_quality'] = render_group

        # Opções de qualidade
        for quality in ["Low", "Medium", "High"]:
            action = GUIFactory.create_action(
                self.main_window, quality,
                lambda q=quality: self.main_window.on_set_render_quality(q),
                tip=f"Set render quality to {quality}",
                checkable=True,
                checked=(quality == "Medium")  # Padrão: Medium
            )
            render_group.addAction(action)
            render_menu.addAction(action)
            self.actions[f'render_{quality.lower()}'] = action

        # Fullscreen
        view_menu.addSeparator()
        self.actions['fullscreen'] = GUIFactory.create_action(
            self.main_window, "Fullscreen",
            self.main_window.on_toggle_fullscreen, "F11",
            tip="Toggle fullscreen mode",
            checkable=True, checked=False
        )
        view_menu.addAction(self.actions['fullscreen'])

    def _setup_civilization_menu(self):
        """Configura o menu Civilização."""
        # Criar ações
        self.actions['tech_tree'] = GUIFactory.create_action(
            self.main_window, "Technology Tree",
            self.main_window.on_tech_tree, "T",
            tip="View the technology tree",
            enabled=False  # Desabilitado inicialmente
        )

        self.actions['diplomacy'] = GUIFactory.create_action(
            self.main_window, "Diplomacy",
            self.main_window.on_diplomacy, "D",
            tip="Manage diplomatic relations",
            enabled=False  # Desabilitado inicialmente
        )

        self.actions['economy'] = GUIFactory.create_action(
            self.main_window, "Economy",
            self.main_window.on_economy, "E",
            tip="View economic information",
            enabled=False  # Desabilitado inicialmente
        )

        self.actions['military'] = GUIFactory.create_action(
            self.main_window, "Military",
            self.main_window.on_military, "Shift+M",
            tip="View military information",
            enabled=False  # Desabilitado inicialmente
        )

        self.actions['end_turn'] = GUIFactory.create_action(
            self.main_window, "End Turn",
            self.main_window.on_end_turn, "Enter",
            tip="End the current turn",
            enabled=False  # Desabilitado inicialmente
        )

        # Criar menu
        civ_menu = self.main_window.menuBar().addMenu("Civilization")
        civ_menu.addAction(self.actions['tech_tree'])
        civ_menu.addAction(self.actions['diplomacy'])
        civ_menu.addAction(self.actions['economy'])
        civ_menu.addAction(self.actions['military'])
        civ_menu.addSeparator()
        civ_menu.addAction(self.actions['end_turn'])

        self.menus['civilization'] = civ_menu

    def _setup_help_menu(self):
        """Configura o menu Ajuda."""
        # Criar ações
        self.actions['manual'] = GUIFactory.create_action(
            self.main_window, "Game Manual",
            self.main_window.on_manual, "F1",
            tip="View the game manual"
        )

        self.actions['about'] = GUIFactory.create_action(
            self.main_window, "About",
            self.main_window.on_about,
            tip="About Project CIVILIZATION"
        )

        # Criar menu
        help_menu = self.main_window.menuBar().addMenu("Help")
        help_menu.addAction(self.actions['manual'])
        help_menu.addSeparator()
        help_menu.addAction(self.actions['about'])

        self.menus['help'] = help_menu

    def get_action(self, action_name: str) -> Optional[QAction]:
        """
        Obtém uma ação pelo nome.
        
        Args:
            action_name: Nome da ação
            
        Returns:
            QAction: A ação correspondente ou None se não existir
        """
        return self.actions.get(action_name)
    
    def get_menu(self, menu_name: str) -> Optional[QMenu]:
        """
        Obtém um menu pelo nome.

        Args:
            menu_name: Nome do menu

        Returns:
            QMenu: O menu correspondente ou None se não existir
        """
        return self.menus.get(menu_name)

    def enable_game_actions(self, enabled=True):
        """
        Habilita ou desabilita ações relacionadas ao jogo.

        Args:
            enabled (bool): Se as ações devem ser habilitadas
        """
        game_actions = ['save_game', 'save_game_as', 'end_turn']
        for action_name in game_actions:
            if action_name in self.actions:
                self.actions[action_name].setEnabled(enabled)
