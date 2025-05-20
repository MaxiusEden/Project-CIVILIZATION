import json
import os

class Unit:
    def __init__(self, unit_type, civilization, position):
        self.unit_type = unit_type
        self.civilization = civilization
        self.position = position
        self.health = 100
        self.moves_left = 0
        self.abilities = []
        self.experience = 0
        self.level = 1
        self.symbol = self._get_symbol()
        
        # Carrega dados da unidade
        self._load_unit_data()
        
    def _load_unit_data(self):
        """Carrega dados da unidade a partir do arquivo JSON."""
        try:
            with open('data/units.json', 'r') as f:
                units_data = json.load(f)
                
            if self.unit_type in units_data:
                unit_data = units_data[self.unit_type]
                self.name = unit_data.get('name', self.unit_type.capitalize())
                self.cost = unit_data.get('cost', 50)
                self.maintenance = unit_data.get('maintenance', 1)
                self.max_moves = unit_data.get('movement', 2)
                self.moves_left = self.max_moves
                self.combat_strength = unit_data.get('combat_strength', 0)
                self.ranged_strength = unit_data.get('ranged_strength', 0)
                self.range = unit_data.get('range', 0)
                self.abilities = unit_data.get('abilities', [])
                self.charges = unit_data.get('charges', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            # Valores padrão se o arquivo não for encontrado ou for inválido
            self.name = self.unit_type.capitalize()
            self.cost = 50
            self.maintenance = 1
            self.max_moves = 2
            self.moves_left = self.max_moves
            self.combat_strength = 10
            self.ranged_strength = 0
            self.range = 0
            self.abilities = []
            self.charges = 0
        
    def _get_symbol(self):
        """Retorna o símbolo ASCII para representar a unidade."""
        symbols = {
            "settler": 'S',
            "warrior": 'W',
            "archer": 'A',
            "builder": 'B',
            "spearman": 'P',
            "horseman": 'H',
            "swordsman": 'X',
            "catapult": 'C'
        }
        return symbols.get(self.unit_type, '?')
    
    def move(self, dx, dy):
        """Move a unidade na direção especificada."""
        if self.moves_left <= 0:
            return False
            
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        
        # Verifica se a nova posição é válida
        world = self.civilization.world
        if not (0 <= new_x < world.width and 0 <= new_y < world.height):
            return False
            
        # Verifica se o terreno é passável
        terrain = world.get_tile(new_x, new_y)
        if terrain == '~':  # Água (não passável para unidades terrestres)
            if 'embark' not in self.abilities:
                return False
        
        # Move a unidade
        self.position = (new_x, new_y)
        self.moves_left -= 1
        return True
    
    def attack(self, target):
        """Ataca outra unidade."""
        if self.moves_left <= 0:
            return False
            
        # Verifica se o alvo está ao alcance
        tx, ty = target.position
        x, y = self.position
        distance = max(abs(tx - x), abs(ty - y))
        
        if self.ranged_strength > 0:
            # Ataque à distância
            if distance <= self.range:
                damage = self.ranged_strength * (self.health / 100)
                target.take_damage(damage)
                self.moves_left = 0
                return True
        else:
            # Ataque corpo a corpo
            if distance <= 1:
                damage = self.combat_strength * (self.health / 100)
                target.take_damage(damage)
                # Contra-ataque
                if target.health > 0 and target.combat_strength > 0:
                    counter_damage = target.combat_strength * (target.health / 100) * 0.5
                    self.take_damage(counter_damage)
                self.moves_left = 0
                return True
                
        return False
    
    def take_damage(self, damage):
        """Recebe dano de um ataque."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.destroy()
    
    def destroy(self):
        """Remove a unidade do jogo."""
        if self in self.civilization.units:
            self.civilization.units.remove(self)
        if self.civilization.world and self in self.civilization.world.units:
            self.civilization.world.units.remove(self)
    
    def found_city(self):
        """Funda uma nova cidade na posição atual (apenas para colonizadores)."""
        if 'found_city' in self.abilities and self.moves_left > 0:
            x, y = self.position
            city_name = f"{self.civilization.name} Cidade {len(self.civilization.cities) + 1}"
            self.civilization.found_city(city_name, self.position)
            self.destroy()  # O colonizador é consumido
            return True
        return False
    
    def build_improvement(self, improvement_type):
        """Constrói uma melhoria no terreno atual (apenas para construtores)."""
        if 'build_improvement' in self.abilities and self.moves_left > 0 and self.charges > 0:
            x, y = self.position
            # Implementar lógica para adicionar a melhoria ao terreno
            # world.add_improvement(x, y, improvement_type)
            self.charges -= 1
            self.moves_left = 0
            
            # Se não tiver mais cargas, destruir o construtor
            if self.charges <= 0:
                self.destroy()
                
            return True
        return False
    
    def process_turn(self):
        """Processa um novo turno para a unidade."""
        self.moves_left = self.max_moves
