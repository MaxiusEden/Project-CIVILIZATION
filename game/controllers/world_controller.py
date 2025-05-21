# game/controllers/world_controller.py
import logging
import random
from game.models.game_state import GameState

class WorldController:
    """
    Controlador do mundo do jogo.
    
    Gerencia operações relacionadas ao mundo, como navegação, visualização e interação com tiles.
    """
    
    def __init__(self, game_state):
        """
        Inicializa o controlador do mundo.
        
        Args:
            game_state: Estado do jogo, contendo informações sobre o mundo e civilizações.
        """
        self.game_state = game_state
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def world(self):
        """Obtém o mundo do jogo."""
        return self.game_state.world if self.game_state else None
    
    def get_tile(self, x, y):
        """
        Obtém um tile nas coordenadas especificadas.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            
        Returns:
            Tile: Tile nas coordenadas especificadas, ou None se as coordenadas forem inválidas.
        """
        if self.world:
            return self.world.get_tile(x, y)
        return None
    
    def get_visible_tiles(self, civilization):
        """
        Obtém os tiles visíveis para uma civilização.
        
        Args:
            civilization: Civilização.
            
        Returns:
            list: Lista de tiles visíveis.
        """
        if not self.world:
            return []
        
        # Implementação básica: tiles visíveis são aqueles próximos a unidades e cidades
        visible_tiles = set()
        
        # Adiciona tiles próximos a cidades
        for city in civilization.cities:
            city_tile = self.world.get_tile(city.x, city.y)
            if city_tile:
                visible_tiles.add(city_tile)
                
                # Adiciona tiles em um raio de 2 da cidade
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        neighbor = self.world.get_tile(city.x + dx, city.y + dy)
                        if neighbor:
                            visible_tiles.add(neighbor)
        
        # Adiciona tiles próximos a unidades
        for unit in civilization.units:
            unit_tile = self.world.get_tile(unit.x, unit.y)
            if unit_tile:
                visible_tiles.add(unit_tile)
                
                # Adiciona tiles em um raio de 1 da unidade
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        neighbor = self.world.get_tile(unit.x + dx, unit.y + dy)
                        if neighbor:
                            visible_tiles.add(neighbor)
        
        return list(visible_tiles)
    
    def get_tile_info(self, x, y):
        """
        Obtém informações detalhadas sobre um tile.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            
        Returns:
            dict: Informações sobre o tile, ou None se as coordenadas forem inválidas.
        """
        tile = self.get_tile(x, y)
        if not tile:
            return None
        
        # Obtém informações básicas do tile
        info = {
            'x': tile.x,
            'y': tile.y,
            'terrain': tile.terrain_type,
            'resource': tile.resource,
            'improvement': tile.improvement,
            'owner': tile.owner.name if tile.owner else None,
            'units': [],
            'city': None
        }
        
        # Adiciona informações sobre unidades no tile
        for unit in tile.units:
            unit_info = {
                'id': unit.id,
                'type': unit.type,
                'owner': unit.owner.name if unit.owner else None,
                'health': unit.health,
                'moves_left': unit.moves_left
            }
            info['units'].append(unit_info)
        
        # Adiciona informações sobre a cidade no tile, se houver
        if tile.city:
            info['city'] = {
                'id': tile.city.id,
                'name': tile.city.name,
                'owner': tile.city.owner.name if tile.city.owner else None,
                'population': tile.city.population,
                'health': tile.city.health
            }
        
        return info
    
    def get_path(self, start_x, start_y, end_x, end_y, unit=None):
        """
        Encontra um caminho entre dois pontos.
        
        Args:
            start_x (int): Coordenada X inicial.
            start_y (int): Coordenada Y inicial.
            end_x (int): Coordenada X final.
            end_y (int): Coordenada Y final.
            unit (Unit): Unidade que vai percorrer o caminho (opcional).
            
        Returns:
            list: Lista de coordenadas (x, y) representando o caminho, ou None se não houver caminho.
        """
        if not self.world:
            return None
        
        # Implementação básica: caminho em linha reta
        # TODO: Implementar algoritmo de pathfinding (A*)
        path = []
        
        # Calcula a direção
        dx = 1 if end_x > start_x else (-1 if end_x < start_x else 0)
        dy = 1 if end_y > start_y else (-1 if end_y < start_y else 0)
        
        x, y = start_x, start_y
        
        # Gera o caminho
        while x != end_x or y != end_y:
            # Prioriza movimento na direção com maior distância
            if abs(end_x - x) > abs(end_y - y):
                x += dx
            else:
                y += dy
            
            # Verifica se o tile é válido
            tile = self.world.get_tile(x, y)
            if not tile:
                return None
            
            # Verifica se a unidade pode mover para o tile
            if unit and not unit.can_move_to(tile, self.game_state.terrain_data):
                return None
            
            path.append((x, y))
        
        return path
    
    def generate_world(self, world_type="continents"):
        """
        Gera o mundo do jogo de acordo com o tipo especificado.
        
        Args:
            world_type (str): Tipo de mundo (ex: 'continents', 'pangea', etc.)
        """
        terrain_types = ["plains", "hills", "mountains", "forest", "desert", "water"]
        world = self.world
        if not world:
            return

        for x in range(world.width):
            for y in range(world.height):
                terrain = random.choice(terrain_types)
                tile = world.get_tile(x, y)
                if tile:
                    tile.terrain_type = terrain
                    tile.resource = None
                    tile.improvement = None

    def new_game(self, world_type="continents"):
        # Crie o novo estado do jogo
        self.game_state = GameState()
        # Agora crie o WorldController com o novo game_state
        self.world_controller = WorldController(self.game_state)
        # Agora pode gerar o mundo
        self.world_controller.generate_world(world_type)
        # ... continue com o restante da inicialização ...
