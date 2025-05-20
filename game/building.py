import json

class Building:
    def __init__(self, building_type):
        self.building_type = building_type
        self.completed = False
        
        # Carrega dados do edifício
        self._load_building_data()
        
    def _load_building_data(self):
        """Carrega dados do edifício a partir do arquivo JSON."""
        try:
            with open('data/buildings.json', 'r') as f:
                buildings_data = json.load(f)
                
            if self.building_type in buildings_data:
                building_data = buildings_data[self.building_type]
                self.name = building_data.get('name', self.building_type.capitalize())
                self.cost = building_data.get('cost', 100)
                self.maintenance = building_data.get('maintenance', 1)
                self.required_tech = building_data.get('requires_tech', None)
                self.effects = building_data.get('effects', {})
                self.description = building_data.get('description', '')
                self.requires_river = building_data.get('requires_river', False)
        except (FileNotFoundError, json.JSONDecodeError):
            # Valores padrão se o arquivo não for encontrado ou for inválido
            self.name = self.building_type.capitalize()
            self.cost = 100
            self.maintenance = 1
            self.required_tech = None
            self.effects = {}
            self.description = ''
            self.requires_river = False
    
    def can_be_built(self, city, technologies):
        """Verifica se o edifício pode ser construído na cidade."""
        # Verifica se a tecnologia necessária foi pesquisada
        if self.required_tech and self.required_tech not in [tech.name for tech in technologies]:
            return False
            
        # Verifica se a cidade já tem este edifício
        if any(b.building_type == self.building_type for b in city.buildings):
            return False
            
        # Verifica requisitos especiais
        if self.requires_river and not city.has_river:
            return False
            
        return True
    
    def apply_effects(self, city):
        """Aplica os efeitos do edifício à cidade."""
        if 'food' in self.effects:
            city.food += self.effects['food']
        if 'production' in self.effects:
            city.production_per_turn += self.effects['production']
        if 'gold' in self.effects:
            city.gold_per_turn += self.effects['gold']
        if 'science' in self.effects:
            city.science_per_turn += self.effects['science']
        if 'culture' in self.effects:
            city.culture_per_turn += self.effects['culture']
        if 'housing' in self.effects:
            city.housing += self.effects['housing']
        if 'defense' in self.effects:
            city.defense += self.effects['defense']
