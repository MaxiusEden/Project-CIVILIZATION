from PyQt5.QtCore import QObject, pyqtSignal

from game.models.game_state import GameState
from game.models.world import World
from game.controllers.world_controller import WorldController
from game.controllers.civ_controller import CivController
from game.controllers.city_controller import CityController
from game.controllers.unit_controller import UnitController
from game.utils.data_loader import DataLoader
from game.utils.save_manager import SaveManager


class GameController(QObject):
    """Main controller for the game, manages game state and other controllers."""
    
    # Signals for GUI updates
    game_started = pyqtSignal()
    turn_ended = pyqtSignal()
    game_loaded = pyqtSignal()
    game_saved = pyqtSignal()
    turn_changed = pyqtSignal()
    active_city_changed = pyqtSignal()
    map_updated = pyqtSignal()
    
    def __init__(self):
        """Initialize the game controller."""
        super().__init__()
        
        # Initialize game state
        self.game_state = None
        
        # Initialize sub-controllers
        self.world_controller = None
        self.civ_controller = None
        self.city_controller = None
        self.unit_controller = None
        
        # Load game data
        self.data_loader = DataLoader()
        self.save_manager = SaveManager()
        
        # Load configuration
        self.config = self.data_loader.load_config()
    
    def new_game(self, config=None):
        """
        Start a new game with the given configuration.
        
        Args:
            config (dict, optional): Game configuration. Defaults to None.
        """
        # Use provided config or default
        if config is None:
            config = self.config.get('default_game', {})
        
        # Create new game state
        self.game_state = GameState()
        self.game_state.current_turn = 1

        # Crie o mundo
        world_size = config.get('world_size', 'standard')
        world_type = config.get('world_type', 'continents')
        world_config = self.config.get('world_sizes', {}).get(world_size, {})
        width = world_config.get('width', 40)
        height = world_config.get('height', 24)
        self.game_state.world = World(width, height)

        # **INICIALIZE O WORLD CONTROLLER AQUI**
        self.world_controller = WorldController(self.game_state)

        # Inicialize os outros controladores
        self.civ_controller = CivController(self)
        self.city_controller = CityController(self)
        self.unit_controller = UnitController(self)

        # Agora pode gerar o mundo
        self.world_controller.generate_world(world_type)
        
        # Create civilizations
        num_civs = config.get('num_civs', 4)
        player_civ_id = config.get('player_civ', 'rome')
        
        self.civ_controller.create_civilizations(num_civs, player_civ_id)
        
        # Place initial units and cities
        self.civ_controller.place_initial_units()
        
        # Set player civilization
        self.game_state.player_civ = self.civ_controller.get_player_civilization()        
        # Emit signal for GUI
        self.game_started.emit()
    
    def load_game(self, save_name):
        """
        Load a saved game.
        
        Args:
            save_name (str): Name of the save file.
        """
        # Load game state from file
        self.game_state = self.save_manager.load_game(save_name)
        
        # Initialize sub-controllers with loaded game state
        self.world_controller = WorldController(self.game_state)
        self.civ_controller = CivController(self.game_state)
        self.city_controller = CityController(self.game_state)
        self.unit_controller = UnitController(self.game_state)
        
        # Emit signal for GUI
        self.game_loaded.emit()
    
    def save_game(self, save_name):
        """
        Save the current game.
        
        Args:
            save_name (str): Name for the save file.
        """
        # Save game state to file
        self.save_manager.save_game(self.game_state, save_name)
        
        # Emit signal for GUI
        self.game_saved.emit()
    
    def end_turn(self):
        """End the current turn and process AI turns."""
        # Process end of turn for player civilization
        self.process_end_of_turn(self.game_state.player_civ)
        
        # Process AI turns
        for civ in self.game_state.civilizations:
            if civ != self.game_state.player_civ:
                self.process_ai_turn(civ)
        
        # Increment turn counter
        self.game_state.current_turn += 1
        
        # Process start of turn for all civilizations
        for civ in self.game_state.civilizations:
            self.process_start_of_turn(civ)
        
        # Emit signal for GUI
        self.turn_ended.emit()
    
    def process_end_of_turn(self, civ):
        """
        Process end of turn for a civilization.
        
        Args:
            civ: The civilization to process.
        """
        # Process cities
        for city in civ.cities:
            self.city_controller.process_end_of_turn(city)
        
        # Process units
        for unit in civ.units:
            self.unit_controller.process_end_of_turn(unit)
        
        # Process research
        self.civ_controller.process_research(civ)
    
    def process_start_of_turn(self, civ):
        """
        Process start of turn for a civilization.
        
        Args:
            civ: The civilization to process.
        """
        # Reset movement points for units
        for unit in civ.units:
            self.unit_controller.reset_movement(unit)
        
        # Process city production
        for city in civ.cities:
            self.city_controller.process_production(city)
    
    def process_ai_turn(self, civ):
        """
        Process AI turn for a civilization.
        
        Args:
            civ: The AI civilization to process.
        """
        # Process end of turn
        self.process_end_of_turn(civ)
        
        # AI decision making
        self.civ_controller.process_ai_turn(civ)
        
        # Process start of turn
        self.process_start_of_turn(civ)
    
    def perform_unit_action(self, unit, action):
        """
        Perform an action with a unit.
        
        Args:
            unit: The unit to perform the action.
            action (dict): The action to perform.
        
        Returns:
            dict: Result of the action.
        """
        return self.unit_controller.perform_action(unit, action)
    
    def perform_city_action(self, city, action):
        """
        Perform an action with a city.
        
        Args:
            city: The city to perform the action.
            action (dict): The action to perform.
        
        Returns:
            dict: Result of the action.
        """
        return self.city_controller.perform_action(city, action)
    
    def research_technology(self, tech_id):
        """
        Start researching a technology.
        
        Args:
            tech_id (str): ID of the technology to research.
        
        Returns:
            dict: Result of the action.
        """
        return self.civ_controller.start_research(self.game_state.player_civ, tech_id)
    
    def perform_diplomatic_action(self, action):
        """
        Perform a diplomatic action.
        
        Args:
            action (dict): The diplomatic action to perform.
        
        Returns:
            dict: Result of the action.
        """
        return self.civ_controller.perform_diplomatic_action(action)
    
    def check_victory_conditions(self):
        """
        Check if any victory conditions have been met.
        
        Returns:
            dict: Victory status.
        """
        return self.civ_controller.check_victory_conditions()
    
    def get_tech_tree(self):
        """
        Get the technology tree.
        
        Returns:
            dict: Technology tree data.
        """
        return self.data_loader.load_tech_tree()
    
    def get_building_data(self):
        """
        Get building data.
        
        Returns:
            dict: Building data.
        """
        return self.data_loader.load_buildings()
    
    def get_unit_data(self):
        """
        Get unit data.
        
        Returns:
            dict: Unit data.
        """
        return self.data_loader.load_units()
    
    def get_world(self):
        """
        Get the game world.
        
        Returns:
            World: The game world.
        """
        return self.game_state.world if self.game_state else None
    
    def get_game_state(self):
        """
        Get the current game state.
        
        Returns:
            GameState: The current game state.
        """
        return self.game_state
    
    def get_current_civilization(self):
        """
        Get the current player civilization.
        
        Returns:
            Civilization: The player civilization.
        """
        return self.game_state.player_civ if self.game_state else None
    
    def get_all_units(self):
        """
        Get all units in the game.
        
        Returns:
            list: All units.
        """
        if not self.game_state:
            return []
        
        all_units = []
        for civ in self.game_state.civilizations:
            all_units.extend(civ.units)
        
        return all_units
    
    def get_all_cities(self):
        """
        Get all cities in the game.
        
        Returns:
            list: All cities.
        """
        if not self.game_state:
            return []
        
        all_cities = []
        for civ in self.game_state.civilizations:
            all_cities.extend(civ.cities)
        
        return all_cities
