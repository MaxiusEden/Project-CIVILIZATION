# game/models/unit.py
import logging
import uuid

class Unit:
    """
    Representa uma unidade no jogo.
    
    Uma unidade pertence a uma civilização, ocupa um tile no mapa,
    e pode se mover, atacar e realizar ações especiais.
    """
    
    def __init__(self, x, y, unit_type):
        """
        Inicializa uma nova unidade.
        
        Args:
            x (int): Coordenada X da unidade.
            y (int): Coordenada Y da unidade.
            unit_type (str): Tipo da unidade.
        """
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.type = unit_type
        self.owner = None  # Referência à civilização proprietária
        
        # Atributos da unidade
        self.health = 100
        self.movement = 0
        self.max_movement = 0
        self.strength = 0
        self.ranged_strength = 0
        self.range = 0
        
        # Estado da unidade
        self.moves_left = 0
        self.has_acted = False
        self.is_fortified = False
        self.is_sleeping = False
        
        # Experiência e promoções
        self.experience = 0
        self.promotions = []
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{unit_type}")
    
    def initialize_from_data(self, unit_data):
        """
        Inicializa os atributos da unidade a partir dos dados do tipo de unidade.
        
        Args:
            unit_data (dict): Dados do tipo de unidade.
        """
        unit_info = unit_data.get(self.type, {})
        
        self.max_movement = unit_info.get('movement', 2)
        self.moves_left = self.max_movement
        self.strength = unit_info.get('strength', 0)
        self.ranged_strength = unit_info.get('ranged_strength', 0)
        self.range = unit_info.get('range', 0)
    
    def reset_turn(self):
        """Reseta o estado da unidade para o início de um novo turno."""
        self.moves_left = self.max_movement
        self.has_acted = False
        
        # Cura unidades fortificadas
        if self.is_fortified and self.health < 100:
            self.health = min(100, self.health + 10)
    
    def can_move(self):
        """
        Verifica se a unidade pode se mover.
        
        Returns:
            bool: True se a unidade pode se mover, False caso contrário.
        """
        return self.moves_left > 0 and not self.is_fortified and not self.is_sleeping
    
    def can_act(self):
        """
        Verifica se a unidade pode realizar ações.
        
        Returns:
            bool: True se a unidade pode realizar ações, False caso contrário.
        """
        return not self.has_acted and not self.is_sleeping
    
    def can_move_to(self, tile, terrain_data):
        """
        Verifica se a unidade pode se mover para um tile.
        
        Args:
            tile: Tile de destino.
            terrain_data (dict): Dados de terrenos do jogo.
            
        Returns:
            bool: True se a unidade pode se mover para o tile, False caso contrário.
        """
        # Verifica se a unidade pode se mover
        if not self.can_move():
            return False
        
        # Obtém o custo de movimento do terreno
        terrain_info = terrain_data.get(tile.terrain_type, {})
        movement_cost = terrain_info.get('movement_cost', 1)
        
        # Verifica se o terreno é intransponível
        if movement_cost >= 999:
            # TODO: Implementar unidades navais e aéreas
            return False
        
        # Verifica se há unidades inimigas no tile
        for unit in tile.units:
            if unit.owner != self.owner:
                return False
        
        # Verifica se há uma cidade inimiga no tile
        if tile.city and tile.city.owner != self.owner:
            return False
        
        return True
    
    def move_to(self, x, y):
        """
        Move a unidade para as coordenadas especificadas.
        
        Args:
            x (int): Coordenada X de destino.
            y (int): Coordenada Y de destino.
            
        Returns:
            bool: True se o movimento foi bem-sucedido, False caso contrário.
        """
        # Verifica se as coordenadas são diferentes
        if x == self.x and y == self.y:
            return False
        
        # Calcula a distância Manhattan
        distance = abs(x - self.x) + abs(y - self.y)
        
        # Verifica se a distância é válida (movimento de 1 tile por vez)
        if distance > 1:
            return False
        
        # Atualiza as coordenadas
        old_x, old_y = self.x, self.y
        self.x, self.y = x, y
        
        # Consome pontos de movimento
        self.moves_left -= 1
        
        self.logger.debug(f"Moveu de ({old_x}, {old_y}) para ({x}, {y})")
        return True
    
    def attack(self, target):
        """
        Ataca uma unidade ou cidade alvo.
        
        Args:
            target: Unidade ou cidade alvo.
            
        Returns:
            dict: Resultado do ataque.
        """
        # Verifica se a unidade pode atacar
        if not self.can_act():
            return {'success': False, 'reason': 'cannot_act'}
        
        # Verifica se o alvo está ao alcance
        target_type = target.__class__.__name__
        distance = abs(target.x - self.x) + abs(target.y - self.y)
        
        # Ataque corpo a corpo
        if self.ranged_strength == 0 and distance > 1:
            return {'success': False, 'reason': 'out_of_range'}
        
        # Ataque à distância
        if self.ranged_strength > 0 and distance > self.range:
            return {'success': False, 'reason': 'out_of_range'}
        
        # Realiza o ataque
        damage = self._calculate_damage(target)
        
        # Aplica o dano
        if target_type == 'Unit':
            target.health -= damage
            
            # Verifica se a unidade foi destruída
            if target.health <= 0:
                # TODO: Implementar destruição de unidades
                pass
            
            # Contra-ataque (apenas para ataques corpo a corpo)
            counter_damage = 0
            if self.ranged_strength == 0 and distance == 1:
                counter_damage = target._calculate_damage(self)
                self.health -= counter_damage
                
                # Verifica se esta unidade foi destruída
                if self.health <= 0:
                    # TODO: Implementar destruição de unidades
                    pass
        
        elif target_type == 'City':
            target.health -= damage
            
            # Verifica se a cidade foi capturada
            if target.health <= 0:
                # TODO: Implementar captura de cidades
                pass
        
        # Marca a unidade como tendo agido
        self.has_acted = True
        self.moves_left = 0
        
        return {
            'success': True,
            'damage': damage,
            'counter_damage': counter_damage if 'counter_damage' in locals() else 0
        }
    
    def _calculate_damage(self, target):
        """
        Calcula o dano causado a um alvo.
        
        Args:
            target: Unidade ou cidade alvo.
            
        Returns:
            int: Dano calculado.
        """
        # Força base de ataque
        attack_strength = self.ranged_strength if self.ranged_strength > 0 else self.strength
        
        # Força de defesa do alvo
        target_type = target.__class__.__name__
        if target_type == 'Unit':
            defense_strength = target.strength
        elif target_type == 'City':
            # Usamos um método mais genérico para obter a defesa da cidade
            defense_strength = getattr(target, 'defense_strength', 10)
        else:
            defense_strength = 1
        
        # Fórmula básica de dano
        damage_ratio = attack_strength / max(1, defense_strength)
        base_damage = 30 * damage_ratio
        
        # Aplica modificadores
        # TODO: Implementar modificadores de terreno, promoções, etc.
        
        # Limita o dano
        damage = max(1, min(99, int(base_damage)))
        
        return damage


    
    def fortify(self):
        """
        Fortifica a unidade, aumentando sua defesa mas impedindo movimento.
        
        Returns:
            bool: True se a fortificação foi bem-sucedida, False caso contrário.
        """
        if not self.can_act():
            return False
        
        self.is_fortified = True
        self.has_acted = True
        self.moves_left = 0
        
        self.logger.debug(f"Fortificou em ({self.x}, {self.y})")
        return True
    
    def sleep(self):
        """
        Coloca a unidade para dormir até ser acordada manualmente.
        
        Returns:
            bool: True se a ação foi bem-sucedida, False caso contrário.
        """
        if not self.can_act():
            return False
        
        self.is_sleeping = True
        
        self.logger.debug(f"Dormindo em ({self.x}, {self.y})")
        return True
    
    def wake_up(self):
        """Acorda a unidade."""
        self.is_sleeping = False
        self.is_fortified = False
        
        self.logger.debug(f"Acordou em ({self.x}, {self.y})")
    
    def to_dict(self):
        """
        Converte a unidade para um dicionário para serialização.
        
        Returns:
            dict: Representação da unidade como dicionário.
        """
        data = super().to_dict()
        data.update({
            'x': self.x,
            'y': self.y,
            'type': self.type,
            'owner': self.owner.id if self.owner else None,
            'health': self.health,
            'movement': self.movement,
            'max_movement': self.max_movement,
            'strength': self.strength,
            'ranged_strength': self.ranged_strength,
            'range': self.range,
            'moves_left': self.moves_left,
            'has_acted': self.has_acted,
            'is_fortified': self.is_fortified,
            'is_sleeping': self.is_sleeping,
            'experience': self.experience,
            'promotions': self.promotions.copy()
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria uma instância da unidade a partir de um dicionário.
        
        Args:
            data (dict): Dicionário contendo os dados da unidade.
            
        Returns:
            Unit: Nova instância da unidade.
        """
        unit = super().from_dict(data)
        unit.x = data.get('x', 0)
        unit.y = data.get('y', 0)
        unit.type = data.get('type', 'warrior')
        
        unit.health = data.get('health', 100)
        unit.movement = data.get('movement', 0)
        unit.max_movement = data.get('max_movement', 0)
        unit.strength = data.get('strength', 0)
        unit.ranged_strength = data.get('ranged_strength', 0)
        unit.range = data.get('range', 0)
        
        unit.moves_left = data.get('moves_left', 0)
        unit.has_acted = data.get('has_acted', False)
        unit.is_fortified = data.get('is_fortified', False)
        unit.is_sleeping = data.get('is_sleeping', False)
        
        unit.experience = data.get('experience', 0)
        unit.promotions = data.get('promotions', [])
        
        # Referências a outros objetos serão resolvidas posteriormente
        unit._owner_id = data.get('owner')
        
        return unit
