# game/models/civilization.py
from game.models.base_model import BaseModel
import logging
import random

class Civilization(BaseModel):
    """
    Representa uma civilização no jogo.
    
    Uma civilização é controlada por um jogador ou pela IA e possui
    cidades, unidades, tecnologias e recursos.
    """
    
    def __init__(self, name, leader_name, color="#FFFFFF", is_ai=False):
        """
        Inicializa uma nova civilização.
        
        Args:
            name (str): Nome da civilização.
            leader_name (str): Nome do líder.
            color (str): Cor da civilização em formato hexadecimal.
            is_ai (bool): Se True, esta civilização é controlada pela IA.
        """
        super().__init__()
        self.name = name
        self.leader_name = leader_name
        self.color = color
        self.is_ai = is_ai
        
        # Recursos
        self.gold = 0
        self.science = 0
        self.culture = 0
        self.happiness = 0
        
        # Coleções
        self.cities = []
        self.units = []
        self.technologies = []
        self.researching = None  # Tecnologia em pesquisa
        
        # Relações diplomáticas
        self.known_civs = []
        self.relations = {}  # {civ_id: relation_value}
        
        # Estatísticas
        self.score = 0
        self.turn_founded = 0
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{name}")
    
    def add_city(self, city):
        """
        Adiciona uma cidade à civilização.
        
        Args:
            city: Cidade a ser adicionada.
        """
        if city not in self.cities:
            self.cities.append(city)
            city.owner = self
            self.logger.info(f"Cidade {city.name} fundada")
    
    def remove_city(self, city):
        """
        Remove uma cidade da civilização.
        
        Args:
            city: Cidade a ser removida.
        """
        if city in self.cities:
            self.cities.remove(city)
            self.logger.info(f"Cidade {city.name} perdida")
    
    def add_unit(self, unit):
        """
        Adiciona uma unidade à civilização.
        
        Args:
            unit: Unidade a ser adicionada.
        """
        if unit not in self.units:
            self.units.append(unit)
            unit.owner = self
    
    def remove_unit(self, unit):
        """
        Remove uma unidade da civilização.
        
        Args:
            unit: Unidade a ser removida.
        """
        if unit in self.units:
            self.units.remove(unit)
    
    def has_technology(self, tech_id):
        """
        Verifica se a civilização possui uma tecnologia.
        
        Args:
            tech_id (str): ID da tecnologia.
            
        Returns:
            bool: True se a civilização possui a tecnologia, False caso contrário.
        """
        return tech_id in self.technologies
    
    def can_research(self, tech_id, tech_tree):
        """
        Verifica se a civilização pode pesquisar uma tecnologia.
        
        Args:
            tech_id (str): ID da tecnologia.
            tech_tree (dict): Árvore tecnológica.
            
        Returns:
            bool: True se a civilização pode pesquisar a tecnologia, False caso contrário.
        """
        # Verifica se a tecnologia já foi pesquisada
        if self.has_technology(tech_id):
            return False
        
        # Verifica se a tecnologia existe
        if tech_id not in tech_tree:
            return False
        
        # Verifica se todos os pré-requisitos foram atendidos
        tech = tech_tree[tech_id]
        for prereq in tech.get('prerequisites', []):
            if not self.has_technology(prereq):
                return False
        
        return True
    
    def start_research(self, tech_id, tech_tree):
        """
        Inicia a pesquisa de uma tecnologia.
        
        Args:
            tech_id (str): ID da tecnologia.
            tech_tree (dict): Árvore tecnológica.
            
        Returns:
            bool: True se a pesquisa foi iniciada, False caso contrário.
        """
        if not self.can_research(tech_id, tech_tree):
            return False
        
        self.researching = {
            'id': tech_id,
            'progress': 0,
            'cost': tech_tree[tech_id]['cost']
        }
        
        self.logger.info(f"Iniciando pesquisa de {tech_tree[tech_id]['name']}")
        return True
    
    def update_research(self):
        """
        Atualiza o progresso da pesquisa atual.
        
        Returns:
            bool: True se uma tecnologia foi concluída, False caso contrário.
        """
        if not self.researching:
            return False
        
        # Adiciona ciência ao progresso
        self.researching['progress'] += self.science
        
        # Verifica se a pesquisa foi concluída
        if self.researching['progress'] >= self.researching['cost']:
            tech_id = self.researching['id']
            self.technologies.append(tech_id)
            self.researching = None
            self.logger.info(f"Tecnologia {tech_id} concluída")
            return True
        
        return False
    
    def calculate_income(self):
        """
        Calcula a renda total da civilização.
        
        Returns:
            dict: Renda por tipo (gold, science, culture).
        """
        income = {
            'gold': 0,
            'science': 0,
            'culture': 0
        }
        
        # Renda base
        income['gold'] += 1
        
        # Renda das cidades
        for city in self.cities:
            city_income = city.calculate_income()
            for resource_type, amount in city_income.items():
                if resource_type in income:
                    income[resource_type] += amount
        
        return income
    
    def update_resources(self):
        """Atualiza os recursos da civilização com base na renda."""
        income = self.calculate_income()
        
        # Atualiza os recursos
        self.gold += income['gold']
        self.science = income['science']  # Science é produzida por turno, não acumulada
        self.culture += income['culture']
        
        # Atualiza a felicidade
        self.update_happiness()
    
    def update_happiness(self):
        """Atualiza a felicidade da civilização."""
        # Felicidade base
        happiness = 0
        
        # Cada cidade reduz a felicidade
        happiness -= len(self.cities)
        
        # Cada população reduz a felicidade
        for city in self.cities:
            happiness -= city.population // 2
        
        # TODO: Adicionar efeitos de edifícios, recursos de luxo, etc.
        
        self.happiness = happiness
    
    def calculate_score(self, current_turn):
        """
        Calcula a pontuação da civilização.
        
        Args:
            current_turn (int): Turno atual.
            
        Returns:
            int: Pontuação da civilização.
        """
        score = 0
        
        # Pontos por território (número de cidades)
        score += len(self.cities) * 10
        
        # Pontos por população
        population = sum(city.population for city in self.cities)
        score += population * 2
        
        # Pontos por tecnologias
        score += len(self.technologies) * 5
        
        # Pontos por maravilhas
        # TODO: Implementar maravilhas
        
        # Pontos por ouro
        score += self.gold // 10
        
        # Bônus por longevidade
        turns_existed = current_turn - self.turn_founded
        score += turns_existed // 10
        
        self.score = score
        return score
    
    def process_turn(self, game_state):
        """
        Processa o turno da civilização.
        
        Args:
            game_state: Estado atual do jogo.
            
        Returns:
            dict: Ações realizadas durante o turno.
        """
        actions = {
            'cities_founded': 0,
            'units_created': 0,
            'technologies_completed': 0,
            'battles_fought': 0
        }
        
        # Atualiza recursos
        self.update_resources()
        
        # Atualiza pesquisa
        if self.update_research():
            actions['technologies_completed'] += 1
        
        # Processa cidades
        for city in self.cities:
            city_actions = city.process_turn()
            
            if city_actions.get('unit_created'):
                actions['units_created'] += 1
        
        # Se for IA, processa ações de IA
        if self.is_ai:
            ai_actions = self._process_ai_turn(game_state)
            for key, value in ai_actions.items():
                if key in actions:
                    actions[key] += value
        
        # Calcula pontuação
        self.calculate_score(game_state.current_turn)
        
        return actions
    
    def _process_ai_turn(self, game_state):
        """
        Processa o turno da IA.
        
        Args:
            game_state: Estado atual do jogo.
            
        Returns:
            dict: Ações realizadas pela IA.
        """
        actions = {
            'cities_founded': 0,
            'units_created': 0,
            'technologies_completed': 0,
            'battles_fought': 0
        }
        
        # Implementação básica de IA
        # TODO: Implementar IA mais sofisticada
        
        # Pesquisa tecnologia aleatória disponível
        if not self.researching:
            available_techs = [
                tech_id for tech_id in game_state.tech_tree
                if self.can_research(tech_id, game_state.tech_tree)
            ]
            
            if available_techs:
                tech_id = random.choice(available_techs)
                self.start_research(tech_id, game_state.tech_tree)
        
        # Move unidades aleatoriamente
        for unit in self.units:
            if unit.can_move():
                # Obtém tiles vizinhos válidos
                current_tile = game_state.world.get_tile(unit.x, unit.y)
                neighbors = game_state.world.get_neighbors(unit.x, unit.y)
                
                # Filtra tiles que a unidade pode mover
                valid_neighbors = [
                    tile for tile in neighbors
                    if unit.can_move_to(tile, game_state.terrain_data)
                ]
                
                if valid_neighbors:
                    # Move para um tile aleatório
                    target_tile = random.choice(valid_neighbors)
                    unit.move_to(target_tile.x, target_tile.y)
        
        # Tenta fundar novas cidades com colonizadores
        for unit in self.units:
            if unit.type == 'settler' and unit.can_act():
                # Verifica se o local é adequado para uma cidade
                current_tile = game_state.world.get_tile(unit.x, unit.y)
                
                # Critérios simples: não muito perto de outras cidades
                too_close = False
                for city in self.cities:
                    city_tile = game_state.world.get_tile(city.x, city.y)
                    distance = abs(city_tile.x - current_tile.x) + abs(city_tile.y - current_tile.y)
                    if distance < 4:  # Distância mínima entre cidades
                        too_close = True
                        break
                
                if not too_close and current_tile.terrain_type != 'water':
                    # Funda uma cidade
                    from game.models.city import City
                    city_name = f"{self.name} {len(self.cities) + 1}"
                    city = City(current_tile.x, current_tile.y, city_name)
                    self.add_city(city)
                    
                    # Remove o colonizador
                    self.remove_unit(unit)
                    current_tile.remove_unit(unit)
                    
                    actions['cities_founded'] += 1
        
        return actions
    
    def to_dict(self):
        """
        Converte a civilização para um dicionário para serialização.
        
        Returns:
            dict: Representação da civilização como dicionário.
        """
        data = super().to_dict()
        data.update({
            'name': self.name,
            'leader_name': self.leader_name,
            'color': self.color,
            'is_ai': self.is_ai,
            'gold': self.gold,
            'science': self.science,
            'culture': self.culture,
            'happiness': self.happiness,
            'cities': [city.id for city in self.cities],
            'units': [unit.id for unit in self.units],
            'technologies': self.technologies.copy(),
            'researching': self.researching.copy() if self.researching else None,
            'known_civs': self.known_civs.copy(),
            'relations': self.relations.copy(),
            'score': self.score,
            'turn_founded': self.turn_founded
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria uma instância da civilização a partir de um dicionário.
        
        Args:
            data (dict): Dicionário contendo os dados da civilização.
            
        Returns:
            Civilization: Nova instância da civilização.
        """
        civ = super().from_dict(data)
        civ.name = data.get('name', 'Unknown')
        civ.leader_name = data.get('leader_name', 'Unknown')
        civ.color = data.get('color', '#FFFFFF')
        civ.is_ai = data.get('is_ai', False)
        
        civ.gold = data.get('gold', 0)
        civ.science = data.get('science', 0)
        civ.culture = data.get('culture', 0)
        civ.happiness = data.get('happiness', 0)
        
        # Referências a outros objetos serão resolvidas posteriormente
        civ._city_ids = data.get('cities', [])
        civ._unit_ids = data.get('units', [])
        
        civ.technologies = data.get('technologies', [])
        civ.researching = data.get('researching')
        civ.known_civs = data.get('known_civs', [])
        civ.relations = data.get('relations', {})
        civ.score = data.get('score', 0)
        civ.turn_founded = data.get('turn_founded', 0)
        
        return civ
