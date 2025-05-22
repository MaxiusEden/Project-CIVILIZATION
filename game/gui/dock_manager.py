from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt
from typing import Dict, Any, Optional

from game.gui.gui_factory import GUIFactory
from game.gui.info_panel import InfoPanel
from game.gui.minimap_panel import MinimapPanel
from game.gui.unit_panel import UnitPanel
from game.gui.city_panel import CityPanel

class DockManager:
    """
    Gerenciador de docks para a janela principal.
    
    Esta classe é responsável por criar e gerenciar todos os painéis
    laterais e inferiores da janela principal, fornecendo uma interface
    unificada para acessar e atualizar os painéis.
    """
    
    def __init__(self, main_window, game_controller):
        """
        Inicializa o gerenciador de docks.
        
        Args:
            main_window: A janela principal
            game_controller: O controlador do jogo
        """
        self.main_window = main_window
        self.game_controller = game_controller
        self.docks: Dict[str, QDockWidget] = {}
        self.panels: Dict[str, Any] = {}
        
        # Criar painéis
        self._setup_panels()
    def _setup_panels(self):
        """Configura todos os painéis da interface."""
        self._setup_info_panel()
        self._setup_minimap_panel()
        self._setup_unit_panel()
        self._setup_city_panel()

        # Tabificar alguns painéis (agrupar em abas)
        self.main_window.tabifyDockWidget(self.docks['unit'], self.docks['city'])

        # Garantir que o painel de unidades esteja visível inicialmente
        self.docks['unit'].raise_()

    def _setup_info_panel(self):
        """Configura o painel de informações gerais do jogo."""
        self.panels['info'] = InfoPanel(self.game_controller)
        info_dock = GUIFactory.create_dock_widget(
            "Game Info", 
            self.panels['info'], 
            self.main_window,
            Qt.TopDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.TopDockWidgetArea, info_dock)
        self.docks['info'] = info_dock
    
    def _setup_minimap_panel(self):
        """Configura o painel do minimapa."""
        self.panels['minimap'] = MinimapPanel(self.game_controller)
        minimap_dock = GUIFactory.create_dock_widget(
            "Minimap", 
            self.panels['minimap'], 
            self.main_window,
            Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.BottomDockWidgetArea, minimap_dock)
        self.docks['minimap'] = minimap_dock
    
    def _setup_unit_panel(self):
        """Configura o painel de informações de unidades."""
        self.panels['unit'] = UnitPanel(self.game_controller)
        unit_dock = GUIFactory.create_dock_widget(
            "Unit Info", 
            self.panels['unit'], 
            self.main_window,
            Qt.RightDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, unit_dock)
        self.docks['unit'] = unit_dock
    
    def _setup_city_panel(self):
        """Configura o painel de informações de cidades."""
        self.panels['city'] = CityPanel(self.game_controller)
        city_dock = GUIFactory.create_dock_widget(
            "City Info", 
            self.panels['city'], 
            self.main_window,
            Qt.RightDockWidgetArea
        )
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, city_dock)
        self.docks['city'] = city_dock
    
    def get_dock(self, dock_name: str) -> Optional[QDockWidget]:
        """
        Obtém um dock pelo nome.
        
        Args:
            dock_name: Nome do dock
            
        Returns:
            QDockWidget: O dock correspondente ou None se não existir
        """
        return self.docks.get(dock_name)
    
    def get_panel(self, panel_name: str) -> Optional[Any]:
        """
        Obtém um painel pelo nome.
        
        Args:
            panel_name: Nome do painel
            
        Returns:
            O painel correspondente ou None se não existir
        """
        return self.panels.get(panel_name)
    
    def toggle_dock(self, dock_name: str) -> bool:
        """
        Alterna a visibilidade de um dock.
        
        Args:
            dock_name: Nome do dock
            
        Returns:
            bool: True se o dock estiver visível após a operação, False caso contrário
        """
        dock = self.get_dock(dock_name)
        if dock:
            dock.setVisible(not dock.isVisible())
            return dock.isVisible()
        return False
    
    def update_panels(self):
        """Atualiza todos os painéis com os dados atuais do jogo."""
        for panel_name, panel in self.panels.items():
            if hasattr(panel, 'update_panel'):
                panel.update_panel()

    def update_info_panel(self):
        """Atualiza apenas o painel de informações."""
        if 'info' in self.panels and hasattr(self.panels['info'], 'update_panel'):
            self.panels['info'].update_panel()

    def update_unit_panel(self, unit=None):
        """
        Atualiza o painel de unidades.

        Args:
            unit: Unidade a ser exibida (opcional)
        """
        if 'unit' in self.panels:
            if unit:
                self.panels['unit'].set_unit(unit)
            elif hasattr(self.panels['unit'], 'update_panel'):
                self.panels['unit'].update_panel()

            # Tornar o dock visível se estiver oculto
            if not self.docks['unit'].isVisible():
                self.docks['unit'].setVisible(True)
            self.docks['unit'].raise_()

    def update_city_panel(self, city=None):
        """
        Atualiza o painel de cidades.

        Args:
            city: Cidade a ser exibida (opcional)
        """
        if 'city' in self.panels:
            if city:
                self.panels['city'].set_city(city)
            elif hasattr(self.panels['city'], 'update_panel'):
                self.panels['city'].update_panel()

            # Tornar o dock visível se estiver oculto
            if not self.docks['city'].isVisible():
                self.docks['city'].setVisible(True)
            self.docks['city'].raise_()

    def clear_selection(self):
        """Limpa a seleção em todos os painéis."""
        if 'unit' in self.panels and hasattr(self.panels['unit'], 'clear'):
            self.panels['unit'].clear()

        if 'city' in self.panels and hasattr(self.panels['city'], 'clear'):
            self.panels['city'].clear()

    def restore_default_layout(self):
        """Restaura o layout padrão dos docks."""
        # Mostrar todos os docks
        for dock in self.docks.values():
            dock.setVisible(True)

        # Reposicionar docks
        self.main_window.addDockWidget(Qt.TopDockWidgetArea, self.docks['info'])
        self.main_window.addDockWidget(Qt.BottomDockWidgetArea, self.docks['minimap'])
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.docks['unit'])
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.docks['city'])

        # Tabificar novamente
        self.main_window.tabifyDockWidget(self.docks['unit'], self.docks['city'])
        self.docks['unit'].raise_()


# Mantendo a classe original para compatibilidade
class MainWindowDockManager(DockManager):
    """
    Classe legada para compatibilidade com código existente.
    Use DockManager para novas implementações.
    """

    def setup_info_panel(self):
        """Compatibilidade com código existente."""
        self._setup_info_panel()

    def setup_minimap_panel(self):
        """Compatibilidade com código existente."""
        self._setup_minimap_panel()

    def setup_unit_panel(self):
        """Compatibilidade com código existente."""
        self._setup_unit_panel()

    def setup_city_panel(self):
        """Compatibilidade com código existente."""
        self._setup_city_panel()

    def update_all_panels(self):
        """Compatibilidade com código existente."""
        self.update_panels()
