# game/models/game_state.py
from game.models.world import World
from game.models.civilization import Civilization
from game.models.city import City
from game.models.unit import Unit
from game.utils.data_loader import DataLoader
import logging
import random
import uuid

class GameState:
    """
    Representa o estado completo do jogo.
    
    Contém todas as informações necessárias para representar o estado atual
    do jogo, incluindo o mundo, civilizações, cidades, unidades, etc.
    """
    
    def __init__(self, config=None):
        """
        Inicializa um novo estado de jogo.
        
        Args:
            config (dict): Configurações do jogo.
        """
        self.id = str(uuid.uuid4())
        self.config = config or {}
        self.current_turn = 0
        self.world = None
        self.civilizations = []
        self.player_civ = None
        self.current_civ_index = 0
        self.game_over = False
        self.winner = None
        
        # Carrega dados do jogo
        self.data_loader = DataLoader()
        self.terrain_data = self.data_loader.get_terrains()
        self.resource_data = self.data_loader.get_resources()
        self.unit_data = self.data_loader.get_units()
        self.building_data = self.data_loader.get_buildings()
        self.tech_tree = self.data_loader.get_tech_tree()
        
        self.logger = logging.getLogger(self.__class__.__name__)
