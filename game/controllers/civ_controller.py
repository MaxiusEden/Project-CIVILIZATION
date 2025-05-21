# game/controllers/civ_controller.py
import logging

class CivController:
    """
    Controlador de civilizações.
    
    Gerencia operações relacionadas a civilizações, como diplomacia, pesquisa e economia.
    """
    
    def __init__(self, game_controller):
        """
        Inicializa o controlador de civilizações.
        
        Args:
            game_controller: Controlador principal do jogo.
        """
        self.game_controller = game_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def game_state(self):
        """Obtém o estado atual do jogo."""
        return self.game_controller.game_state
    
    def get_player_civilization(self):
        """
        Obtém a civilização do jogador.
        
        Returns:
            Civilization: Civilização do jogador, ou None se não houver jogo ativo.
        """
        if not self.game_state:
            return None
        
        return self.game_state.player_civ
    
    def get_civilization_by_id(self, civ_id):
        """
        Obtém uma civilização pelo ID.
        
        Args:
            civ_id (str): ID da civilização.
            
        Returns:
            Civilization: Civilização com o ID especificado, ou None se não for encontrada.
        """
        if not self.game_state:
            return None
        
        for civ in self.game_state.civilizations:
            if civ.id == civ_id:
                return civ
        
        return None
    
    def get_civilization_info(self, civilization):
        """
        Obtém informações detalhadas sobre uma civilização.
        
        Args:
            civilization: Civilização.
            
        Returns:
            dict: Informações sobre a civilização.
        """
        if not civilization:
            return None
        
        # Obtém informações básicas da civilização
        info = {
            'id': civilization.id,
            'name': civilization.name,
            'leader': civilization.leader_name,
            'color': civilization.color,
            'is_ai': civilization.is_ai,
            'gold': civilization.gold,
            'science': civilization.science,
            'culture': civilization.culture,
            'happiness': civilization.happiness,
            'score': civilization.score,
            'cities': [],
            'units': [],
            'technologies': civilization.technologies,
            'researching': civilization.researching,
            'relations': civilization.relations
        }
        
        # Adiciona informações sobre cidades
        for city in civilization.cities:
            city_info = {
                'id': city.id,
                'name': city.name,
                'x': city.x,
                'y': city.y,
                'population': city.population,
                'health': city.health
            }
            info['cities'].append(city_info)
        
        # Adiciona informações sobre unidades
        for unit in civilization.units:
            unit_info = {
                'id': unit.id,
                'type': unit.type,
                'x': unit.x,
                'y': unit.y,
                'health': unit.health,
                'moves_left': unit.moves_left
            }
            info['units'].append(unit_info)
        
        return info
    
    def start_research(self, civilization, tech_id):
        """
        Inicia a pesquisa de uma tecnologia.
        
        Args:
            civilization: Civilização.
            tech_id (str): ID da tecnologia.
            
        Returns:
            bool: True se a pesquisa foi iniciada com sucesso, False caso contrário.
        """
        if not civilization:
            return False
        
        # Verifica se a tecnologia existe
        tech_data = self.game_state.tech_tree.get(tech_id)
        if not tech_data:
            self.logger.error(f"Tecnologia não encontrada: {tech_id}")
            return False
        
        # Verifica se a tecnologia já foi pesquisada
        if tech_id in civilization.technologies:
            self.logger.warning(f"Tecnologia já pesquisada: {tech_id}")
            return False
        
        # Verifica pré-requisitos
        prerequisites = tech_data.get('requires', [])
        for prereq in prerequisites:
            if prereq not in civilization.technologies:
                self.logger.warning(f"Pré-requisito não atendido: {prereq}")
                return False
        
        # Inicia a pesquisa
        civilization.researching = {
            'tech_id': tech_id,
            'progress': 0,
            'cost': tech_data.get('cost', 100)
        }
        
        self.logger.info(f"{civilization.name} iniciou pesquisa de {tech_id}")
        return True
    
    def get_available_technologies(self, civilization):
        """
        Obtém as tecnologias disponíveis para pesquisa.
        
        Args:
            civilization: Civilização.
            
        Returns:
            list: Lista de IDs de tecnologias disponíveis.
        """
        if not civilization:
            return []
        
        available = []
        
        for tech_id, tech_data in self.game_state.tech_tree.items():
            # Ignora tecnologias já pesquisadas
            if tech_id in civilization.technologies:
                continue
            
            # Verifica pré-requisitos
            prerequisites = tech_data.get('requires', [])
            all_prereqs_met = True
            
            for prereq in prerequisites:
                if prereq not in civilization.technologies:
                    all_prereqs_met = False
                    break
            
            if all_prereqs_met:
                available.append(tech_id)
        
        return available
    
    def declare_war(self, civilization, target_civ):
        """
        Declara guerra a outra civilização.
        
        Args:
            civilization: Civilização que declara guerra.
            target_civ: Civilização alvo.
            
        Returns:
            bool: True se a guerra foi declarada com sucesso, False caso contrário.
        """
        if not civilization or not target_civ:
            return False
        
        # Verifica se já estão em guerra
        if civilization.relations.get(target_civ.id, 'neutral') == 'war':
            self.logger.warning(f"{civilization.name} já está em guerra com {target_civ.name}")
            return False
        
        # Declara guerra
        civilization.relations[target_civ.id] = 'war'
        target_civ.relations[civilization.id] = 'war'
        
        self.logger.info(f"{civilization.name} declarou guerra a {target_civ.name}")
        return True
    
    def make_peace(self, civilization, target_civ):
        """
        Faz paz com outra civilização.
        
        Args:
            civilization: Civilização que propõe paz.
            target_civ: Civilização alvo.
            
        Returns:
            bool: True se a paz foi estabelecida com sucesso, False caso contrário.
        """
        if not civilization or not target_civ:
            return False
        
        # Verifica se estão em guerra
        if civilization.relations.get(target_civ.id, 'neutral') != 'war':
            self.logger.warning(f"{civilization.name} não está em guerra com {target_civ.name}")
            return False
        
        # Estabelece paz
        civilization.relations[target_civ.id] = 'peace'
        target_civ.relations[civilization.id] = 'peace'
        
        self.logger.info(f"{civilization.name} fez paz com {target_civ.name}")
        return True
    
    def create_civilizations(self, num_civs, player_civ_id):
        """
        Cria as civilizações do jogo, incluindo o jogador e as AIs.
        """
        from game.models.civilization import Civilization

        self.game_state.civilizations = []
        for i in range(num_civs):
            if i == 0:
                civ_name = f"Civilização {i+1}"
                leader_name = "Jogador"
                is_ai = False
            else:
                civ_name = f"Civilização {i+1}"
                leader_name = f"Líder AI {i}"
                is_ai = True
            civ = Civilization(name=civ_name, leader_name=leader_name, is_ai=is_ai)
            # Se quiser sobrescrever o id gerado automaticamente:
            if i == 0:
                civ.id = player_civ_id
            else:
                civ.id = f"ai_{i}"
            self.game_state.civilizations.append(civ)
    
    def place_initial_units(self):
        """
        Posiciona unidades iniciais para cada civilização no início do jogo.
        """
        from game.models.unit import Unit

        for i, civ in enumerate(self.game_state.civilizations):
            x = 2 + i * 2
            y = 2 + i * 2
            unit = Unit(x=x, y=y, unit_type="settler")
            unit.owner = civ
            civ.units.append(unit)
            self.game_state.world.get_tile(x, y).units.append(unit)
