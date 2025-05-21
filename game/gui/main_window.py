from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction, QMenuBar, QStatusBar
from PyQt5.QtCore import Qt, QSize
import config

from game.gui.map_view import MapGLWidget
from game.gui.info_panel import InfoPanel
from game.gui.minimap_panel import MinimapPanel
from game.gui.unit_panel import UnitPanel
from game.gui.city_panel import CityPanel
from game.gui.tech_dialog import TechDialog
from game.gui.diplomacy_dialog import DiplomacyDialog
from game.gui.options_dialog import OptionsDialog


class MainWindow(QMainWindow):
    """Main application window for the Civilization game."""
    
    def __init__(self, game_controller):
        super().__init__()
        self.game_controller = game_controller
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Set up central widget (3D map)
        self.map_widget = MapGLWidget(self.game_controller)
        self.setCentralWidget(self.map_widget)
        
        # Create dock widgets
        self.setup_dock_widgets()
        
        # Create menus
        self.setup_menus()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Connect signals
        self.connect_signals()
    
    def setup_dock_widgets(self):
        """Set up the dock widgets for various game panels."""
        # Info panel (top)
        self.info_panel = InfoPanel(self.game_controller)
        info_dock = QDockWidget("Game Info", self)
        info_dock.setWidget(self.info_panel)
        info_dock.setAllowedAreas(Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.TopDockWidgetArea, info_dock)
        
        # Minimap panel (bottom right)
        self.minimap_panel = MinimapPanel(self.game_controller)
        minimap_dock = QDockWidget("Minimap", self)
        minimap_dock.setWidget(self.minimap_panel)
        minimap_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, minimap_dock)
        
        # Unit panel (right)
        self.unit_panel = UnitPanel(self.game_controller)
        unit_dock = QDockWidget("Unit Info", self)
        unit_dock.setWidget(self.unit_panel)
        unit_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, unit_dock)
        
        # City panel (right)
        self.city_panel = CityPanel(self.game_controller)
        city_dock = QDockWidget("City Info", self)
        city_dock.setWidget(self.city_panel)
        city_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, city_dock)
        
    def setup_menus(self):
        """Set up the application menus."""
        # Game menu
        game_menu = self.menuBar().addMenu("Game")
        
        new_game_action = QAction("New Game", self)
        new_game_action.triggered.connect(self.on_new_game)
        game_menu.addAction(new_game_action)
        
        load_game_action = QAction("Load Game", self)
        load_game_action.triggered.connect(self.on_load_game)
        game_menu.addAction(load_game_action)
        
        save_game_action = QAction("Save Game", self)
        save_game_action.triggered.connect(self.on_save_game)
        game_menu.addAction(save_game_action)
        
        game_menu.addSeparator()
        
        options_action = QAction("Options", self)
        options_action.triggered.connect(self.on_options)
        game_menu.addAction(options_action)
        
        game_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("View")
        
        toggle_minimap_action = QAction("Toggle Minimap", self)
        toggle_minimap_action.triggered.connect(self.on_toggle_minimap)
        view_menu.addAction(toggle_minimap_action)
        
        toggle_grid_action = QAction("Toggle Grid", self)
        toggle_grid_action.triggered.connect(self.on_toggle_grid)
        view_menu.addAction(toggle_grid_action)
        
        # Civilization menu
        civ_menu = self.menuBar().addMenu("Civilization")
        
        tech_tree_action = QAction("Technology Tree", self)
        tech_tree_action.triggered.connect(self.on_tech_tree)
        civ_menu.addAction(tech_tree_action)
        
        diplomacy_action = QAction("Diplomacy", self)
        diplomacy_action.triggered.connect(self.on_diplomacy)
        civ_menu.addAction(diplomacy_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """Connect signals between components."""
        # Connect game controller signals to UI updates
        self.game_controller.turn_changed.connect(self.info_panel.update_turn)
        self.game_controller.turn_ended.connect(self.info_panel.update_turn)
        self.game_controller.active_city_changed.connect(self.city_panel.update_city)
        self.game_controller.map_updated.connect(self.map_widget.update_map)
        self.game_controller.map_updated.connect(self.minimap_panel.update_minimap)
    
    # Event handlers
    def on_new_game(self):
        """Handle new game action."""
        # TODO: Implement new game dialog and initialization
        self.status_bar.showMessage("Starting new game...")
    
    def on_load_game(self):
        """Handle load game action."""
        # TODO: Implement load game dialog
        self.status_bar.showMessage("Loading game...")
    
    def on_save_game(self):
        """Handle save game action."""
        # TODO: Implement save game dialog
        self.status_bar.showMessage("Saving game...")
    
    def on_options(self):
        """Handle options action."""
        dialog = OptionsDialog(self)
        if dialog.exec_():
            # Apply new settings
            self.status_bar.showMessage("Settings updated")
    
    def on_toggle_minimap(self):
        """Toggle minimap visibility."""
        # TODO: Implement minimap toggle
        self.status_bar.showMessage("Toggled minimap")
    
    def on_toggle_grid(self):
        """Toggle grid visibility."""
        self.map_widget.toggle_grid()
        self.status_bar.showMessage("Toggled grid")
    
    def on_tech_tree(self):
        """Show technology tree dialog."""
        dialog = TechDialog(self.game_controller, self)
        dialog.exec_()
    
    def on_diplomacy(self):
        """Show diplomacy dialog."""
        dialog = DiplomacyDialog(self.game_controller, self)
        dialog.exec_()
    
    def on_about(self):
        """Show about dialog."""
        # TODO: Implement about dialog
        self.status_bar.showMessage("About dialog")
