# game/models/city.py
from game.models.base_model import BaseModel
import logging
import random

class City(BaseModel):
    """
    Representa uma cidade no jogo.
    
    Uma cidade pertence a uma civilização, ocupa um tile no mapa,
    e produz recursos, unidades e edifícios.
    """
    
    def __init__(self, x, y, name):
        """
        Inicializa uma nova cidade.
        
        Args:
            x (int): Coordenada X da cidade.
            y (int): Coordenada Y da cidade.
            name (str): Nome da cidade.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.name = name
        self.owner = None  # Referência à civilização proprietária
        
        # Atributos da cidade
        self.population = 1
        self.health = 100
        self.food = 0
        self.food_needed = 10  # Comida necessária para crescer
        self.production = 0
        
        # Produção atual
        self.producing = None  # {type: 'unit'|'building', id: '...', progress: 0, cost: 0}
        
        # Edifícios construídos
        self.buildings = []
        
        # Tiles trabalhados pela cidade
        self.worked_tiles = []
        
        # Estatísticas
        self.founded_turn = 0
        self.last_growth_turn = 0
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{name}")
    
    def calculate_income(self):
        """
        Calcula a renda total da cidade.
        
        Returns:
            dict: Renda por tipo (food, production, gold, science, culture).
        """
        income = {
            'food': 0,
            'production': 0,
            'gold': 0,
            'science': 0,
            'culture': 0
        }
        
        # Renda base da cidade
        income['food'] += 2
        income['production'] += 1
        
        # Renda por população
        income['science'] += self.population
        
        # TODO: Adicionar renda de tiles trabalhados
        
        # Renda de edifícios
        # TODO: Implementar efeitos de edifícios
        
        return income
    
    def process_turn(self):
        """
        Processa o turno da cidade.
        
        Returns:
            dict: Ações realizadas durante o turno.
        """
        actions = {
            'population_growth': False,
            'building_completed': None,
            'unit_created': None
        }
        
        # Calcula renda
        income = self.calculate_income()
        
        # Processa comida e crescimento populacional
        self.food += income['food']
        
        if self.food >= self.food_needed:
            self.food -= self.food_needed
            self.population += 1
            self.food_needed = 10 + (self.population * 5)  # Aumenta comida necessária
            actions['population_growth'] = True
            self.logger.info(f"População cresceu para {self.population}")
        
        # Processa produção
        if self.producing:
            self.production += income['production']
            self.producing['progress'] += income['production']
            
            if self.producing['progress'] >= self.producing['cost']:
                # Produção concluída
                if self.producing['type'] == 'building':
                    building_id = self.producing['id']
                    self.buildings.append(building_id)
                    actions['building_completed'] = building_id
                    self.logger.info(f"Edifício {building_id} concluído")
                
                elif self.producing['type'] == 'unit':
                    # Cria a unidade
                    from game.models.unit import Unit
                    unit_id = self.producing['id']
                    unit = Unit(self.x, self.y, unit_id)
                    
                    if self.owner:
                        self.owner.add_unit(unit)
                        
                        # Adiciona a unidade ao tile
                        if self.owner.game_state:
                            tile = self.owner.game_state.world.get_tile(self.x, self.y)
                            if tile:
                                tile.add_unit(unit)
                    
                    actions['unit_created'] = unit
                    self.logger.info(f"Unidade {unit_id} criada")
                
                # Reseta produção
                self.producing = None
                self.production = 0
        
        return actions
    
    def start_production(self, production_type, item_id, cost):
        """
        Inicia a produção de um item.
        
        Args:
            production_type (str): Tipo de produção ('unit' ou 'building').
            item_id (str): ID do item a ser produzido.
            cost (int): Custo de produção do item.
            
        Returns:
            bool: True se a produção foi iniciada, False caso contrário.
        """
        if self.producing:
            return False
        
        self.producing = {
            'type': production_type,
            'id': item_id,
            'progress': self.production,
            'cost': cost
        }
        
        self.logger.info(f"Iniciando produção de {production_type} {item_id}")
        return True
    
    def can_build(self, building_id, building_data):
        """
        Verifica se a cidade pode construir um edifício.
        
        Args:
            building_id (str): ID do edifício.
            building_data (dict): Dados de edifícios do jogo.
            
        Returns:
            bool: True se a cidade pode construir o edifício, False caso contrário.
        """
        # Verifica se o edifício existe
        if building_id not in building_data:
            return False
        
        # Verifica se o edifício já foi construído
        if building_id in self.buildings:
            return False
        
        building = building_data[building_id]
        
        # Verifica pré-requisitos de tecnologia
        if 'requires_tech' in building and self.owner:
            if not self.owner.has_technology(building['requires_tech']):
                return False
        
        # Verifica pré-requisitos de edifícios
        if 'requires_building' in building:
            required_building = building['requires_building']
            if required_building not in self.buildings:
                return False
        
        # Verifica pré-requisitos de população
        if 'requires_population' in building:
            if self.population < building['requires_population']:
                return False
        
        return True
    
    def get_available_buildings(self, building_data):
        """
        Obtém a lista de edifícios disponíveis para construção.
        
        Args:
            building_data (dict): Dados de edifícios do jogo.
            
        Returns:
            list: Lista de IDs de edifícios disponíveis.
        """
        available = []
        
        for building_id in building_data:
            if self.can_build(building_id, building_data):
                available.append(building_id)
        
        return available
    
    def get_available_units(self, unit_data):
        """
        Obtém a lista de unidades disponíveis para produção.
        
        Args:
            unit_data (dict): Dados de unidades do jogo.
            
        Returns:
            list: Lista de IDs de unidades disponíveis.
        """
        available = []
        
        for unit_id, unit_info in unit_data.items():
            # Verifica pré-requisitos de tecnologia
            if 'requires_tech' in unit_info and self.owner:
                if not self.owner.has_technology(unit_info['requires_tech']):
                    continue
            
            # Verifica pré-requisitos de recursos estratégicos
            if 'requires_resource' in unit_info and self.owner:
                # TODO: Implementar verificação de recursos
                pass
            
            available.append(unit_id)
        
        return available
    
    def get_worked_tiles(self, world):
        """
        Obtém a lista de tiles trabalhados pela cidade.
        
        Args:
            world: Mundo do jogo.
            
        Returns:
            list: Lista de tiles trabalhados.
        """
        worked_tiles = []
        
        # Obtém todos os tiles em um raio de 3 do centro da cidade
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                # Calcula a distância Manhattan
                distance = abs(dx) + abs(dy)
                
                # Ignora tiles muito distantes ou o próprio centro
                if distance > 3 or distance == 0:
                    continue
                
                # Obtém o tile
                tile = world.get_tile(self.x + dx, self.y + dy)
                if tile and tile.owner == self.owner:
                    worked_tiles.append(tile)
        
        return worked_tiles
    
    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'name': self.name,
            'owner': self.owner.id if self.owner else None,
            'population': self.population,
            'health': self.health,
            'food': self.food,
            'food_needed': self.food_needed,
            'production': self.production,
            'producing': self.producing,
            'buildings': self.buildings,
            'worked_tiles': self.worked_tiles,
            'founded_turn': self.founded_turn,
            'last_growth_turn': self.last_growth_turn
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'], data['name'])
        obj.id = data.get('id', obj.id)
        obj.population = data.get('population', 1)
        obj.health = data.get('health', 100)
        obj.food = data.get('food', 0)
        obj.food_needed = data.get('food_needed', 10)
        obj.production = data.get('production', 0)
        obj.producing = data.get('producing')
        obj.buildings = data.get('buildings', [])
        obj.worked_tiles = data.get('worked_tiles', [])
        obj.founded_turn = data.get('founded_turn', 0)
        obj.last_growth_turn = data.get('last_growth_turn', 0)
        return obj
