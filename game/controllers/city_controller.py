# game/controllers/city_controller.py
import logging

class CityController:
    """
    Controlador de cidades.
    
    Gerencia operações relacionadas a cidades, como construção, crescimento e produção.
    """
    
    def __init__(self, game_controller):
        """
        Inicializa o controlador de cidades.
        
        Args:
            game_controller: Controlador principal do jogo.
        """
        self.game_controller = game_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def game_state(self):
        """Obtém o estado atual do jogo."""
        return self.game_controller.game_state
    
    def get_city_by_id(self, city_id):
        """
        Obtém uma cidade pelo ID.
        
        Args:
            city_id (str): ID da cidade.
            
        Returns:
            City: Cidade com o ID especificado, ou None se não for encontrada.
        """
        if not self.game_state:
            return None
        
        for civ in self.game_state.civilizations:
            for city in civ.cities:
                if city.id == city_id:
                    return city
        
        return None
    
    def get_city_by_position(self, x, y):
        """
        Obtém uma cidade pela posição.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            
        Returns:
            City: Cidade na posição especificada, ou None se não for encontrada.
        """
        if not self.game_state or not self.game_state.world:
            return None
        
        tile = self.game_state.world.get_tile(x, y)
        if not tile:
            return None
        
        return tile.city
    
    def found_city(self, unit, name=None):
        """
        Funda uma nova cidade usando um colonizador.
        
        Args:
            unit: Unidade colonizadora.
            name (str): Nome da cidade (opcional).
            
        Returns:
            dict: {'success': True, 'city': City} ou {'success': False, 'reason': str}
        """
        if not unit or unit.type != 'settler':
            self.logger.error("Unidade não é um colonizador")
            return {'success': False, 'reason': 'not_a_settler'}
        
        tile = self.game_state.world.get_tile(unit.x, unit.y)
        if not tile or tile.city:
            self.logger.error("Não é possível fundar cidade neste local")
            return {'success': False, 'reason': 'invalid_tile'}
        
        if tile.terrain_type in ['water', 'mountains']:
            self.logger.error("Terreno inadequado para fundar cidade")
            return {'success': False, 'reason': 'bad_terrain'}
        
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                neighbor = self.game_state.world.get_tile(unit.x + dx, unit.y + dy)
                if neighbor and neighbor.city:
                    self.logger.error("Muito próximo de outra cidade")
                    return {'success': False, 'reason': 'too_close_to_city'}
        
        if not name:
            civ = unit.owner
            if civ:
                name = f"{civ.name} City {len(civ.cities) + 1}"
            else:
                name = f"City {unit.x}_{unit.y}"
        
        city = self.game_state.city_class(unit.x, unit.y, name)
        city.owner = unit.owner
        city.founded_turn = self.game_state.current_turn
        
        if city.owner:
            city.owner.add_city(city)
        tile.city = city
        if city.owner:
            city.owner.remove_unit(unit)
        tile.remove_unit(unit)
        
        self.logger.info(f"Cidade {name} fundada em ({unit.x}, {unit.y})")
        return {'success': True, 'city': city}
    
    def set_production(self, city, production_id):
        """
        Define o que a cidade deve produzir.
        
        Args:
            city: Cidade.
            production_id (str): ID do edifício ou unidade a ser produzido.
            
        Returns:
            bool: True se a produção foi definida com sucesso, False caso contrário.
        """
        if not city:
            return False
        
        # Verifica se é um edifício
        building_data = self.game_state.building_data.get(production_id)
        if building_data:
            # Verifica se o edifício já existe na cidade
            if production_id in city.buildings:
                self.logger.warning(f"Edifício {production_id} já existe na cidade {city.name}")
                return False
            
            # Verifica se a cidade pode construir o edifício
            if not city.can_build(production_id, self.game_state.building_data):
                self.logger.warning(f"Cidade {city.name} não pode construir {production_id}")
                return False
            
            # Define a produção
            city.producing = {
                'type': 'building',
                'id': production_id,
                'progress': 0,
                'cost': building_data.get('cost', 50)
            }
            
            self.logger.info(f"Cidade {city.name} começou a construir {production_id}")
            return True
        
        # Verifica se é uma unidade
        unit_data = self.game_state.unit_data.get(production_id)
        if unit_data:
            # Verifica se a cidade pode produzir a unidade
            # TODO: Implementar verificação de pré-requisitos para unidades
            
            # Define a produção
            city.producing = {
                'type': 'unit',
                'id': production_id,
                'progress': 0,
                'cost': unit_data.get('cost', 50)
            }
            
            self.logger.info(f"Cidade {city.name} começou a produzir {production_id}")
            return True
        
        self.logger.error(f"Produção inválida: {production_id}")
        return False
    
    def get_available_buildings(self, city):
        """
        Obtém os edifícios disponíveis para construção na cidade.
        
        Args:
            city: Cidade.
            
        Returns:
            list: Lista de IDs de edifícios disponíveis.
        """
        if not city:
            return []
        
        return city.get_available_buildings(self.game_state.building_data)
    
    def get_available_units(self, city):
        """
        Obtém as unidades disponíveis para produção na cidade.
        
        Args:
            city: Cidade.
            
        Returns:
            list: Lista de IDs de unidades disponíveis.
        """
        if not city:
            return []
        
        return city.get_available_units(self.game_state.unit_data)
    
    def get_city_info(self, city):
        """
        Obtém informações detalhadas sobre uma cidade.
        
        Args:
            city: Cidade.
            
        Returns:
            dict: Informações sobre a cidade.
        """
        if not city:
            return None
        
        # Obtém informações básicas da cidade
        info = {
            'id': city.id,
            'name': city.name,
            'x': city.x,
            'y': city.y,
            'owner': city.owner.name if city.owner else None,
            'population': city.population,
            'health': city.health,
            'food': city.food,
            'food_needed': city.food_needed,
            'production': city.production,
            'producing': city.producing,
            'buildings': city.buildings,
            'worked_tiles': [(tile.x, tile.y) for tile in city.worked_tiles],
            'founded_turn': city.founded_turn
        }
        
        # Adiciona informações sobre produção atual
        if city.producing:
            if city.producing['type'] == 'building':
                building_data = self.game_state.building_data.get(city.producing['id'])
                if building_data:
                    info['producing']['name'] = building_data.get('name', city.producing['id'])
                    info['producing']['description'] = building_data.get('description', '')
            
            elif city.producing['type'] == 'unit':
                unit_data = self.game_state.unit_data.get(city.producing['id'])
                if unit_data:
                    info['producing']['name'] = unit_data.get('name', city.producing['id'])
                    info['producing']['description'] = unit_data.get('description', '')
        
        return info
