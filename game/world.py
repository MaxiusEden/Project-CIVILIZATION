import random

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = self._generate_map()
        self.civilizations = []
        self.cities = []
        self.units = []
        
    def _generate_map(self):
        """Gera um mapa simples com terrenos variados."""
        terrain_types = ['.', '~', '^', '#', '*']  # planície, água, montanha, floresta, recurso
        weights = [0.6, 0.2, 0.1, 0.08, 0.02]  # probabilidades de cada tipo
        
        world_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                terrain = random.choices(terrain_types, weights=weights)[0]
                row.append(terrain)
            world_map.append(row)
            
        return world_map
    
    def add_civilization(self, civilization):
        """Adiciona uma civilização ao mundo."""
        self.civilizations.append(civilization)
        civilization.world = self
    
    def get_tile(self, x, y):
        """Retorna o tipo de terreno em uma coordenada específica."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map[y][x]
        return None
    
    def set_tile(self, x, y, tile_type):
        """Modifica o terreno em uma coordenada específica."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map[y][x] = tile_type
    
    def next_turn(self):
        """Processa o próximo turno para todas as entidades."""
        # Atualiza todas as civilizações
        for civ in self.civilizations:
            civ.process_turn()
        
        # Atualiza todas as cidades
        for city in self.cities:
            city.process_turn()
        
        # Atualiza todas as unidades
        for unit in self.units:
            unit.process_turn()
