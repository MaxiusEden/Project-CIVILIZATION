"""
Modelo para edifícios no jogo.
"""

class Building:
    """
    Representa um edifício em uma cidade.
    """
    
    def __init__(self, building_id, data):
        """
        Inicializa um edifício.
        
        Args:
            building_id (str): Identificador único do edifício.
            data (dict): Dados do edifício.
        """
        self.id = building_id
        self.name = data.get('name', building_id)
        self.cost = data.get('cost', 0)
        self.maintenance = data.get('maintenance', 0)
        self.description = data.get('description', '')
        
        # Efeitos do edifício
        self.effects = data.get('effects', {})
        
        # Requisitos
        self.requires_tech = data.get('requires_tech', None)
        self.requires_building = data.get('requires_building', None)
        
        # Flags especiais
        self.is_wonder = data.get('is_wonder', False)
        self.is_national = data.get('is_national', False)
        
    def get_effect(self, effect_type):
        """
        Retorna o valor de um efeito específico.
        
        Args:
            effect_type (str): Tipo de efeito (food, production, gold, etc).
            
        Returns:
            int/float: Valor do efeito, ou 0 se não existir.
        """
        return self.effects.get(effect_type, 0)
    
    def to_dict(self):
        """
        Converte o edifício para um dicionário.
        
        Returns:
            dict: Representação do edifício como dicionário.
        """
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'maintenance': self.maintenance,
            'effects': self.effects,
            'requires_tech': self.requires_tech,
            'requires_building': self.requires_building,
            'is_wonder': self.is_wonder,
            'is_national': self.is_national
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria um edifício a partir de um dicionário.
        
        Args:
            data (dict): Dicionário com os dados do edifício.
            
        Returns:
            Building: Nova instância de Building.
        """
        building_id = data.pop('id')
        return cls(building_id, data)
