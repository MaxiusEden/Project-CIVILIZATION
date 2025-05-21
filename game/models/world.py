# game/models/world.py
from game.models.base_model import BaseModel
from game.utils.perlin_noise import PerlinNoise
import random
import logging

class Tile(BaseModel):
    """
    Representa um tile (célula) no mapa do mundo.
    
    Cada tile tem um tipo de terreno, possivelmente um recurso,
    e pode conter unidades ou uma cidade.
    """
    
    def __init__(self, x, y, terrain_type="plains", resource=None):
        """
        Inicializa um novo tile.
        
        Args:
            x (int): Coordenada X do tile.
            y (int): Coordenada Y do tile.
            terrain_type (str): Tipo de terreno do tile.
            resource (str): Recurso presente no tile, se houver.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.resource = resource
        self.improvement = None
        self.owner = None  # Civilização que controla este tile
        self.city = None   # Cidade neste tile, se houver
        self.units = []    # Unidades neste tile
        
    def to_dict(self):
        """
        Converte o tile para um dicionário para serialização.
        
        Returns:
            dict: Representação do tile como dicionário.
        """
        data = super().to_dict()
        data.update({
            'x': self.x,
            'y': self.y,
            'terrain_type': self.terrain_type,
            'resource': self.resource,
            'improvement': self.improvement,
            'owner': self.owner.id if self.owner else None,
            'city': self.city.id if self.city else None,
            'units': [unit.id for unit in self.units]
        })
        return data
    
    @classmethod
    def from_dict(cls, data, world=None):
        """
        Cria uma instância do tile a partir de um dicionário.
        
        Args:
            data (dict): Dicionário contendo os dados do tile.
            world (World): Referência ao mundo para resolver referências.
            
        Returns:
            Tile: Nova instância do tile.
        """
        tile = super().from_dict(data)
        tile.x = data.get('x', 0)
        tile.y = data.get('y', 0)
        tile.terrain_type = data.get('terrain_type', 'plains')
        tile.resource = data.get('resource')
        tile.improvement = data.get('improvement')
        
        # Referências a outros objetos serão resolvidas posteriormente
        # quando todas as entidades estiverem carregadas
        tile._owner_id = data.get('owner')
        tile._city_id = data.get('city')
        tile._unit_ids = data.get('units', [])
        
        return tile
    
    def get_movement_cost(self, terrain_data):
        """
        Retorna o custo de movimento para este tile.
        
        Args:
            terrain_data (dict): Dados de terrenos do jogo.
            
        Returns:
            int: Custo de movimento.
        """
        terrain_info = terrain_data.get(self.terrain_type, {})
        return terrain_info.get('movement_cost', 1)
    
    def get_yields(self, terrain_data, resource_data):
        """
        Calcula os rendimentos (food, production, gold) deste tile.
        
        Args:
            terrain_data (dict): Dados de terrenos do jogo.
            resource_data (dict): Dados de recursos do jogo.
            
        Returns:
            dict: Rendimentos do tile (food, production, gold).
        """
        # Rendimentos base do terreno
        terrain_info = terrain_data.get(self.terrain_type, {})
        yields = {
            'food': terrain_info.get('food', 0),
            'production': terrain_info.get('production', 0),
            'gold': terrain_info.get('gold', 0)
        }
        
        # Adiciona rendimentos do recurso, se houver
        if self.resource and self.resource in resource_data:
            resource_info = resource_data[self.resource]
            resource_yields = resource_info.get('yields', {})
            
            for yield_type, value in resource_yields.items():
                if yield_type in yields:
                    yields[yield_type] += value
        
        # TODO: Adicionar rendimentos de melhorias
        
        return yields
    
    def add_unit(self, unit):
        """
        Adiciona uma unidade a este tile.
        
        Args:
            unit: Unidade a ser adicionada.
        """
        if unit not in self.units:
            self.units.append(unit)
    
    def remove_unit(self, unit):
        """
        Remove uma unidade deste tile.
        
        Args:
            unit: Unidade a ser removida.
        """
        if unit in self.units:
            self.units.remove(unit)


class World(BaseModel):
    """
    Representa o mundo do jogo, composto por um grid de tiles.
    """
    
    def __init__(self, width=80, height=40, seed=None):
        """
        Inicializa um novo mundo.
        
        Args:
            width (int): Largura do mundo em tiles.
            height (int): Altura do mundo em tiles.
            seed (int): Semente para geração aleatória. Se None, usa uma semente aleatória.
        """
        super().__init__()
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        self.tiles = []
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Inicializa o grid de tiles vazio
        self._initialize_tiles()
    
    def _initialize_tiles(self):
        """Inicializa o grid de tiles com terreno padrão."""
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(Tile(x, y))
            self.tiles.append(row)
    
    def generate_terrain(self, data_loader):
        """
        Gera o terreno do mundo usando ruído de Perlin.
        
        Args:
            data_loader: Carregador de dados para obter informações de terrenos e recursos.
        """
        self.logger.info(f"Gerando terreno com semente {self.seed}...")
        
        # Carrega dados de terrenos e recursos
        terrain_data = data_loader.get_terrains()
        resource_data = data_loader.get_resources()
        
        # Cria o gerador de ruído
        noise_gen = PerlinNoise(self.seed)
        
        # Gera o mapa de altura
        elevation_map = noise_gen.generate_noise_map(
            self.width, self.height, 
            scale=10.0, octaves=4, 
            persistence=0.5, lacunarity=2.0
        )
        
        # Gera o mapa de umidade
        moisture_map = noise_gen.generate_noise_map(
            self.width, self.height, 
            scale=15.0, octaves=3, 
            persistence=0.4, lacunarity=2.0
        )
        
        # Define os tipos de terreno com base nos mapas de altura e umidade
        for y in range(self.height):
            for x in range(self.width):
                elevation = elevation_map[y][x]
                moisture = moisture_map[y][x]
                
                # Determina o tipo de terreno com base na elevação e umidade
                terrain_type = self._determine_terrain_type(elevation, moisture)
                
                # Atualiza o tile
                self.tiles[y][x].terrain_type = terrain_type
                
                # Chance de gerar um recurso
                if random.random() < 0.1:  # 10% de chance
                    resource = self._determine_resource(terrain_type, resource_data)
                    if resource:
                        self.tiles[y][x].resource = resource
        
        self.logger.info("Geração de terreno concluída.")
    
    def _determine_terrain_type(self, elevation, moisture):
        """
        Determina o tipo de terreno com base na elevação e umidade.
        
        Args:
            elevation (float): Valor de elevação (0-1).
            moisture (float): Valor de umidade (0-1).
            
        Returns:
            str: Tipo de terreno.
        """
        # Água
        if elevation < 0.3:
            return "water"
        
        # Montanhas
        if elevation > 0.8:
            return "mountains"
        
        # Colinas
        if elevation > 0.6:
            return "hills"
        
        # Deserto (baixa umidade)
        if moisture < 0.3:
            return "desert"
        
        # Floresta (alta umidade)
        if moisture > 0.6:
            return "forest"
        
        # Planície (padrão)
        return "plains"
    
    def _determine_resource(self, terrain_type, resource_data):
        """
        Determina um recurso adequado para o tipo de terreno.
        
        Args:
            terrain_type (str): Tipo de terreno.
            resource_data (dict): Dados de recursos.
            
        Returns:
            str: Tipo de recurso ou None.
        """
        # Filtra recursos válidos para este terreno
        valid_resources = []
        for resource_id, resource_info in resource_data.items():
            valid_terrains = resource_info.get('valid_terrains', [])
            if terrain_type in valid_terrains:
                valid_resources.append(resource_id)
        
        # Retorna um recurso aleatório ou None se não houver recursos válidos
        if valid_resources:
            return random.choice(valid_resources)
        return None
    
    def get_tile(self, x, y):
        """
        Obtém o tile nas coordenadas especificadas.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            
        Returns:
            Tile: O tile nas coordenadas especificadas ou None se fora dos limites.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def get_neighbors(self, x, y, include_diagonals=False):
        """
        Obtém os tiles vizinhos ao tile nas coordenadas especificadas.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            include_diagonals (bool): Se True, inclui os vizinhos diagonais.
            
        Returns:
            list: Lista de tiles vizinhos.
        """
        neighbors = []
        
        # Vizinhos ortogonais (norte, leste, sul, oeste)
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        # Adiciona vizinhos diagonais se solicitado
        if include_diagonals:
            directions.extend([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            tile = self.get_tile(nx, ny)
            if tile:
                neighbors.append(tile)
        
        return neighbors
    
    def find_path(self, start_x, start_y, end_x, end_y, movement_cost_fn):
        """
        Encontra o caminho mais curto entre dois pontos usando o algoritmo A*.
        
        Args:
            start_x (int): Coordenada X inicial.
            start_y (int): Coordenada Y inicial.
            end_x (int): Coordenada X final.
            end_y (int): Coordenada Y final.
            movement_cost_fn (callable): Função que retorna o custo de movimento para um tile.
            
        Returns:
            list: Lista de tiles que formam o caminho ou None se não houver caminho.
        """
        import heapq
        
        # Verifica se as coordenadas são válidas
        if not self.get_tile(start_x, start_y) or not self.get_tile(end_x, end_y):
            return None
        
        # Função heurística (distância de Manhattan)
        def heuristic(x, y):
            return abs(x - end_x) + abs(y - end_y)
        
        # Inicializa estruturas de dados
        open_set = []  # Fila de prioridade (custo, x, y)
        closed_set = set()  # Conjunto de nós visitados (x, y)
        g_score = {}  # Custo do caminho do início até (x, y)
        f_score = {}  # Custo estimado do caminho completo
        came_from = {}  # Mapa de nós para seus predecessores
        
        # Adiciona o nó inicial
        heapq.heappush(open_set, (0, start_x, start_y))
        g_score[(start_x, start_y)] = 0
        f_score[(start_x, start_y)] = heuristic(start_x, start_y)
        
        while open_set:
            # Obtém o nó com menor f_score
            _, current_x, current_y = heapq.heappop(open_set)
            current_pos = (current_x, current_y)
            
            # Verifica se chegamos ao destino
            if current_x == end_x and current_y == end_y:
                # Reconstrói o caminho
                path = []
                while current_pos in came_from:
                    x, y = current_pos
                    path.append(self.get_tile(x, y))
                    current_pos = came_from[current_pos]
                
                # Adiciona o nó inicial
                path.append(self.get_tile(start_x, start_y))
                
                # Inverte o caminho (do início para o fim)
                path.reverse()
                return path
            
            # Marca o nó como visitado
            closed_set.add(current_pos)
            
            # Explora os vizinhos
            for neighbor in self.get_neighbors(current_x, current_y):
                neighbor_pos = (neighbor.x, neighbor.y)
                
                # Pula nós já visitados
                if neighbor_pos in closed_set:
                    continue
                
                # Calcula o custo do caminho até o vizinho
                tentative_g_score = g_score[current_pos] + movement_cost_fn(neighbor)
                
                # Verifica se já temos um caminho melhor para este vizinho
                if neighbor_pos in g_score and tentative_g_score >= g_score[neighbor_pos]:
                    continue
                
                # Este é o melhor caminho até agora
                came_from[neighbor_pos] = current_pos
                g_score[neighbor_pos] = tentative_g_score
                f_score[neighbor_pos] = tentative_g_score + heuristic(neighbor.x, neighbor.y)
                
                # Adiciona o vizinho à fila de prioridade
                heapq.heappush(open_set, (f_score[neighbor_pos], neighbor.x, neighbor.y))
        
        # Não encontrou caminho
        return None
    
    def to_dict(self):
        """
        Converte o mundo para um dicionário para serialização.
        
        Returns:
            dict: Representação do mundo como dicionário.
        """
        data = super().to_dict()
        data.update({
            'width': self.width,
            'height': self.height,
            'seed': self.seed,
            'tiles': [[tile.to_dict() for tile in row] for row in self.tiles]
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria uma instância do mundo a partir de um dicionário.
        
        Args:
            data (dict): Dicionário contendo os dados do mundo.
            
        Returns:
            World: Nova instância do mundo.
        """
        world = super().from_dict(data)
        world.width = data.get('width', 80)
        world.height = data.get('height', 40)
        world.seed = data.get('seed', 0)
        
        # Inicializa o grid de tiles vazio
        world._initialize_tiles()
        
        # Carrega os tiles
        tiles_data = data.get('tiles', [])
        for y, row_data in enumerate(tiles_data):
            if y >= world.height:
                break
                
            for x, tile_data in enumerate(row_data):
                if x >= world.width:
                    break
                    
                world.tiles[y][x] = Tile.from_dict(tile_data, world)
        
        return world
