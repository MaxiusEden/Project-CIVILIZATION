# game/models/game_state.py
from game.models.world import World
from game.models.civilization import Civilization
from game.models.city import City
from game.models.unit import Unit
from game.utils.data_loader import DataLoader
from game.utils.logger import get_game_logger
import random
import uuid

class GameState:
    """
    Representa o estado completo do jogo.
    """
    def __init__(self, config=None, from_dict_data=None):
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
        self._data_loader = None
        self._terrain_data = None
        self._resource_data = None
        self._unit_data = None
        self._building_data = None
        self._tech_tree = None
        self.logger = get_game_logger(self.__class__.__name__)
        if from_dict_data:
            self.from_dict(from_dict_data)

    @property
    def data_loader(self):
        if self._data_loader is None:
            self._data_loader = DataLoader()
        return self._data_loader

    @property
    def terrain_data(self):
        if self._terrain_data is None:
            self._terrain_data = self.data_loader.get_terrains()
        return self._terrain_data

    @property
    def resource_data(self):
        if self._resource_data is None:
            self._resource_data = self.data_loader.get_resources()
        return self._resource_data

    @property
    def unit_data(self):
        if self._unit_data is None:
            self._unit_data = self.data_loader.get_units()
        return self._unit_data

    @property
    def building_data(self):
        if self._building_data is None:
            self._building_data = self.data_loader.get_buildings()
        return self._building_data

    @property
    def tech_tree(self):
        if self._tech_tree is None:
            self._tech_tree = self.data_loader.get_tech_tree()
        return self._tech_tree

    def to_dict(self):
        return {
            'id': self.id,
            'config': self.config,
            'current_turn': self.current_turn,
            'world': self.world.to_dict() if self.world else None,
            'civilizations': [civ.to_dict() for civ in self.civilizations],
            'player_civ': self.player_civ.to_dict() if self.player_civ else None,
            'current_civ_index': self.current_civ_index,
            'game_over': self.game_over,
            'winner': self.winner,
        }

    def from_dict(self, data):
        self.id = data.get('id', self.id)
        self.config = data.get('config', {})
        self.current_turn = data.get('current_turn', 0)
        # Para world, civilizations, player_civ, winner, é necessário garantir que os modelos implementem from_dict
        if data.get('world'):
            from game.models.world import World
            self.world = World.from_dict(data['world'])
        if data.get('civilizations'):
            from game.models.civilization import Civilization
            self.civilizations = [Civilization.from_dict(c) for c in data['civilizations']]
        if data.get('player_civ'):
            from game.models.civilization import Civilization
            self.player_civ = Civilization.from_dict(data['player_civ'])
        self.current_civ_index = data.get('current_civ_index', 0)
        self.game_over = data.get('game_over', False)
        self.winner = data.get('winner')
