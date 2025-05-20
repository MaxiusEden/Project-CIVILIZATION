from game.building import Building

class City:
    def __init__(self, name, civilization, position):
        self.name = name
        self.civilization = civilization
        self.position = position
        self.population = 1
        self.buildings = []
        self.food = 0
        self.food_per_turn = 2
        self.production = 0
        self.production_per_turn = 3
        self.gold_per_turn = 5
        self.science_per_turn = 2
        self.culture_per_turn = 1
        self.housing = 5
        self.defense = 10
        self.has_river = False  # Determinar com base na geração do mapa
        self.building_queue = []
        self.unit_queue = []
        self.worked_tiles = []
        self.health = 100
        
    def add_building(self, building):
        """Adiciona um edifício à cidade."""
        self.buildings.append(building)
        building.apply_effects(self)
    
    def queue_building(self, building_type):
        """Adiciona um edifício à fila de construção."""
        building = Building(building_type)
        if building.can_be_built(self, self.civilization.technologies):
            self.building_queue.append(building)
            return True
        return False
    
    def queue_unit(self, unit_type):
        """Adiciona uma unidade à fila de produção."""
        # Verificar se a unidade pode ser produzida (tecnologias, recursos, etc.)
        # Por enquanto, simplificamos e permitimos qualquer unidade
        self.unit_queue.append(unit_type)
        return True
    
    def process_turn(self):
        """Processa um turno para a cidade."""
        # Crescimento populacional
        self.food += self.food_per_turn
        food_needed = self.population * 10
        if self.food >= food_needed and self.population < self.housing:
            self.food -= food_needed
            self.population += 1
            self.update_yields()
        
        # Produção
        self.production += self.production_per_turn
        
        # Processa fila de construção
        if self.building_queue and self.production >= self.building_queue[0].cost:
            building = self.building_queue.pop(0)
            self.production -= building.cost
            self.add_building(building)
        elif self.unit_queue and self.production >= self._get_unit_cost(self.unit_queue[0]):
            unit_type = self.unit_queue.pop(0)
            self.production -= self._get_unit_cost(unit_type)
            self._create_unit(unit_type)
    
    def _get_unit_cost(self, unit_type):
        """Retorna o custo de produção de uma unidade."""
        # Idealmente, isso seria carregado de um arquivo de dados
        costs = {
            "settler": 80,
            "warrior": 40,
            "archer": 60,
            "builder": 50,
            "spearman": 65,
            "horseman": 80
        }
        return costs.get(unit_type, 50)
    
    def _create_unit(self, unit_type):
        """Cria uma nova unidade do tipo especificado."""
        # Encontra uma posição válida próxima à cidade
        x, y = self.position
        positions = [(x, y), (x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        
        for pos in positions:
            px, py = pos
            world = self.civilization.world
            
            # Verifica se a posição é válida e não tem outra unidade
            if (0 <= px < world.width and 0 <= py < world.height and 
                world.get_tile(px, py) != '~' and
                not any(u.position == pos for u in world.units)):
                
                self.civilization.create_unit(unit_type, pos)
                break
    
    def update_yields(self):
        """Atualiza os rendimentos da cidade com base na população e edifícios."""
        # Base yields
        self.food_per_turn = 2 + self.population
        self.production_per_turn = 3 + (self.population // 2)
        self.gold_per_turn = 5 + self.population
        self.science_per_turn = 2 + (self.population // 2)
        self.culture_per_turn = 1 + (self.population // 3)
        
        # Adiciona efeitos dos edifícios
        for building in self.buildings:
            building.apply_effects(self)
    
    def take_damage(self, damage):
        """A cidade recebe dano de um ataque."""
        # Reduz o dano com base na defesa da cidade
        reduced_damage = damage * (100 / (100 + self.defense))
        self.health -= reduced_damage
        
        if self.health <= 0:
            self.health = 0
            # A cidade pode ser capturada quando sua saúde chega a 0
    
        def capture(self, new_civilization):
            """A cidade é capturada por outra civilização."""
            if self.health <= 0:
                # Remove a cidade da civilização atual
                if self in self.civilization.cities:
                    self.civilization.cities.remove(self)
                
                # Adiciona a cidade à nova civilização
                self.civilization = new_civilization
                new_civilization.cities.append(self)
                
                # Redefine alguns valores da cidade
                self.health = 50
                self.building_queue = []
                self.unit_queue = []
                
                # Perde alguns edifícios durante a captura
                self.buildings = [b for b in self.buildings if not self._is_destroyed_on_capture()]
                
                # Atualiza os rendimentos
                self.update_yields()
                
                return True
            return False
    
    def _is_destroyed_on_capture(self):
        """Determina aleatoriamente se um edifício é destruído durante a captura."""
        import random
        return random.random() < 0.3  # 30% de chance de destruição
    
    def get_status_string(self):
        """Retorna uma string com informações sobre o status da cidade."""
        status = f"{self.name} (Pop: {self.population})\n"
        status += f"Saúde: {self.health}/100\n"
        status += f"Comida: {self.food}/{self.population * 10} (+{self.food_per_turn}/turno)\n"
        status += f"Produção: {self.production} (+{self.production_per_turn}/turno)\n"
        status += f"Ouro: +{self.gold_per_turn}/turno\n"
        status += f"Ciência: +{self.science_per_turn}/turno\n"
        status += f"Cultura: +{self.culture_per_turn}/turno\n"
        
        if self.building_queue:
            status += f"Construindo: {self.building_queue[0].name} ({self.production}/{self.building_queue[0].cost})\n"
        elif self.unit_queue:
            status += f"Produzindo: {self.unit_queue[0]} ({self.production}/{self._get_unit_cost(self.unit_queue[0])})\n"
        else:
            status += "Nada em produção\n"
            
        return status

