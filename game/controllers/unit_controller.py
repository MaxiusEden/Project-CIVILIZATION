# game/controllers/unit_controller.py
import logging

class UnitController:
    """
    Controlador de unidades.
    
    Gerencia operações relacionadas a unidades, como movimento, combate e ações especiais.
    """
    
    def __init__(self, game_controller):
        """
        Inicializa o controlador de unidades.
        
        Args:
            game_controller: Controlador principal do jogo.
        """
        self.game_controller = game_controller
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def game_state(self):
        """Obtém o estado atual do jogo."""
        return self.game_controller.game_state
    
    def get_unit_by_id(self, unit_id):
        """
        Obtém uma unidade pelo ID.
        
        Args:
            unit_id (str): ID da unidade.
            
        Returns:
            Unit: Unidade com o ID especificado, ou None se não for encontrada.
        """
        if not self.game_state:
            return None
        
        for civ in self.game_state.civilizations:
            for unit in civ.units:
                if unit.id == unit_id:
                    return unit
        
        return None
    
    def get_units_at_position(self, x, y):
        """
        Obtém as unidades em uma posição.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            
        Returns:
            list: Lista de unidades na posição especificada.
        """
        if not self.game_state or not self.game_state.world:
            return []
        
        tile = self.game_state.world.get_tile(x, y)
        if not tile:
            return []
        
        return tile.units
    
    def move_unit(self, unit, target_x, target_y):
        """
        Move uma unidade para uma posição alvo.
        
        Args:
            unit: Unidade a ser movida.
            target_x (int): Coordenada X alvo.
            target_y (int): Coordenada Y alvo.
            
        Returns:
            dict: Resultado do movimento.
        """
        if not unit:
            return {'success': False, 'reason': 'no_unit'}
        
        # Verifica se a unidade pode se mover
        if unit.moves_left <= 0:
            return {'success': False, 'reason': 'no_moves_left'}
        
        if unit.has_acted:
            return {'success': False, 'reason': 'already_acted'}
        
        # Verifica se o destino é válido
        target_tile = self.game_state.world.get_tile(target_x, target_y)
        if not target_tile:
            return {'success': False, 'reason': 'invalid_destination'}
        
        # Verifica se a unidade pode mover para o tile alvo
        if not unit.can_move_to(target_tile, self.game_state.terrain_data):
            return {'success': False, 'reason': 'impassable_terrain'}
        
        # Calcula o caminho
        path = self.game_controller.world_controller.get_path(
            unit.x, unit.y, target_x, target_y, unit
        )
        
        if not path:
            return {'success': False, 'reason': 'no_path'}
        
        # Verifica se o caminho é muito longo
        if len(path) > unit.moves_left:
            # Move o máximo possível
            path = path[:unit.moves_left]
        
        # Remove a unidade do tile atual
        current_tile = self.game_state.world.get_tile(unit.x, unit.y)
        if current_tile:
            current_tile.remove_unit(unit)
        
        # Atualiza a posição da unidade
        last_pos = path[-1]
        unit.x, unit.y = last_pos
        
        # Adiciona a unidade ao novo tile
        new_tile = self.game_state.world.get_tile(unit.x, unit.y)
        if new_tile:
            new_tile.add_unit(unit)
        
        # Atualiza os movimentos restantes
        unit.moves_left -= len(path)
        
        self.logger.info(f"Unidade {unit.type} movida para ({unit.x}, {unit.y})")
        
        return {
            'success': True,
            'path': path,
            'moves_left': unit.moves_left
        }
    
    def attack(self, unit, target_x, target_y):
        """
        Realiza um ataque com uma unidade.
        
        Args:
            unit: Unidade atacante.
            target_x (int): Coordenada X do alvo.
            target_y (int): Coordenada Y do alvo.
            
        Returns:
            dict: Resultado do ataque.
        """
        if not unit:
            return {'success': False, 'reason': 'no_unit'}
        
        # Verifica se a unidade pode atacar
        if unit.has_acted:
            return {'success': False, 'reason': 'already_acted'}
        
        # Verifica se o alvo é válido
        target_tile = self.game_state.world.get_tile(target_x, target_y)
        if not target_tile:
            return {'success': False, 'reason': 'invalid_target'}
        
        # Calcula a distância
        distance = abs(unit.x - target_x) + abs(unit.y - target_y)
        
        # Verifica se o alvo está ao alcance
        if unit.ranged_strength > 0:
            if distance > unit.range:
                return {'success': False, 'reason': 'out_of_range'}
        else:
            if distance > 1:
                return {'success': False, 'reason': 'out_of_range'}
        
        # Encontra o alvo
        target = None
        
        # Verifica se há uma cidade no tile
        if target_tile.city:
            city = target_tile.city
            
            # Verifica se a cidade é inimiga
            if city.owner and unit.owner and city.owner.id != unit.owner.id:
                target = city
        
        # Se não há cidade inimiga, verifica se há unidades inimigas
        if not target and target_tile.units:
            for target_unit in target_tile.units:
                # Verifica se a unidade é inimiga
                if target_unit.owner and unit.owner and target_unit.owner.id != unit.owner.id:
                    target = target_unit
                    break
        
        if not target:
            return {'success': False, 'reason': 'no_valid_target'}
        
        # Realiza o ataque
        attack_result = unit.attack(target)
        
        # Verifica se o alvo foi destruído
        if target.health <= 0:
            if isinstance(target, type(unit)):  # É uma unidade
                # Remove a unidade do tile
                target_tile.remove_unit(target)
                
                # Remove a unidade da civilização
                if target.owner:
                    target.owner.remove_unit(target)
                
                self.logger.info(f"Unidade {target.type} destruída em ({target_x}, {target_y})")
            else:  # É uma cidade
                # Captura a cidade
                if unit.owner:
                    # Remove a cidade da civilização atual
                    if target.owner:
                        target.owner.remove_city(target)
                    
                    # Adiciona a cidade à civilização do atacante
                    target.owner = unit.owner
                    unit.owner.add_city(target)
                    
                    # Restaura parte da saúde da cidade
                    target.health = max(1, target.max_health // 2)
                    
                    self.logger.info(f"Cidade {target.name} capturada por {unit.owner.name}")
        
        return attack_result
    
    def fortify(self, unit):
        """
        Fortifica uma unidade.
        
        Args:
            unit: Unidade a ser fortificada.
            
        Returns:
            bool: True se a unidade foi fortificada com sucesso, False caso contrário.
        """
        if not unit:
            return False
        
        # Verifica se a unidade pode se fortificar
        if unit.has_acted:
            return False
        
        # Fortifica a unidade
        unit.is_fortified = True
        unit.has_acted = True
        unit.moves_left = 0
        
        self.logger.info(f"Unidade {unit.type} fortificada em ({unit.x}, {unit.y})")
        return True
    
    def sleep(self, unit):
        """
        Coloca uma unidade para dormir.
        
        Args:
            unit: Unidade a ser colocada para dormir.
            
        Returns:
            bool: True se a unidade foi colocada para dormir com sucesso, False caso contrário.
        """
        if not unit:
            return False
        
        # Coloca a unidade para dormir
        unit.is_sleeping = True
        unit.has_acted = True
        
        self.logger.info(f"Unidade {unit.type} dormindo em ({unit.x}, {unit.y})")
        return True
    
    def wake(self, unit):
        """
        Acorda uma unidade.
        
        Args:
            unit: Unidade a ser acordada.
            
        Returns:
            bool: True se a unidade foi acordada com sucesso, False caso contrário.
        """
        if not unit:
            return False
        
        # Acorda a unidade
        unit.is_sleeping = False
        
        self.logger.info(f"Unidade {unit.type} acordada em ({unit.x}, {unit.y})")
        return True
    
    def get_unit_info(self, unit):
        """
        Obtém informações detalhadas sobre uma unidade.
        
        Args:
            unit: Unidade.
            
        Returns:
            dict: Informações sobre a unidade.
        """
        if not unit:
            return None
        
        # Obtém informações básicas da unidade
        info = {
            'id': unit.id,
            'type': unit.type,
            'x': unit.x,
            'y': unit.y,
            'owner': unit.owner.name if unit.owner else None,
            'health': unit.health,
            'strength': unit.strength,
            'ranged_strength': unit.ranged_strength,
            'range': unit.range,
            'movement': unit.movement,
            'moves_left': unit.moves_left,
            'has_acted': unit.has_acted,
            'is_fortified': unit.is_fortified,
            'is_sleeping': unit.is_sleeping,
            'experience': unit.experience,
            'promotions': unit.promotions
        }
        
        # Adiciona informações do tipo de unidade
        unit_data = self.game_state.unit_data.get(unit.type, {})
        info.update({
            'name': unit_data.get('name', unit.type),
            'description': unit_data.get('description', ''),
            'cost': unit_data.get('cost', 0),
            'maintenance': unit_data.get('maintenance', 0)
        })
        
        return info
